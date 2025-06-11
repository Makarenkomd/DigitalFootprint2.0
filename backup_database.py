import shutil
import os
from datetime import datetime, timedelta

# Исходный файл
source_file = 'db/database.db'

# Путь к целевой папке
destination_folder = 'backups_of_database'

# Формирование нового имени файла с датой и временем в формате МСК
current_time_msk = datetime.utcnow() + timedelta(hours=3)  # Текущее время в МСК (UTC+3)
time_str = current_time_msk.strftime("%Y-%m-%d_%H-%M-%S")  # Формат: ГГГГ-ММ-ДД_ЧЧ-ММ-СС
new_file_name = f'backup_database_{time_str}.db'

# Полный путь для нового файла
destination_file = os.path.join(destination_folder, new_file_name)

# Проверяем, существует ли целевая папка, и создаём её, если нет
if not os.path.exists(destination_folder):
    os.makedirs(destination_folder)

# Копирование файла
try:
    shutil.copy(source_file, destination_file)
    print(f"Файл успешно скопирован как {destination_file}")
except FileNotFoundError:
    print("Указанный исходный файл не найден.")
except PermissionError:
    print("Недостаточно прав для выполнения операции.")
except Exception as e:
    print(f"Произошла ошибка: {e}")