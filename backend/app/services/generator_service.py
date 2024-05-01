from sdv.metadata import SingleTableMetadata
from sdv.single_table import GaussianCopulaSynthesizer, CTGANSynthesizer, TVAESynthesizer
from sdv.lite import SingleTablePreset
import pandas as pd
import chardet
import os
from app.models import Generator, db
from sdv.evaluation.single_table import evaluate_quality
import zipfile
# from app import cache 
# import json

def read_csv(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    print('Кодировка файла:', result['encoding'])
    data = pd.read_csv(file_path, encoding=result['encoding'])
    return data

def get_metadata(dataset_location):
    data = read_csv(dataset_location)
    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(data)
    # Предобработка метаданных
    metadata = replace_types(metadata, data)
    metadata = split_numerical(metadata, data)
    metadata = remove_pii(metadata)
    metadata_dict = metadata.to_dict()
    metadata_dict = remove_primary_key(metadata_dict)
    metadata_dict = remove_metadata_spec_version(metadata_dict)
    # print(metadata_dict)
    return metadata_dict

    
    # try:
    #     metadata = get_metadata_for_sdv(metadata_dict)
    #     synthesizer = GaussianCopulaSynthesizer(metadata) #  enforce_min_max_values=True
    #     synthesizer.fit(data)
    #     synthetic_data = synthesizer.sample(num_rows=500)
    #     synthetic_data.to_excel('synthetic_data5.xlsx', index=False)
    # except Exception as e:
    #     print('Ошибка при обучении', e)
    
    # # Сохраняем данные в CSV
    # synthetic_data.to_csv('synthetic_data2.csv', index=False)

    # # Сохраняем данные в XLSX
    # synthetic_data.to_excel('synthetic_data2.xlsx', index=False)


# region Предобработка метаданных

# Заменяет типы данных, которые не входят в перечень ('numerical','categorical','datetime','boolean')
# на 'numeric', если значения в столбце являются числами и 'categorical' в противном случае
def replace_types(metadata: SingleTableMetadata, data: pd.DataFrame):
    for column in metadata.columns:
        if metadata.columns[column]['sdtype'] not in ['numerical','categorical','datetime','boolean']: # ,'id'
            if data[column].dtype in ['int64','float64']:
                # print('Найден числовой столбец:', column, 'с типом в метаданных:', metadata.columns[column]['sdtype'], 'и типом в данных:', data[column].dtype)
                metadata.columns[column]['sdtype'] = 'numerical'
            else:
                # print('Найден категориальный столбец:', column, 'с типом в метаданных:', metadata.columns[column]['sdtype'], 'и типом в данных:', data[column].dtype)
                metadata.columns[column]['sdtype'] = 'categorical'
    return metadata
    
# Удаляет атрибут pii из метаданных, который необходим для распознавания персональных данных
def remove_pii(metadata: SingleTableMetadata):
    for column in metadata.columns:
        if 'pii' in metadata.columns[column]:
            del metadata.columns[column]['pii']
    return metadata


def remove_primary_key(metadata: dict):
    if 'primary_key' in metadata:
        del metadata['primary_key']
    return metadata

# Разбиение числового типа numerical на числовые дискретные (numerical digital) и числовые непрерывные (numerical continuous)
def split_numerical(metadata: SingleTableMetadata, data: pd.DataFrame):
    for column in metadata.columns:
        if metadata.columns[column]['sdtype'] == 'numerical':
            if data[column].dtype == 'int64':
                metadata.columns[column]['sdtype'] = 'numerical digital'
            else:
                metadata.columns[column]['sdtype'] = 'numerical continuous'
    return metadata                  

def remove_metadata_spec_version(metadata: dict):
    del metadata['METADATA_SPEC_VERSION']
    return metadata

# Объединяет типы numerical digital и numerical continuous в тип numerical. Используется перед загрузкой метаданных в модель.
# def join_numerical(metadata: SingleTableMetadata):
#     for column in metadata.columns:
#         if metadata.columns[column]['sdtype'] in ['numerical digital','numerical continuous']:
#             metadata.columns[column]['sdtype'] = 'numerical'
#     return metadata
# endregion


def get_metadata_for_sdv(metadata_dict: dict):
    metadata_dict["METADATA_SPEC_VERSION"] = "SINGLE_TABLE_V1"
    for column in metadata_dict['columns']:
        if metadata_dict['columns'][column]['sdtype'] in ['numerical digital','numerical continuous']:
            metadata_dict['columns'][column]['sdtype'] = 'numerical'
    metadata = SingleTableMetadata.load_from_dict(metadata_dict)
    return metadata


from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Создаем новую сессию для обновления model_location
Session = sessionmaker(bind=create_engine('postgresql://postgres:1111@localhost:5432/dataGenerator?client_encoding==utf8'))
session = Session()

def train_model(generator_id):
    # Получаем новую копию объекта generator, используя новую сессию
    generator = session.query(Generator).get(generator_id)

    # TODO Временно получаю метаданные из файла, так как модель на категориальных данных работает намного дольше
    data = read_csv(generator.dataset_location)
    # metadata = get_metadata(generator.dataset_location)
    # metadata = get_metadata_for_sdv(metadata)
    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(data)

    generator.model_training_status = {
        'is_fetched_data': True,
        'is_model_trained': False,
        'column_shapes_score': None,
        'column_pair_trends_score': None
    }
    session.commit()

    print('Выбрана модель:', generator.model_config['model'])
    # model_params = generator.model_config['model_params']
    
    
    synthesizer = None #CTGANSynthesizer(metadata, epochs=3, verbose=True)
    if (generator.model_config['model'] == 'GaussianCopula'):
        synthesizer = GaussianCopulaSynthesizer(metadata)
    elif (generator.model_config['model'] == 'CTGAN'):
        synthesizer = CTGANSynthesizer(metadata)
    elif (generator.model_config['model'] == 'TVAE'):
        synthesizer = TVAESynthesizer(metadata)

    synthesizer.fit(data)

    # Оценка качества модели
    synthetic_data = synthesizer.sample(num_rows=data.shape[0])
    quality_report = evaluate_quality(
        real_data=data,
        synthetic_data=synthetic_data,
        metadata=metadata)
    # print('Отчет о качестве модели')
    # print(quality_report)
    # print(type(quality_report))
    # print('Детали отчета о качестве модели')
    # print(quality_report.get_details(property_name='Column Shapes'))
    # print(type(quality_report.get_details(property_name='Column Shapes')))
    # print(quality_report.get_details(property_name='Column Pair Trends'))
    # print(type(quality_report.get_details(property_name='Column Pair Trends')))

    column_shapes_score = quality_report.get_details(property_name='Column Shapes')
    average_column_shapes_score = round(column_shapes_score['Score'].mean(), 4)
    column_pair_trends_score = quality_report.get_details(property_name='Column Pair Trends')
    average_column_pair_trends_score = round(column_pair_trends_score['Score'].mean(), 4)


    model_location = os.path.join('generators', str(generator.generator_id), 'model.pkl')
    synthesizer.save(filepath=model_location)
    generator.model_training_status = {
        'is_fetched_data': True,
        'is_model_trained': True,
        'column_shapes_score': average_column_shapes_score,
        'column_pair_trends_score': average_column_pair_trends_score
    }
    
    # Обновляем model_location и сохраняем изменения в базе данных
    generator.model_location = model_location
    session.commit()
    print('Модель обучена и сохранена по пути:', model_location)

    # synthetic_data = synthesizer.sample(num_rows=500)
    # synthetic_data.to_excel('synthetic_data.xlsx', index=False)
    #return model_location


import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

def generate_data(generator, num_variants, num_records):
    # Получаем новую копию объекта generator, используя новую сессию
    #generator = session.query(Generator).get(generator_id)
    synthesizer = None
    if (generator.model_config['model'] == 'GaussianCopula'):
        synthesizer = GaussianCopulaSynthesizer.load(generator.model_location)
    elif (generator.model_config['model'] == 'CTGAN'):
        synthesizer = CTGANSynthesizer.load(generator.model_location)
    elif (generator.model_config['model'] == 'TVAE'):
        synthesizer = TVAESynthesizer.load(generator.model_location)

    dataset_folder = os.path.join('generators', str(generator.generator_id), 'synthetic_data')
    # Создаем папку, если она еще не существует
    os.makedirs(dataset_folder, exist_ok=True)

    for i in range(num_variants):
        synthetic_data = synthesizer.sample(num_rows=num_records)
        dataset_location=os.path.join(dataset_folder, f'synthetic_data{i}.csv')
        synthetic_data.to_csv(dataset_location, index=False)

    # Формирование отчета о данных
    synthetic_data = synthesizer.sample(num_rows=num_records)
    real_data = pd.read_csv(generator.dataset_location)  # TODO Заменить на read_csv(generator.dataset_location)
    get_data_report(generator, synthetic_data, real_data)


    # Создание архива со сгенерированными данными и отчетом
    arhive_location = os.path.join(dataset_folder, 'synthetic_data.zip') # {generator.name}_
    with zipfile.ZipFile(arhive_location, 'w') as zipf:
        for i in range(num_variants):
            file_path = os.path.join(dataset_folder, f'synthetic_data{i}.csv')
            zipf.write(file_path, arcname=os.path.join('datasets', f'synthetic_data{i}.csv'))
            os.remove(file_path)  # Удаление файла после добавления в архив

        # Добавление отчета в архив
        report_path = os.path.join(dataset_folder, 'model-report.html')
        zipf.write(report_path, arcname='model-report.html')
        os.remove(report_path) 
    
    
    
    # return synthetic_data
    # model_location = os.path.join('generators', str(generator.generator_id), 'syntehtic_data.csv')
    # synthetic_data.to_csv('synthetic_data.csv', index=False)
    # print('Сгенерированные данные сохранены в файле synthetic_data.csv')

def get_data_report(generator, synthetic_data, real_data):
    # Создать пустой список для хранения HTML-строк каждого графика
    html_strings = []

    # Добавить заголовок и общую информацию перед графиками
    html_strings.append(f'<h1 style="text-align:center;">Отчет о данных для генератора "{generator.name}"</h1>')
    html_strings.append('<h2 style="text-align:center;">Общая информация</h2>')
    html_strings.append(f'<p style="text-align:center;">Строк в исходном датасете: {len(real_data)}</p>')
    html_strings.append(f'<p style="text-align:center;">Строк в сгенерированном датасете: {len(synthetic_data)}</p>')
    html_strings.append(f'<p style="text-align:center;">Столбцов: {len(synthetic_data.columns)}</p>')
    html_strings.append('<hr>')
    html_strings.append('<h2 style="text-align:center;">Распределение признаков</h2>')

    # Создать графики для каждого столбца
    for variable in synthetic_data.columns:
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=real_data[variable], name='Исходные данные', histnorm='probability density'))
        fig.add_trace(go.Histogram(x=synthetic_data[variable], name='Синтетические данные', histnorm='probability density'))

        # Обновить макет, чтобы показать оба графика наложенными
        fig.update_layout(barmode='overlay', title={
            'text': variable,
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        })
        fig.update_traces(opacity=0.75)

        # Сохранить график в HTML-строку и добавить его в список
        html_string = pio.to_html(fig, full_html=False)
        html_strings.append(html_string)

    # Объединить все HTML-строки в одну и сохранить в файл
    dataset_folder = os.path.join('generators', str(generator.generator_id), 'synthetic_data')
    data_report_location = os.path.join(dataset_folder, 'model-report.html')
    with open(data_report_location, 'w', encoding='utf-8') as f:
        f.write(''.join(html_strings))
