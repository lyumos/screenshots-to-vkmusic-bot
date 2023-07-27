import os
import re
import easyocr
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import time
from private_data import vk_login, vk_password, vk_music_link


# Обработка ведется при помощи CPU, а не GPU
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"


# функция распознавания всего текста изображения
def recognize_text(img_path: str) -> list:
    reader = easyocr.Reader(['en', 'ru'])
    text = reader.readtext(img_path, detail=0, paragraph=True, text_threshold=0.8)
    return text


# функция фильтрафии всего текста
def filter_text(text: list) -> str:
    filtered_text = []
    for element in text:
        if not (re.match(r'\s*\d{1,3}[.,*:]\d{2}', element) or re.match(r'^[а-яА-ЯёЁ\s]+$', element)):
            if 'LTE' not in element:
                latin_letters = sum(1 for char in element if char.isalpha() and char.isascii())
                digits = sum(1 for char in element if char.isdigit())
                cyrillic_letters = sum(1 for char in element if char.isalpha() and not char.isascii())
                if latin_letters > sum([digits, cyrillic_letters]):
                    regex = r'[^a-zA-Z\s]'
                    result = re.sub(regex, '', element).strip()
                    if not result[0].islower():
                        lower = sum(1 for c in result if c.islower())
                        upper = sum(1 for c in result if c.isupper())
                        if lower > upper:
                            new_reg = r'\b\w*(?:music|official|Reels|musique)\w*\b'
                            new_res = re.sub(new_reg, '', result).strip()
                            filtered_text.append(new_res)
    if len(filtered_text) == 2:
        if filtered_text[0] in filtered_text[1]:
            return filtered_text[1]
        elif filtered_text[1] in filtered_text[0]:
            return filtered_text[0]
        else:
            return ', '.join(filtered_text)
    else:
        return ', '.join(filtered_text)


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
    time.sleep(1)
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(1)
    driver.get(vk_music_link)
    time.sleep(1)
    search = driver.find_element(By.XPATH, "//input[@class = 'ui_search_field _field']")
    search.send_keys(song_info)
    search.send_keys(Keys.RETURN)
    time.sleep(1)
    song = driver.find_elements(By.CLASS_NAME, "audio_row__inner")[42]
    time.sleep(1)
    song_link = song.find_elements(By.TAG_NAME, 'a')[-1].get_attribute('href')
    return song_link


