from application.logging.logger import get_logger
import os
import hashlib
from application.core.config import Directories


logger = get_logger(__name__)

tmp_dir = os.path.join(Directories.COLLECTION_DIR + "/resource")


def save_uploaded_file(file):
    os.makedirs(tmp_dir, exist_ok=True)
    temp_file_path = None  # Initialize temp_file_path
    try:
        temp_file_path = os.path.join(tmp_dir, hash_value(file.filename))
        # file.seek(0)
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(file.file.read())
    except Exception as e:
        logger.error("Unable to save file: %s", str(e))
    return temp_file_path


def hash_value(data):
    return hashlib.sha256(data.encode("utf-8")).hexdigest()
