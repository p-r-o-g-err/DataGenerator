from flask import Blueprint, jsonify, request
import requests
from app.models import Generator, db
from werkzeug.utils import secure_filename
import os

bp = Blueprint("generator", __name__)

@bp.route('/create_generator', methods=['Post'])
def create_generator():
    data = request.get_json()
    user_id = data.get('user_id')
    name = data.get('name')
    original_dataset = data.get('original_dataset')
    original_metadata = data.get('original_metadata')
    parameters = data.get('parameters')

    Generator.add_generator(user_id, name, original_dataset, original_metadata, parameters)

    return jsonify({'message': 'Генератор успешно создан'}), 201


@bp.route('/get_data', methods=['Post'])
def get_data():
    if 'file' not in request.files:
        return 'Не был передан исходный датасет', 400
    file = request.files['file']
    
    file_bytes = file.read()

    # print(file_bytes)

    return 'good', 200

    # if file.filename == '':
    #     return 'No selected file', 400
    # if file:
    #     filename = secure_filename(file.filename)
    #     file.save(os.path.join('/path/to/save', filename))
    #     return 'File uploaded successfully', 200