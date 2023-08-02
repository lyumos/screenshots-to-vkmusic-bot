import os
import re
import easyocr
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import time
from private_data import vk_login, vk_password, vk_music_link
from PIL import Image


# Обработка ведется при помощи CPU, а не GPU
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

# функция для распознавания типа скриншота
def define_img_type(img_path: str) -> int:
    pass
#     return img_type

# функция для обрезки скриншота
def crop_img(img_path: str, img_type: int) -> str:
    crop_pattern = {1: [160, 140, 651, 223], 2: [160, 510, 651, 593], 3: [0, 0, 0, 0]}
    crop_coords = crop_pattern[img_type]
    with Image.open(img_path) as image:
        cropped_image = image.crop(crop_coords)
        cropped_image_path: str = img_path.split('.')[0] + '_cropped.' + img_path.split('.')[1]
        cropped_image.save(cropped_image_path, format='JPEG')
    return cropped_image_path

# return img_path

# функция распознавания всего текста изображения
def recognize_text(img_path: str) -> list:
    reader = easyocr.Reader(['en', 'fr', 'pt', 'es'])
    text = reader.readtext(img_path, detail=0, paragraph=True, text_threshold=0.8)
    print(text)
    return text


# функция фильтрафии всего текста
def filter_text(text: list) -> str:
    filtered_text = []
    for element in text:
        if 'music' in element:
            new_element = element.replace('music', '')
            filtered_text.append(new_element)
        elif 'official' in element:
            new_element = element.replace('official', '')
            filtered_text.append(new_element)
        elif 'musique' in element:
            new_element = element.replace('musique', '')
            filtered_text.append(new_element)
        elif '0' in element:
            new_element = element.replace('0', '')
            filtered_text.append(new_element)
        else:
            filtered_text.append(element)
    return ' '.join(filtered_text)


# функция для входа вк
def sign_in_vk_1():
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0")

    driver = webdriver.Chrome()

    driver.get("https://vk.com/")
    time.sleep(1)

    login = driver.find_element(By.ID, "index_email")
    login.clear()
    login.send_keys(vk_login)
    time.sleep(1)

    driver.find_element(By.CLASS_NAME, "FlatButton--primary").click()
    time.sleep(1)

    password = driver.find_element(By.XPATH, "//input[@name = 'password']")
    password.send_keys(vk_password)
    password.send_keys(Keys.RETURN)
    time.sleep(3)

    button1 = driver.find_element(By.XPATH,
                                  "//button[@class='vkuiButton vkuiButton--sz-l vkuiButton--lvl-tertiary vkuiButton--clr-accent vkuiButton--aln-center vkuiButton--sizeY-compact vkuiButton--stretched vkuiTappable vkuiTappable--sizeX-regular vkuiTappable--hasHover vkuiTappable--hasActive vkuiTappable--mouse']")
    ActionChains(driver).move_to_element(button1).click().perform()
    time.sleep(3)

    return driver


def sign_in_vk_2(driver, code):
    auth_code = driver.find_element(By.XPATH, "//input[@name = 'otp']")
    auth_code.send_keys(code)
    auth_code.send_keys(Keys.RETURN)

    return driver


# функция для получения ссылки на первую песню из поиска
def get_link(driver, song_info):
    ActionChains(driver).key_down(Keys.CONTROL).send_keys('t').key_up(Keys.CONTROL).perform()
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(1)
    driver.get(vk_music_link)
    time.sleep(2)
    search = driver.find_element(By.XPATH, "//input[@class = 'ui_search_field _field']")
    search.send_keys(song_info)
    search.send_keys(Keys.RETURN)
    time.sleep(3)
    songs_list = driver.find_elements(By.CLASS_NAME, "audio_row__inner")
    first_song_index = 30
    try:
        song = songs_list[first_song_index]
    except IndexError:
        first_song_index = min(first_song_index, len(songs_list) - 1)
        song = songs_list[first_song_index]
    print(f'Индекс: {first_song_index}')
    print(f'Длина списка песен: {len(songs_list)}')
    time.sleep(1)
    song_link = song.find_elements(By.TAG_NAME, 'a')[-1].get_attribute('href')
    if len(song_link) == 0:
        # while song_link == 0:
            # last_song_index = len(songs_list) - 1
        song = songs_list[-1]
        song_link = song.find_elements(By.TAG_NAME, 'a')[-1].get_attribute('href')
        # print(first_song_index)
    return song_link
