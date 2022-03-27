import datetime
import telebot
from telebot import types
from datetime import date
from datetime import datetime

HELP = 'Что я пока умею:\n' \
       '- Для удобства команды вводятся кнопками. Ручками вводится только дата и задание\n' \
       '- Добавлять задания в список дел по категориям\n' \
       '- Выводить список дел сообщением\n' \
       '- Оnслеживаю валидности введенной даты (задачу на прошлое не добавишь)\n' \
       '- Отслеживаю корректность введенного задания (не менее 3 символов)\n' \
       '\nИЗ моих МИНУСОВ:\n' \
       '- Даные храняться в списке. Хотелось бы в файле или БД\n' \
       '\nБудем избавляться от минусов по мере взросления.\n' \
       'Внизу появилось основное меню.\n' \
       'Погнали тестить меня. Да прибудет с Вами Python'

chk_date = datetime(2099, 10, 22)


task_list = {}
category = ''

bot = telebot.TeleBot('')


def add_task(task_date, task):
    if task_date in task_list:
        task_list[task_date].append(task)
    else:
        task_list[task_date] = [task]


def check_str(chat_id, input_str):  # проверка корректности ввода даты и задачи
    err_date_msg = "Эээээй. Что-то не так с датой. Формат ввода даты <b>DD.MM.YYYY</b> Попробуй еще раз"
    if input_str.find('-') == -1:
        bot.send_message(chat_id, "Может тире забыл между датой и заданием. Попробуй еще раз")
    else:
        my_str = input_str.split('-')
        if len(my_str) < 2:
            bot.send_message(chat_id, "Эээээй. Что-то не так. Формат ввода <b>DD.MM.YYYY-task</b>.\n"
                                      "Попробуй еще раз", parse_mode='html')
        else:
            if len(my_str[1]) < 3:
                bot.send_message(chat_id, "Эээээй. Что-то не так. Задание слишком короткое. Попробуй еще раз")
            else:
                if len(my_str[0]) < 10:
                    bot.send_message(chat_id, err_date_msg, parse_mode='html')
                else:
                    input_date = my_str[0].split('.')
                    if len(input_date[0]) != 2 or len(input_date[1]) != 2 or len(input_date[2]) != 4:
                        bot.send_message(chat_id, err_date_msg, parse_mode='html')
                    else:
                        global chk_date
                        try:
                            chk_date = datetime.strptime(my_str[0], "%d.%m.%Y")
                            if chk_date.date() < date.today():
                                today = date.today()
                                bot.send_message(chat_id, f'Сегодня <b>{today.strftime("%d.%m.%Y")} </b>\n'
                                                          f'Ты ввел <b>{chk_date.strftime("%d.%m.%Y")}</b>\n'
                                                          f'Ничего не смущает. Или у тебя есть машина времени????\n'
                                                          f'Давай попробуй еще раз', parse_mode='html')
                            else:
                                global category
                                if category != '':
                                    task_str = my_str[1] + ': ' + category
                                    add_task(my_str[0], task_str)
                                    bot.send_message(chat_id, f"Задача <b>{my_str[1]}</b> добвлена на <b>{my_str[0]}</b>",
                                                     parse_mode='html')
                                    category = ''
                                else:
                                    bot.send_message(chat_id, 'Вы не выбрали категорию!!!\n'
                                                              'нажмите Add Task')
                        except ValueError:
                            bot.send_message(chat_id, 'Такой даты не существует')


def show_tasks(chat_id):
    my_message = '<u>Список запланированных дел:</u>\n'
    for key in task_list:
        my_message += f'\n<b>{key}</b>'
        for value in task_list[key]:
            my_message += f'\n\t\ -- <b>{value}</b>'
    bot.send_message(chat_id, my_message, parse_mode='html')


@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.ReplyKeyboardMarkup(True)
    keyboard.row('Add Task', 'Show Tasks')
    bot.send_message(message.chat.id, 'Привет. {0.first_name}!\nЯ - <b>{1.first_name}</b>,'
                                      'ToDo бот V2.0.'.format(message.from_user, bot.get_me()),
                     reply_markup=keyboard, parse_mode='html')
    bot.send_message(message.chat.id, HELP)


@bot.message_handler(content_types=['text'])
def text_handler(message):
    if message.text == 'Add Task':
        inline_kb = types.InlineKeyboardMarkup(row_width=3)
        inline_btn1 = types.InlineKeyboardButton('Личная жизнь', callback_data='own')
        inline_btn2 = types.InlineKeyboardButton('Домашние дела', callback_data='home')
        inline_btn3 = types.InlineKeyboardButton('Работа', callback_data='work')
        inline_kb.add(inline_btn1, inline_btn2, inline_btn3)
        bot.send_message(message.chat.id, 'Выберите категорию:', reply_markup=inline_kb)
    elif message.text == 'Show Tasks':
        show_tasks(message.chat.id)
    else:
        check_str(message.chat.id, message.text)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    global category
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
    today = date.today()
    if call.data == 'own':
        category = '@Личная жизнь'
        bot.send_message(call.message.chat.id, f'Сегодня <b>{today.strftime("%d.%m.%Y")} </b>\n'
                                               f'Введите задачу(формат <b>DD.MM.YYYY-task</b>):',
                         parse_mode='html')
    if call.data == 'home':
        category = '@Домашние дела'
        bot.send_message(call.message.chat.id, f'Сегодня <b>{today.strftime("%d.%m.%Y")} </b>\n'
                                               f'Введите задачу(формат <b>DD.MM.YYYY-task</b>):',
                         parse_mode='html')
    if call.data == 'work':
        category = '@Работа'
        bot.send_message(call.message.chat.id, f'Сегодня <b>{today.strftime("%d.%m.%Y")} </b>\n'
                                               f'Введите задачу(формат <b>DD.MM.YYYY-task</b>):',
                         parse_mode='html')


if __name__ == '__main__':
    bot.polling(none_stop=True)
