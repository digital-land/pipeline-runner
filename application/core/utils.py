from application.logging.logger import get_logger
import os
import hashlib


logger = get_logger(__name__)

tmp_dir = "collection/resource"


def save_uploaded_file(file):
    try:
        print(file)
        temp_file_path = os.path.join(tmp_dir, file.filename)
        # file.seek(0)
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(file.file.read())
    except Exception as e:
        logger.error("Unable to save file: %s", str(e))
    return temp_file_path


def hash_value(data):
    return hashlib.sha256(data.encode("utf-8")).hexdigest()
