import telebot
import time
import re
from telebot import TeleBot, types
from telebot.types import Message
from screenshots2songs import sign_in_vk_1, sign_in_vk_2

token = 'TOKEN'
permitted_logins = ['LOGIN']
STATE_ONE = 'ввод логина'
STATE_TWO = 'проверка логина'
STATE_THREE = 'авторизация вк 1'
STATE_FOUR = 'авторизация вк 2'
states = {}
pattern = r'^\d{6}$'

bot = telebot.TeleBot(token)


def set_state(user_id: int, state: str):
    states[user_id] = state


def get_state(user_id: int) -> str:
    return states.get(user_id)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Бот создан для личного пользования')
    time.sleep(1)
    set_state(message.chat.id, STATE_ONE)
    handle_state_one(message)


def handle_state_one(message: Message):
    bot.send_message(message.chat.id, 'Введите свой логин')
    time.sleep(1)
    set_state(message.chat.id, STATE_TWO)


def handle_state_two(message: Message):
    login = message.text
    if login in permitted_logins:
        bot.send_message(message.chat.id, f'Добро пожаловать {login}!')
        set_state(message.chat.id, STATE_THREE)
        handle_state_three(message)
    else:
        bot.send_message(message.chat.id, 'К сожалению, у вас нет доступа')
        set_state(message.chat.id, STATE_TWO)
        handle_state_one(message)


def handle_state_three(message: Message):
    bot.send_message(message.chat.id, 'Захожу в ВК..')
    driver = sign_in_vk_1()
    bot.send_message(message.chat.id, 'Для продолжения введи код от ВК')
    set_state(message.chat.id, STATE_FOUR)
    return driver
    # bot.send_message(message.chat.id, 'Введите код от ВК')
    # code = message.text
    # bot.send_message(message.chat.id, f'Все ок, вот твой код {code}')
    # set_state(message.chat.id, STATE_ONE)


def handle_state_four(message, driver):
    bot.send_message(message.chat.id, f'Перешел в состояние 4')
    # if driver:
    #     code = message.text
    #     sign_in_vk_2(driver, code)
    #     bot.send_message(message.chat.id, f'Отлично!')
    # else:
    #     bot.send_message(message.chat.id, f'При открытии ВК что-то пошло не так')


@bot.message_handler(regexp=pattern)
@bot.message_handler()
def handle_code_message(message: Message):
    code = message.text
    sign_in_vk_2(driver, code)
    bot.send_message(message.chat.id, f'Отлично!')


@bot.message_handler(func=lambda message: True)
def message_handler(message: Message):
    driver = None
    state = get_state(message.chat.id)
    if state == STATE_ONE:
        handle_state_one(message)
    if state == STATE_TWO:
        handle_state_two(message)
    if state == STATE_THREE:
        driver = handle_state_three(message)
    if state == STATE_FOUR:
        handle_state_four(message, driver)


# @bot.message_handler(content_types=['photo'])
# def handle_screenshot():
#     pass
#
# @bot.message_handler(content_types=['text'])
# def handle_message(message):
#     password = message.text
#     # может сделать проверку по никнейму
#     if password == 'я есть люмос 149':
#         bot.send_message(message.chat.id, "Пароль верный!")
#         bot.send_message(message.chat.id, "Пришлите скриншот")
#         passed = True
#         handle_screenshot(passed)
#     else:
#         bot.send_message(message.chat.id, "Пароль неправильный, попробуйте еще раз.")

# @bot.message_handler(commands=['help'])
# def help(msg):
#     help_msg =  'Бот создан для личного пользования. Введите пароль для продолжения'
#     bot.send_message(msg.chat.id, help_msg)
#
# @bot.message_handler(commands=['start'])
# def staert(msg):
#     bot.send_message(msg.chat.id, '')
#     password = msg.text
#     if password == correct_password:
#         bot.send_message(msg.chat.id, "Пароль верный!")
#     else:
#         bot.send_message(msg.chat.id, "Пароль неправильный, попробуйте еще раз.")

# отправка запросов серверу ТГ
bot.polling(none_stop=True)
