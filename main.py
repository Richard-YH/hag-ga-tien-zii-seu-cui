from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import openai
from dotenv import load_dotenv
import os
import requests
from bardapi import Bard
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import time
import base64
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from fastapi.staticfiles import StaticFiles

load_dotenv()
openai.api_key = os.getenv('CHATGPT_TOKEN')
baseurl = 'http://203.145.221.230:10101'
mandarin_to_hakka_url = baseurl + '/run/predict'
bard = Bard(token=os.getenv('BARD_TOKEN'))


def get_bone():
    publicKey = '-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCOQ5kNFYF/2+xBrCuwEuAHwhYr\nnXbU4/VCb4y97cm79PfQIRfbjavzDv99AKQ+Paujs9dbacgydeecUk5x4YuX5G+L\n+6IThMKiu2TfIpJhj1zaCqd4NLQjFewLdTWBxVhzXo90I/+TCw9pDqvdC6fTvsCG\niK/gTaLpZnOa0Rt1vQIDAQAB\n-----END PUBLIC KEY-----'
    key = RSA.import_key(publicKey)
    cipher = PKCS1_v1_5.new(key)
    message = f'{int(time.time()*1000)}ilovehakka'.encode()
    ciphertext = cipher.encrypt(message)
    bytes_encode = base64.b64encode(ciphertext).decode()
    return bytes_encode


def decode_part(text, is_han_ji=True):
    text = '【\t\t〗' + text
    array_a = text.strip().split('【\t')
    array_b = []
    for a in array_a[1:]:
        tmp = a.split('\t〗')
        if is_han_ji:
            array_b.extend(list(tmp[0]) + [tmp[1]])
        else:
            array_b.extend(tmp[0].split(' ') + [tmp[1]])

    return [a for a in array_b if a]


def get_img_html(place):
    source = requests.get(
        f'https://www.google.com/search?q={place}&source=lnms&tbm=isch').text

    # Parse the page source and download pics
    soup = BeautifulSoup(str(source), "lxml")
    imgs = []

    for img in soup.body.find_all(
            "div", recursive=False)[2].find('tr').find_all('img', limit=4):
        imgs.append(img['src'])

    return imgs


def get_description(place: str):
    # get Mandarin text

    text = bard.get_answer(f'#zh-tw 請給予「{place}」這個地區或物品的簡介，在五十字以內')['content']

    # get Hakka sound, han-ji, phing-im

    data = {
        'bone': get_bone(),
        'page_name': 'hakkadic',
        'input_lang': 'zh-tw',
        'input_accent': '四縣腔T',
        'input_txt': text
    }
    response = requests.post('https://www.gohakka.org/py/translate.py',
                             data=urlencode(data))

    json = response.json()
    han_ji = decode_part(json['hakkapart'], True)
    phing_im = decode_part(json['participle'], False)
    if len(han_ji) != len(phing_im):
        print(f'Length not same:\n{han_ji}\n{" ".join(phing_im)}')

    hakka = list(zip(han_ji, phing_im))

    return {
        'mandarin': text,
        'hakka': hakka,
        'sound_link':
        f'https://hts.ithuan.tw/語音合成?查詢腔口=四縣腔&查詢語句={json["yee"]}',
        'images': get_img_html(place)
    }


def create_app():
    app = FastAPI()

    @app.get("/", response_class=HTMLResponse)
    def index():
        with open('index.html') as fh:
            data = fh.read()
        return HTMLResponse(content=data, status_code=200)

    @app.get("/search")
    def search(place: str = '六堆'):
        return get_description(place)

    @app.on_event("startup")
    def on_startup():
        pass

    app.mount("/images", StaticFiles(directory="images"), name="images")

    return app
