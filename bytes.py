from io import BytesIO
from PIL import Image


def image_to_bytes(image_path, format='JPEG'):
    """
    Конвертирует изображение в байты

    :param image_path: Путь к файлу изображения или файловый объект
    :param format: Формат изображения (JPEG, PNG и т.д.)
    :return: Байтовое представление изображения
    """
    try:
        # Открываем изображение с помощью Pillow
        with Image.open(image_path) as img:
            # Конвертируем в RGB, если это PNG с прозрачностью
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')

            # Создаем байтовый поток
            byte_io = BytesIO()

            # Сохраняем изображение в байтовый поток
            img.save(byte_io, format=format)

            # Получаем байты
            byte_data = byte_io.getvalue()

            return byte_data

    except Exception as e:
        print(f"Ошибка при конвертации изображения: {e}")
        return None