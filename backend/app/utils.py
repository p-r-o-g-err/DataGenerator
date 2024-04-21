import csv
import io

# Преобразование CSV в Bytea
def csv_to_bytea(csv_file_path):
    with open(csv_file_path, 'r') as csv_file:
        bytea_data = io.BytesIO(csv_file.read().encode())
    return bytea_data

# Преобразование Bytea обратно в CSV
def bytea_to_csv(bytea_data, csv_file_path):
    csv_data = bytea_data.getvalue().decode()
    with open(csv_file_path, 'w') as csv_file:
        csv_file.write(csv_data)