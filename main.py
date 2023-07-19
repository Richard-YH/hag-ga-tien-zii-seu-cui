from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import openai
from dotenv import load_dotenv
import os
import json
import requests

load_dotenv()
openai.api_key = os.getenv('CHATGPT_TOKEN')
baseurl = 'http://203.145.221.230:10101'
mandarin_to_hakka_url = baseurl + '/run/predict'


def get_description(place: str):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"請給予「{place}」這個地區的簡介，在五十字以內",
        max_tokens=1024,
        temperature=0.5,
    )

    text = response["choices"][0]["text"]
    audio_json = json.dumps({"fn_index": 0, "data": [text]})
    headers = {'Content-Type': 'application/json'}
    response = requests.post(mandarin_to_hakka_url,
                             data=audio_json,
                             headers=headers)
    if response.status_code == 200:
        json_response = json.loads(response.text)
        audiopath = json_response['data'][0]['name']
        download_link = f'{baseurl}/file={audiopath}'
    else:
        download_link = 'error'

    return {
        'text': text,
        'sound_link': download_link,
    }


def create_app():
    app = FastAPI()

    @app.get("/", response_class=HTMLResponse)
    def index():
        # TODO: maybe return some information about this service?
        with open('index.html') as fh:
            data = fh.read()
        return HTMLResponse(content=data, status_code=200)

    @app.get("/search")
    def search(place: str = '六堆'):
        return get_description(place)

    @app.on_event("startup")
    def on_startup():
        pass

    return app
