import os
import json
import requests
import logging

# Настроим логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

class TrainingModel:
    def __init__(self, api_url, json_folder_path):
        """
        Инициализация класса с указанием URL для API и пути к папке с JSON.
        :param api_url: URL для отправки запроса к модели
        :param json_folder_path: Путь к папке с JSON
        """
        self.api_url = api_url  # URL для API (существующий API вашего проекта)
        self.json_folder_path = json_folder_path  # Путь к папке с JSON
        self.json_files = self.load_json_files()  # Загрузка всех JSON файлов

    def load_json_files(self):
        """Загрузка всех JSON файлов из папки"""
        json_files = []
        try:
            # Получаем список всех файлов JSON в папке
            for filename in os.listdir(self.json_folder_path):
                if filename.endswith('.json'):
                    json_files.append(os.path.join(self.json_folder_path, filename))
            logger.info(f"Найдено {len(json_files)} JSON файлов.")
        except Exception as e:
            logger.error(f"Ошибка при загрузке JSON файлов: {e}")
        return json_files

    def prepare_input_string(self, entry):
        """
        Объединяет значения ключей JSON в строку.
        :param entry: объект, который нужно объединить в строку
        :return: строка, содержащая все значения из entry, разделенные пробелами
        """
        input_string = " ".join([str(value) for value in entry.values()])
        return input_string

    def send_to_model(self, input_string):
        """
        Отправка строки в модель через API.
        :param input_string: строка для отправки в модель
        :return: ответ от модели
        """
        try:
            # Отправляем данные на существующий сервер через POST запрос
            response = requests.post(self.api_url, json={"input": input_string})
            response.raise_for_status()  # Проверка на ошибки HTTP
            return response.json()  # Предполагается, что модель возвращает JSON
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при отправке запроса: {e}")
            return None

    def log_response(self, response, filename):
        """
        Логирование ответа модели.
        :param response: ответ от модели
        :param filename: имя файла JSON
        """
        if response:
            logger.info(f"Ответ модели для {filename}: {response}")
        else:
            logger.error(f"Ответ модели для {filename} отсутствует.")

    def process_json_file(self, json_file):
        """
        Обработка одного JSON файла.
        :param json_file: путь к файлу JSON
        """
        try:
            with open(json_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
                logger.info(f"Обработка файла: {json_file}")
                
                for key, entry in data.items():
                    input_string = self.prepare_input_string(entry)
                    logger.info(f"Отправка строки в модель: {input_string}")
                    response = self.send_to_model(input_string)
                    self.log_response(response, json_file)
        except Exception as e:
            logger.error(f"Ошибка при обработке файла {json_file}: {e}")

    def process_all_files(self):
        """Обработка всех файлов в папке"""
        for json_file in self.json_files:
            self.process_json_file(json_file)
