from sdv.metadata import SingleTableMetadata
from sdv.single_table import GaussianCopulaSynthesizer
import pandas as pd

def get_metadata(dataset_location):
    metadata = SingleTableMetadata()
    metadata.detect_from_csv(filepath=dataset_location)
    # Предобработка метаданных
    data = pd.read_csv(dataset_location)
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
                print('Найден числовой столбец:', column, 'с типом в метаданных:', metadata.columns[column]['sdtype'], 'и типом в данных:', data[column].dtype)
                metadata.columns[column]['sdtype'] = 'numerical'
            else:
                print('Найден категориальный столбец:', column, 'с типом в метаданных:', metadata.columns[column]['sdtype'], 'и типом в данных:', data[column].dtype)
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