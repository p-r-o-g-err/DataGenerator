from sdv.metadata import SingleTableMetadata
from sdv.single_table import GaussianCopulaSynthesizer, CTGANSynthesizer, TVAESynthesizer
from sdv.lite import SingleTablePreset
import pandas as pd
import chardet
import os
from app.models import Generator, db
from sdv.evaluation.single_table import evaluate_quality
import zipfile
import plotly.graph_objects as go
import plotly.io as pio
from sdv.evaluation.single_table import get_column_plot
from sdv.evaluation.single_table import get_column_pair_plot
import json

# Получить кодировку файла
def get_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    print('Кодировка файла:', result['encoding'])
    return result['encoding']

# Прочитать датасет из CSV-файла
def read_csv(generator):
    print('Чтение файла:', generator.dataset_location, 'с кодировкой:', generator.dataset_encoding)
    return pd.read_csv(generator.dataset_location, encoding=generator.dataset_encoding)

# Распознать структуру данных (типы столбцов) для сохранения в БД
def get_metadata(generator):
    # Заменяет типы данных, которые не входят в перечень ('numerical','categorical','datetime','boolean')
    # на 'numeric', если значения в столбце являются числами и 'categorical' в противном случае
    def replace_types(metadata: SingleTableMetadata, data: pd.DataFrame):
        for column in metadata.columns:
            # print('Столбец:', column, 'с типом в метаданных:', metadata.columns[column]['sdtype'], 'и типом в данных:', data[column].dtype)
            if metadata.columns[column]['sdtype'] not in ['numerical','categorical','datetime']: # ,'id'
                if data[column].dtype in ['int64','float64']:
                    # print('Найден числовой столбец:', column, 'с типом в метаданных:', metadata.columns[column]['sdtype'], 'и типом в данных:', data[column].dtype)
                    metadata.columns[column]['sdtype'] = 'numerical'
                else:
                    # print('Найден категориальный столбец:', column, 'с типом в метаданных:', metadata.columns[column]['sdtype'], 'и типом в данных:', data[column].dtype)
                    metadata.columns[column]['sdtype'] = 'categorical'
            if data[column].dtype == 'bool':
                metadata.columns[column]['sdtype'] = 'boolean'
            # if data[column].dtype in ['int64','float64']:
            #     metadata.columns[column]['sdtype'] = 'numerical'
                
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

    def remove_metadata_spec_version(metadata: dict):
        del metadata['METADATA_SPEC_VERSION']
        return metadata

    data = read_csv(generator)
    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(data)
    # Предобработка метаданных
    metadata = replace_types(metadata, data)
    metadata = split_numerical(metadata, data)
    metadata = remove_pii(metadata)
    metadata_dict = metadata.to_dict()
    metadata_dict = remove_primary_key(metadata_dict)
    metadata_dict = remove_metadata_spec_version(metadata_dict)
    
    return metadata_dict

# Преобразовать структуру данных из БД в структуру данных для работы с моделями SDV
def get_metadata_for_sdv(metadata_dict: dict):
    metadata_dict["METADATA_SPEC_VERSION"] = "SINGLE_TABLE_V1"
    # Объединение типов numerical digital и numerical continuous в тип numerical
    for column in metadata_dict['columns']:
        if metadata_dict['columns'][column]['sdtype'] in ['numerical digital','numerical continuous']:
            metadata_dict['columns'][column]['sdtype'] = 'numerical'
    metadata = SingleTableMetadata.load_from_dict(metadata_dict)
    return metadata

# Проверить датасет на наличие 50 строк и 2 столбцов
def check_dataset(generator):
    try:
        data = read_csv(generator)
        print('Размер', len(data), len(data.columns))
        return len(data) >= 50 and len(data.columns) >= 2
    except Exception as e:
        print('Ошибка чтения файла:', e)
        return False

