from fastapi import FastAPI, Form
from fastapi.responses import Response


app = FastAPI()

users = {
    'tenundor@gmail.com': {
        'password': '12345',
        'balance': 10_000,
    }
}


@app.get('/')
def index_page():
    with open('templates/login.html', 'r') as f:
        login_page = f.read()
    return Response(login_page, media_type='text/html')


@app.post('/login')
def process_login_page(username: str = Form(...), password: str = Form(...)):
    user = users.get(username)
    if not user or user['password'] != password:
        return Response('Я вас не знаю!', media_type='text/html')
    return Response(
        f"Ваш логин: {username}<br />баланс: {user['balance']} руб.", media_type='text/html'
    )
