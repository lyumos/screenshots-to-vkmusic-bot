import os
import easyocr
os.environ["CUDA_VISIBLE_DEVICES"]="-1"
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from tqdm import tqdm

def text_recognition(img_path):
    reader = easyocr.Reader(['en', 'ru'])
    text = reader.readtext(img_path, detail=0, paragraph=True, text_threshold=0.8)
    return text


def save_results(text):
    with open('../ig-songs-search-in-vk/text_results.txt', mode='a') as file:
        file.write(', '.join(text))
        file.write('\n')


if __name__ == '__main__':
    path = '/home/lyumos/imgs'
    for filename in tqdm(os.listdir(path), desc='Обработка файлов'):
        file_path = os.path.join(path, filename)
        if os.path.isfile(file_path):
            text = text_recognition(file_path)
            save_results(text)
