import os
import re
from typing import Tuple
import easyocr
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import time
from private_data import vk_login, vk_password, vk_music_link
from PIL import Image
import random


# Обработка ведется при помощи CPU, а не GPU
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

# функция для распознавания типа скриншота
def define_img_type(img_path: str) -> int:
    pass
#     return img_type

# функция для обрезки скриншота
def crop_img(img_path: str, img_type: int) -> tuple[str, str]:
    crop_pattern = {1: [[160, 140, 651, 179], [160, 180, 651, 223]], # 1 - аудио рилс
                    2: [[160, 510, 651, 549], [160, 550, 651, 593]], # 2 - аудио из историй
                    3: [[0, 650, 1242, 880], [0, 881, 1242, 931]]} # 3 - скриншоты приложения шазам
    crop_coords = crop_pattern[img_type]
    with Image.open(img_path) as image:
        title_image = image.crop(crop_coords[0])
        author_image = image.crop(crop_coords[1])
        title_image_path: str = img_path.split('.')[0] + 'title_cropped.' + img_path.split('.')[1]
        author_image_path: str = img_path.split('.')[0] + 'author_cropped.' + img_path.split('.')[1]
        title_image.save(title_image_path, format='JPEG')
        author_image.save(author_image_path, format='JPEG')
    return title_image_path, author_image_path


# функция распознования текста и его фильтрации
def recognize_text(img_path: str) -> str:
    reader = easyocr.Reader(['en', 'fr', 'pt', 'es'])
    text = reader.readtext(img_path, detail=0, paragraph=True, text_threshold=0.8)
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
def get_link(driver, title, author):
    ActionChains(driver).key_down(Keys.CONTROL).send_keys('t').key_up(Keys.CONTROL).perform()
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(1)
    driver.get(vk_music_link)
    time.sleep(2)
    search = driver.find_element(By.XPATH, "//input[@class = 'ui_search_field _field']")
    song_info = title + ' ' + author
    search.send_keys(song_info)
    search.send_keys(Keys.RETURN)
    time.sleep(3)
    try:
        songs_list = driver.find_elements(By.CLASS_NAME, "audio_row__inner")
        song = songs_list[30]
        song_link = song.find_elements(By.TAG_NAME, 'a')[-1].get_attribute('href')
        if len(song_link) != 0:
            return f'Вот ссылка на песню со скриншота: {song_link}'
        else:
            singer_link = song.find_elements(By.TAG_NAME, 'a')[0].get_attribute('href')
            return f'К сожалению, ссылку на песню выцепить не удалось. Но вот ссылка на исполнителя: {singer_link}'
    except IndexError:
        search.clear()
        time.sleep(1)
        song_info = title
        search.send_keys(song_info)
        search.send_keys(Keys.RETURN)
        time.sleep(3)
        songs_list = driver.find_elements(By.CLASS_NAME, "audio_row__inner")
        song = songs_list[30]
        song_link = song.find_elements(By.TAG_NAME, 'a')[-1].get_attribute('href')
        return f'Возможно, это она: {song_link}'