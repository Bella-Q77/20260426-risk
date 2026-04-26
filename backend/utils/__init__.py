import os
import json
import uuid
from datetime import datetime
import config

def allowed_file(filename, file_type):
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    allowed_exts = config.ALLOWED_EXTENSIONS.get(file_type, set())
    return ext in allowed_exts

def generate_project_id():
    return f"proj_{uuid.uuid4().hex[:8]}"

def generate_document_id():
    return f"doc_{uuid.uuid4().hex[:6]}"

def save_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)

def load_json(file_path, default=None):
    if not os.path.exists(file_path):
        return default
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return default

def get_file_size(file_path):
    if os.path.exists(file_path):
        size_bytes = os.path.getsize(file_path)
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
    return "0 B"

def format_timestamp(timestamp_str):
    try:
        dt = datetime.fromisoformat(timestamp_str)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return timestamp_str

def safe_serialize(obj):
    if isinstance(obj, (dict, list, str, int, float, bool, type(None))):
        return obj
    elif hasattr(obj, '__dict__'):
        return str(obj)
    else:
        return str(obj)
