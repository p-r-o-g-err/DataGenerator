import csv
import io

# # Преобразование CSV в Bytea
# def csv_to_bytea(csv_file_path):
#     with open(csv_file_path, 'r') as csv_file:
#         bytea_data = io.BytesIO(csv_file.read().encode())
#     return bytea_data

# # Преобразование Bytea обратно в CSV
# def bytea_to_csv(bytea_data, csv_file_path):
#     csv_data = bytea_data.getvalue().decode()
#     with open(csv_file_path, 'w') as csv_file:
#         csv_file.write(csv_data)

def transform_metadata(dataset_metadata):
    if 'columns' in dataset_metadata:
        return [{"column_number": i, "name": name, **details} for i, (name, details) in enumerate(dataset_metadata['columns'].items(), start=1)]
    else:
        return []

def transform_metadata_back(metadata_array):
    metadata = {'columns': {}}
    for column in metadata_array:
        metadata['columns'][column['name']] = column
    for column in metadata['columns']:
        metadata['columns'][column].pop('column_number')
        metadata['columns'][column].pop('name')
    return metadata