# Проверить корректность типов столбцов в датасете
def check_column_types(generator):
    data = read_csv(generator)
    metadata = get_metadata_for_sdv(generator.dataset_metadata)
    metadata_columns = metadata.columns
    for column in data.columns:
        if data[column].dtype in ['int64', 'float64'] and metadata_columns[column]['sdtype'] not in ['categorical', 'numerical']:
            #print('Столбец', column, 'с типом', data[column].dtype, 'не соответствует типу в метаданных:', metadata_columns[column]['sdtype'])
            return False
        if data[column].dtype == 'object' and metadata_columns[column]['sdtype'] not in ['categorical', 'datetime']:
            # # Если тип object, но в метаданных числовой, то пробуем преобразовать первые 5 значений в числа, если ошибка, то проверка не пройдена
            # if metadata_columns[column]['sdtype'] == 'numerical':
            #     try:
            #         pd.to_numeric(data[column].head(5))
            #     except:
            #         return False
            # else:
            print('Столбец', column, 'с типом', data[column].dtype, 'не соответствует типу в метаданных:', metadata_columns[column]['sdtype'])
            return False
        elif data[column].dtype == 'bool' and metadata_columns[column]['sdtype'] != 'boolean':
            #print('Столбец', column, 'с типом', data[column].dtype, 'не соответствует типу в метаданных:', metadata_columns[column]['sdtype'])
            return False
    
    return True
    # if change_type_cols(generator): return True
    # else: return False

# Приведение данных в CSV-файле к типу из метаданных
def change_type_cols(generator):
    data = read_csv(generator)
    metadata = generator.dataset_metadata
    metadata_columns = metadata['columns']
    try:
        for column in metadata_columns:
            sdtype = metadata_columns[column]['sdtype']
            if sdtype == 'numerical digital' and data[column].dtype != 'int64':
                print(f'int64, Столбец {column} с типом {data[column].dtype} и типом в метаданных: {sdtype}')
                data[column] = data[column].astype('int64')
                # data[column] = pd.to_numeric(data[column]).astype('int64')
            elif sdtype == 'numerical continuous' and data[column].dtype != 'float64':
                print(f'float64, Столбец {column} с типом {data[column].dtype} и типом в метаданных: {sdtype}')
                data[column] = data[column].astype('float64')
                # data[column] = pd.to_numeric(data[column]).astype('float64')
            elif sdtype == 'categorical' and data[column].dtype != 'object':
                print(f'object, Столбец {column} с типом {data[column].dtype} и типом в метаданных: {sdtype}')
                data[column] = data[column].astype('object')
            elif sdtype == 'datetime' and data[column].dtype != 'datetime64[ns]':
                print(f'datetime64[ns], Столбец {column} с типом {data[column].dtype} и типом в метаданных: {sdtype}')
                data[column] = pd.to_datetime(data[column])
            elif sdtype == 'boolean' and data[column].dtype != 'bool':
                print(f'bool, Столбец {column} с типом {data[column].dtype} и типом в метаданных: {sdtype}')
                data[column] = data[column].astype('bool')
        return data
    except Exception as e:
        print(f'Ошибка при преобразовании типов: {e}')
        return None

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Создаем новую сессию для обновления model_training_status
Session = sessionmaker(bind=create_engine('postgresql://postgres:1111@localhost:5432/dataGenerator?client_encoding==utf8'))
session = Session()

