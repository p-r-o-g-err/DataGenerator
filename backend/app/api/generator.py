from flask import Blueprint, jsonify, request
import requests
from app.models import Generator, db
from werkzeug.utils import secure_filename
import os
from app.services import generator_service

bp = Blueprint("generator", __name__)

@bp.route('/generator/new', methods=['Post'])
def create_generator():
    # Получаем данные из формы
    user_id = request.form.get('userId')
    name = request.form.get('name')
    # Проверяем, был ли передан файл
    if 'originalDataset' not in request.files:
        return 'Не был передан исходный датасет', 400
    file = request.files['originalDataset']

    # Получаем безопасное имя файла и определяем путь для сохранения
    table_name = secure_filename(file.filename)
    # Добавляем генератор в базу данных
    new_generator = Generator.add_generator(user_id, name, table_name)
    # Получаем generator_id
    generator_id = str(new_generator.generator_id)
    # Определяем путь для сохранения файла
    dataset_location = os.path.join('generators', generator_id, table_name)
    # Создаем папку, если она еще не существует
    os.makedirs(os.path.dirname(dataset_location), exist_ok=True)
    # Сохраняем файл
    file.save(dataset_location)
    # Обновляем dataset_location в базе данных
    new_generator.dataset_location = dataset_location
    # Распознавание структуры данных
    dataset_metadata = generator_service.get_metadata(dataset_location)
    # Обновляем dataset_metadata в базе данных
    new_generator.dataset_metadata = dataset_metadata
    db.session.commit()
    print('Данные генератора', generator_id, user_id, name, table_name, dataset_location, dataset_metadata) 
    
    return jsonify({'message': 'Генератор успешно создан'}), 201
    

@bp.route('/generator/config', methods=['Post'])
def generator_config():

     # # model_config
    # Задать модель, ее параметры, сколько вариантов нужно, какого размера

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