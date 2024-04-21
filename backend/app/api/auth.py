from flask import Blueprint, jsonify, request
import requests
from app.models import User, db

bp = Blueprint("auth", __name__)

@bp.route('/auth/yandex', methods=['GET'])
def auth_user():
    # Проверка токена доступа
    access_token = request.headers.get('Authorization').split(' ')[1]
    url = f'https://login.yandex.ru/info?oauth_token={access_token}'
    response = requests.get(url)
    print('access_token', access_token)
    if response.status_code == 200:
        user_info = response.json()
        result = {
            'first_name': user_info.get('first_name'),
            'last_name': user_info.get('last_name')
        }
        print(user_info.get('id'))
        print(type(user_info.get('id')))
        print(type(user_info.get('first_name')))
        print(type(user_info.get('last_name')))

        # Добавление пользователя в базу данных, если его нет
        yandex_id = user_info.get('id')
        user = db.session.query(User).filter_by(yandex_id=yandex_id).first()
        if (user is None):
            User.add_user(user_info.get('first_name'), user_info.get('last_name'), yandex_id)
        
        return jsonify(result), 200
    else:
        return jsonify({'error': 'Ошибка авторизации'}), 401

# @app.errorhandler(500)
# def handle_500(e):
#     return jsonify({'error': 'Внутренняя ошибка сервера'}), 500