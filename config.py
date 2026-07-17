import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

try:
    os.makedirs(os.path.join(BASE_DIR, 'static', 'uploads'), exist_ok=True)
except OSError:
    pass


def _normalize_db_url(url: str) -> str:
    if url and url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql://', 1)
    return url


class Config:
    # Ganti nilai ini dengan string acak yang kuat sebelum deploy ke production
    SECRET_KEY = os.environ.get('SECRET_KEY', 'ganti-dengan-kunci-rahasia-anda')

    _database_url = os.environ.get('DATABASE_URL')
    if _database_url:
        SQLALCHEMY_DATABASE_URI = _normalize_db_url(_database_url)
    else:
        DB_PATH = os.path.join(BASE_DIR, 'portfolio.db')
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DB_PATH.replace('\\', '/')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # Batas upload 5 MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    SUPABASE_BUCKET = os.environ.get('SUPABASE_BUCKET', 'uploads')

    DEFAULT_ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'Syadza Haifa')
    DEFAULT_ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'Haifasyadzaa110107')