def train_model(generator_id):
    # Получаем новую копию объекта generator, используя новую сессию
    generator = session.query(Generator).get(generator_id)

    ########### 1. Извлекаем метаданные
    metadata = get_metadata_for_sdv(generator.dataset_metadata)

    generator.model_training_status = {
        'is_fetched_data': True,
        'is_model_trained': False,
        'is_report_generated': False,
        'column_shapes_score': None,
        'column_pair_trends_score': None,
        # 'column_pair_trends': {}
    }
    session.commit() # Сохраняем изменения в БД

    ########### 2. Обучаем модель
    print('Выбрана модель:', generator.model_config['model'])
    # model_params = generator.model_config['model_params'] # Параметры модели
    synthesizer = None #CTGANSynthesizer(metadata, epochs=3, verbose=True)
    if (generator.model_config['model'] == 'GaussianCopula'):
        synthesizer = GaussianCopulaSynthesizer(metadata)
    elif (generator.model_config['model'] == 'CTGAN'):
        synthesizer = CTGANSynthesizer(metadata)
    elif (generator.model_config['model'] == 'TVAE'):
        synthesizer = TVAESynthesizer(metadata)

    data = read_csv(generator)
    synthesizer.fit(data)
    # Синтетические данные для отчета
    synthetic_data = synthesizer.sample(num_rows=data.shape[0])

    # Сохранение примера данных
    # sample_data = synthetic_data.head(10).to_dict(orient='records')
    # sample_data_json = json.dumps(sample_data, default=str)
    
    # Сохранение примера сгенерированных данных
    folder_path = os.path.join('generators', str(generator.generator_id))
    dataset_location=os.path.join(folder_path, 'sample_synthetic_data.csv')
    synthetic_data.head(5).to_csv(dataset_location, index=False)
    
    model_location = os.path.join('generators', str(generator.generator_id), 'model.pkl')
    synthesizer.save(filepath=model_location)
    # Обновляем model_location
    generator.model_location = model_location
    generator.model_training_status = {
        'is_fetched_data': True,
        'is_model_trained': True,
        'is_report_generated': False,
        'column_shapes_score': None,
        'column_pair_trends_score': None,
        # 'sample_data': sample_data_json
        # 'column_pair_trends': column_pair_trends_score[['Column 1', 'Column 2', 'Score']].to_dict(orient='records')
    }
    session.commit() # Сохраняем изменения в БД

    ########### 3. Оцениваем качество генерации
    # Оценка качества модели
    quality_report = evaluate_quality(
        real_data=data,
        synthetic_data=synthetic_data,
        metadata=metadata)
        
    column_shapes_score = quality_report.get_details(property_name='Column Shapes')
    average_column_shapes_score = round(column_shapes_score['Score'].mean(), 4)
    column_pair_trends_score = quality_report.get_details(property_name='Column Pair Trends')
    average_column_pair_trends_score = round(column_pair_trends_score['Score'].mean(), 4)

    generator.model_training_status = {
        'is_fetched_data': True,
        'is_model_trained': True,
        'is_report_generated': True,
        'column_shapes_score': average_column_shapes_score,
        'column_pair_trends_score': average_column_pair_trends_score
        # 'sample_data': sample_data_json
        # 'column_pair_trends': column_pair_trends_score[['Column 1', 'Column 2', 'Score']].to_dict(orient='records')
    }
    session.commit() # Сохраняем изменения в БД
    
    # Формирование отчета
    get_data_report(generator, synthetic_data, data, folder_path, quality_report)

    print('Модель обучена и сохранена по пути:', model_location)

    # synthetic_data.to_excel('synthetic_data.xlsx', index=False)

# Сгенерировать наборы данных
def generate_data(generator, num_variants, num_records, add_report=False):
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
        # Если тип данных в metadata = "numerical digital", то округлить значения соответствующего столбца
        for column in generator.dataset_metadata['columns']:
            if generator.dataset_metadata['columns'][column]['sdtype'] == 'numerical digital' and synthetic_data[column].dtype == 'float64':
                synthetic_data[column] = synthetic_data[column].round().astype(int)

        dataset_location=os.path.join(dataset_folder, f'synthetic_data{i}.csv')
        synthetic_data.to_csv(dataset_location, index=False)

    # Пересохранение модели после генерации данных (чтобы seed всегда был новый, т.к. модель его обновляет после каждого вызова sample())
    synthesizer.save(filepath=generator.model_location)

    # Формирование отчета о данных
    synthetic_data = synthesizer.sample(num_rows=num_records)
    real_data = read_csv(generator)
    if add_report:
        get_data_report(generator, synthetic_data, real_data, dataset_folder)


    # Создание архива со сгенерированными данными и отчетом
    arhive_location = os.path.join(dataset_folder, 'synthetic_data.zip') # {generator.name}_
    with zipfile.ZipFile(arhive_location, 'w') as zipf:
        for i in range(num_variants):
            file_path = os.path.join(dataset_folder, f'synthetic_data{i}.csv')
            zipf.write(file_path, arcname=os.path.join('datasets', f'synthetic_data{i}.csv'))
            os.remove(file_path)  # Удаление файла после добавления в архив

        # Добавление отчета в архив
        if add_report:
            report_path = os.path.join(dataset_folder, 'model-report.html')
            zipf.write(report_path, arcname='model-report.html')
            os.remove(report_path) 

