import os
import re
import bs4
import easyocr
import requests
from fake_headers import Headers

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
                            new_reg = r'\b\w*(?:music|official)\w*\b'
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


if __name__ == '__main__':
    path = '/home/lyumos/imgs'
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        if os.path.isfile(file_path):
            text = recognize_text(file_path)
            song_info = filter_text(text)

