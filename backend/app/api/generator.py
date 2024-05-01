from flask import Blueprint, jsonify, request
import requests
from app.models import Generator, db
from werkzeug.utils import secure_filename
import os
from app.services import generator_service
from app.utils import transform_metadata, transform_metadata_back
import threading
# from app import cache 

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
    new_generator.model_config = {
        'model': 'GaussianCopula',
        'model_params': {},
        # 'num_variants': 1,
        # 'num_records': 1000
    }
    new_generator.model_training_status = {
        'is_fetched_data': False,
        'is_model_trained': False,
        'accuracy': None
    }
    
    db.session.commit()

    #dataset_metadata_array = [{"name": name, **details} for name, details in dataset_metadata['columns'].items()]
    #print('dataset_metadata_array', dataset_metadata_array)
    print('Данные генератора', generator_id, user_id, name, table_name, dataset_location, dataset_metadata)
    # print(new_)
    return jsonify({
        'generator_id': generator_id,
        'name': name,
        'table_name': table_name,
        'dataset_metadata': transform_metadata(dataset_metadata),
        'model_config': new_generator.model_config,
        'model_training_status': new_generator.model_training_status,
        'created_at': new_generator.created_at
    }), 201

@bp.route('/generator/all', methods=['Get'])
def get_all_generators():
    generators = Generator.query.all()
    return jsonify([{
        'generator_id': generator.generator_id,
        'name': generator.name,
        'table_name': generator.table_name,
        'dataset_metadata': transform_metadata(generator.dataset_metadata),
        'model_config': generator.model_config,
        'model_training_status': generator.model_training_status,
        'created_at': generator.created_at
    } for generator in generators]), 200

@bp.route('/generator/<generator_id>', methods=['Get'])
def get_generator(generator_id):
    generator = Generator.query.get(generator_id)
    if generator is None:
        return 'Генератор не найден', 404
    return jsonify({
        'generator_id': generator.generator_id,
        'name': generator.name,
        'table_name': generator.table_name,
        'dataset_metadata':transform_metadata(generator.dataset_metadata),
        'model_config': generator.model_config,
        'model_training_status': generator.model_training_status,
        'created_at': generator.created_at,
    }), 200

@bp.route('/generator/delete/<generator_id>', methods=['Delete'])
def delete_generator(generator_id):
    generator = Generator.query.get(generator_id)
    if generator is None:
        return 'Генератор не найден', 404
    db.session.delete(generator)
    db.session.commit()
    return 'Генератор удален', 200

@bp.route('/generator/update/<generator_id>', methods=['Put'])
def update_generator(generator_id):
    generator = Generator.query.get(generator_id)
    if generator is None:
        return 'Генератор не найден', 404
    data = request.get_json()
    generator.name = data['name']
    generator.table_name = data['table_name']

    #print(transform_metadata_back(data['dataset_metadata']))
    dataset_metadata = transform_metadata_back(data['dataset_metadata'])
    generator.dataset_metadata = dataset_metadata
    generator.model_config = data['model_config']
    db.session.commit()
    return 'Генератор обновлен', 200

@bp.route('/generator/train/<generator_id>', methods=['Post'])
def train_generator(generator_id):
    generator = Generator.query.get(generator_id)
    if generator is None:
        return 'Генератор не найден', 404

    generator.model_training_status = {
        'is_fetched_data': False,
        'is_model_trained': False,
        'column_shapes_score': None,
        'column_pair_trends_score': None
    }
    db.session.commit()

    # Запускаем обучение в фоновом потоке
    train_thread = threading.Thread(target=generator_service.train_model, args=(generator.generator_id,))
    train_thread.start()


    # generator.model_location = generator_service.train_model(generator)
    # db.session.commit()

    return 'Обучение начато', 200

import zipfile
from flask import send_file

@bp.route('/generator/generate/<generator_id>', methods=['Post'])
def generate_data(generator_id):
    generator = Generator.query.get(generator_id)
    if generator is None:
        return 'Генератор не найден', 404

    data = request.get_json()
    num_variants = data.get('num_variants')
    num_records = data.get('num_records')

    generated_data = generator_service.generate_data(generator, num_variants, num_records)

    # Архивируем сгенерированные данные
    arhive_location = os.path.abspath(os.path.join('generators', str(generator.generator_id), 'synthetic_data', 'synthetic_data.zip'))

    return send_file(arhive_location, as_attachment=True) # jsonify(generated_data)