def get_data_report(generator, synthetic_data, real_data, folder_path, quality_report = None):
    metadata = get_metadata_for_sdv(generator.dataset_metadata)

    # Создать пустой список для хранения HTML-строк каждого графика
    html_strings = []

    # Добавить заголовок и общую информацию перед графиками
    html_strings.append(f'<h1 style="text-align:center;">Отчет о данных для генератора "{generator.name}"</h1>')
    html_strings.append('<h2 style="text-align:center;">Общая информация</h2>')
    html_strings.append(f'<p style="text-align:center;">Строк в исходном датасете: {len(real_data)}</p>')
    html_strings.append(f'<p style="text-align:center;">Строк в сгенерированном датасете: {len(synthetic_data)}</p>')
    html_strings.append(f'<p style="text-align:center;">Столбцов: {len(synthetic_data.columns)}</p>')
    
    html_strings.append('<hr>')
    html_strings.append('<h2 style="text-align:center;">Корреляция</h2>')
    html_strings.append('<p style="text-align:center;">Матрица показывает, насколько хорошо синтетические данные воспроизводят связи между признаками по сравнению с реальными данными</p>')
    
    if quality_report is None:
        quality_report = evaluate_quality(real_data=real_data, synthetic_data=synthetic_data, metadata=metadata)
    
    pair_trends = quality_report.get_details(property_name='Column Pair Trends')
    # Преобразование данных в формат матрицы
    pair_trends_matrix = pair_trends.pivot(index="Column 1", columns="Column 2", values="Score")
    # Добавление обратных корреляций для симметричной матрицы
    pair_trends_matrix = pair_trends_matrix.combine_first(pair_trends_matrix.T)
    # Заполнение диагонали единицами (корреляция каждого элемента с самим собой)
    for col in pair_trends_matrix.columns:
        pair_trends_matrix.at[col, col] = 1.0

    fig_corr = go.Figure(data=go.Heatmap(
        z=pair_trends_matrix.values,
        x=pair_trends_matrix.columns,
        y=pair_trends_matrix.index,
        colorscale='Viridis',
        zmin=0,
        zmax=1
    ))
    # fig_corr.update_layout(title='Матрица корреляции')
    html_string = pio.to_html(fig_corr, full_html=False)
    html_strings.append(html_string)
    
    html_strings.append('<hr>')
    html_strings.append('<h2 style="text-align:center;">Распределение признаков</h2>')

    # Создать графики распределения для каждого столбца
    for variable in synthetic_data.columns:
        fig = get_column_plot(
            real_data=real_data,
            synthetic_data=synthetic_data,
            metadata=metadata,
            column_name=variable
        )
        # Обновить макет, чтобы показать оба графика наложенными
        fig.update_layout(
            barmode='overlay', 
            title={
                'text': variable,
                'x': 0.4,
                'xanchor': 'center',
                'yanchor': 'top'
            }
        )
        # Сохранить график в HTML-строку и добавить его в список
        html_string = pio.to_html(fig, full_html=False)
        html_strings.append(html_string)
    
    # Объединить все HTML-строки в одну и сохранить в файл
    data_report_location = os.path.join(folder_path, 'model-report.html')
    with open(data_report_location, 'w', encoding='utf-8') as f:
        f.write(''.join(html_strings))
