from io import BytesIO
from PIL import Image


def image_to_bytes(image_path, format='JPEG'):
    try:
        with Image.open(image_path) as img:
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')

            byte_io = BytesIO()

            img.save(byte_io, format=format)

            byte_data = byte_io.getvalue()

            return byte_data

    except Exception as e:
        print(f"Ошибка при конвертации изображения: {e}")
        return None