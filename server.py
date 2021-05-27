import base64
import hashlib
import hmac
from typing import Optional

from fastapi import FastAPI, Form, Cookie
from fastapi.responses import Response


app = FastAPI()

SECRET_KEY = '9627fc5c05204e648873b4c476c6c1aa4cf3a1e40cb8b1a405dccfedfd5c7963'

users = {
    'tenundor@gmail.com': {
        'password': '12345',
        'name': 'Антон',
        'balance': 10_000,
    }
}


def sign_data(data: str) -> str:
    """Возвращает подписанные данные"""
    return hmac.new(
        SECRET_KEY.encode(),
        msg=data.encode(),
        digestmod=hashlib.sha256,
    ).hexdigest().upper()


@app.get('/')
def index_page(username: Optional[str] = Cookie(default=None)):
    with open('templates/login.html', 'r') as f:
        login_page = f.read()
    if username:
        try:
            user = users[username]
        except KeyError:
            response = Response(login_page, media_type='text/html')
            response.delete_cookie(key='username')
            return response
        return Response(f"Привет, {user['name']}", media_type='text/html')
    return Response(login_page, media_type='text/html')


@app.post('/login')
def process_login_page(username: str = Form(...), password: str = Form(...)):
    user = users.get(username)
    if not user or user['password'] != password:
        return Response('Я вас не знаю!', media_type='text/html')
    response = Response(
        f"Ваш логин: {username}<br />баланс: {user['balance']} руб.", media_type='text/html'
    )
    username_signed = base64.b64encode(username.encode()).decode() + '.' + \
        sign_data(username)
    response.set_cookie(key='username', value=username_signed)
    return response
