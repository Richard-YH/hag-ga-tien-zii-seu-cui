from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import openai
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv('CHATGPT_TOKEN')


def get_description(place: str):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"請給予「{place}」這個地區的簡介，在一百字以內",
        max_tokens=1024,
        temperature=0.5,
    )
    # print(response)

    return response["choices"][0]["text"]


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
