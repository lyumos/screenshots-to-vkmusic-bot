import telebot
import os
import requests
from telegram import Update
from telegram.ext import CallbackContext
from telebot import TeleBot, types
from telebot.types import Message
from screenshots2songs import sign_in_vk_1, sign_in_vk_2, recognize_text, get_link, crop_img, define_img_type
from my_private_data import bot_token, imgs_path, users_info
import emoji

bot = telebot.TeleBot(bot_token)


@bot.message_handler(commands=['start'])
def start(message: Message):
    user = message.json['from']['username']
    if user in users_info.keys():
        bot.send_message(message.chat.id, f'Привет, {user}! {emoji.emojize(":sparkles:")}')
        handle_state_one(message, user)
    else:
        bot.send_message(message.chat.id, 'В доступе отказано')
        bot.send_message(message.chat.id, f'{emoji.emojize(":disappointed_face:")}')


@bot.message_handler(func=lambda message: True, state=1)
def handle_state_one(message, user):
    bot.send_message(message.chat.id, 'Захожу в ВК')
    bot.send_message(message.chat.id, users_info[user][-1])
    driver = sign_in_vk_1(user)
    bot.send_message(message.chat.id, 'Введи код')
    bot.register_next_step_handler(message, lambda m: handle_state_two(m, driver, user))


# обработчик ввода кода
@bot.message_handler(func=lambda message: True, state=2)
def handle_state_two(message, driver, user):
    code = message.text
    driver = sign_in_vk_2(driver, code)
    bot.send_message(message.chat.id, 'Готово! Пришли скриншот')
    bot.register_next_step_handler(message, lambda m: handle_state_three(m, driver, user))


@bot.message_handler(content_types=['photo'], state=3)
def handle_state_three(message, driver, user):
    bot.send_message(message.chat.id, 'Скриншот принят')
    bot.send_message(message.chat.id, f'{emoji.emojize(":magnifying_glass_tilted_left:")}')
    image_id = message.photo[-1].file_id
    image_info = bot.get_file(image_id)
    image_path = image_info.file_path
    image_filename = os.path.basename(image_path)
    image_bytes = requests.get(f'https://api.telegram.org/file/bot{bot_token}/{image_path}').content
    save_path = os.path.join(imgs_path, image_filename)
    with open(save_path, 'wb') as f:
        f.write(image_bytes)
    abs_path = os.path.abspath(save_path)
    img_type = define_img_type(abs_path)
    if img_type == 4:
        song_info = recognize_text(abs_path, img_type)
        bot.send_message(message.chat.id, f'"{song_info}"')
        result = get_link(driver, user, song_info, '')
    else:
        title_img_path, author_img_path = crop_img(abs_path, img_type)
        title = recognize_text(title_img_path, img_type)
        author = recognize_text(author_img_path, img_type)
        song_info = title + ' ' + author
        bot.send_message(message.chat.id, f'{song_info}')
        result = get_link(driver, user, title, author)
    bot.send_message(message.chat.id, result)
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button_yes = types.KeyboardButton(text='Да')
    button_no = types.KeyboardButton(text='Нет')
    keyboard.add(button_yes, button_no)
    bot.send_message(message.chat.id, 'Есть ли есть еще скриншоты?', reply_markup=keyboard)
    bot.register_next_step_handler(message, lambda m: handle_state_four(m, driver, user))


@bot.message_handler(content_types=['photo'], state=4)
def handle_state_four(message, driver, user):
    answer = message.text
    if message.content_type == 'text':
        if answer == 'Нет':
            driver.quit()
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            start_button = types.KeyboardButton('/start')
            markup.add(start_button)
            bot.send_message(message.chat.id, f'Окей, до встречи! {emoji.emojize(":waving_hand:")}', reply_markup=markup)
        else:
            bot.send_message(message.chat.id, 'Пришли скриншот')
            bot.register_next_step_handler(message, lambda m: handle_state_three(m, driver, user))
    else:
        handle_state_three(message, driver, user)


if __name__ == '__main__':
    bot.polling(none_stop=True)
