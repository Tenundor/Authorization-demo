import base64
import hashlib
import hmac
import json
from typing import Optional

from fastapi import FastAPI, Form, Cookie
from fastapi.responses import Response
from pydantic import BaseModel


class Phone(BaseModel):
    phone: str


app = FastAPI()

SECRET_KEY = '9627fc5c05204e648873b4c476c6c1aa4cf3a1e40cb8b1a405dccfedfd5c7963'
PASSWORD_SALT = '71bffd706e8079620a190837f96944c690d10ee58d23f50f6af5cec480414630'

users = {
    'tenundor@gmail.com': {
        'password': '20120cc9df1494a7ddc35618dc2119e3809b92be6f1702d3dbdc034642e49c05',
        'name': 'Антон',
        'balance': 10_000,
    },
    'ivan@ivan.com': {
        'password': 'ce31c2cc36ebc048116973a6b50ad83b08512d6b8a1f870c0ed780137f210bdf',
        'name': 'Иван',
        'balance': 5_000,
    }
}


def verify_password(password: str, password_hash: str) -> bool:
    return hmac.compare_digest(
        hashlib.sha256((password + PASSWORD_SALT).encode()).hexdigest(),
        password_hash
    )


def sign_data(data: str) -> str:
    """Возвращает подписанные данные"""
    return hmac.new(
        SECRET_KEY.encode(),
        msg=data.encode(),
        digestmod=hashlib.sha256,
    ).hexdigest().upper()


def get_username_from_signed_string(username_signed: str) -> Optional[str]:
    username_base64, sign = username_signed.split('.')
    username = base64.b64decode(username_base64.encode()).decode()
    valid_sign = sign_data(username)
    if hmac.compare_digest(valid_sign, sign):
        return username


def standardize_phone(raw_phone: str) -> str:
    cleared_full_phone = ''

    for symbol in raw_phone:
        if symbol.isnumeric():
            cleared_full_phone += symbol

    code_start_index = cleared_full_phone.find('9', 0, 2)

    if code_start_index == -1:
        return cleared_full_phone

    code_length = 3
    phone_code = cleared_full_phone[code_start_index:code_start_index + code_length]
    phone = cleared_full_phone[code_start_index + code_length:]

    return f'8 ({phone_code}) {phone[:3]}-{phone[3:5]}-{phone[5:]}'


@app.get('/')
def index_page(username: Optional[str] = Cookie(default=None)):
    with open('templates/login.html', 'r') as f:
        login_page = f.read()
    if not username:
        return Response(login_page, media_type='text/html')
    valid_username = get_username_from_signed_string(username)
    if not valid_username:
        response = Response(login_page, media_type='text/html')
        response.delete_cookie(key='username')
        return response
    try:
        user = users[valid_username]
    except KeyError:
        response = Response(login_page, media_type='text/html')
        response.delete_cookie(key='username')
        return response
    return Response(f"Привет, {user['name']}", media_type='text/html')


@app.post('/login')
def process_login_page(username: str = Form(...), password: str = Form(...)):
    user = users.get(username)
    if not user or not verify_password(password, user['password']):
        return Response(
            json.dumps({
                'success': False,
                'message': 'Я вас не знаю!',
            }),
            media_type='application/json'
        )
    response = Response(
        json.dumps({
            'success': True,
            'message': f"Ваш логин: {username}<br />баланс: {user['balance']} руб.",
        }),
        media_type='application/json'
    )
    username_signed = base64.b64encode(username.encode()).decode() + '.' + \
        sign_data(username)
    response.set_cookie(key='username', value=username_signed)
    return response


@app.post('/unify_phone_from_json')
def unify_phone_page(phone: Phone):
    return Response(standardize_phone(phone.phone), media_type='text/html')


@app.post('/unify_phone_from_form')
def unify_phone_from_form_page(phone: str = Form(...)):
    return Response(standardize_phone(phone), media_type='text/html')


@app.get('/unify_phone_from_query')
def unify_phone_from_query_page(phone: str):
    return Response(standardize_phone(phone), media_type='text/html')


@app.get('/unify_phone_from_cookies')
def unify_phone_from_cookies_page(phone: str = Cookie(default=None)):
    return Response(standardize_phone(phone), media_type='text/html')

