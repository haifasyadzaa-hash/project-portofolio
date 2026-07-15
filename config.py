import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Buat folder uploads jika belum ada
os.makedirs(os.path.join(BASE_DIR, 'static', 'uploads'), exist_ok=True)


class Config:
    # Ganti nilai ini dengan string acak yang kuat sebelum deploy ke production
    SECRET_KEY = os.environ.get('SECRET_KEY', 'ganti-dengan-kunci-rahasia-anda')

    # Database configuration dengan absolute path
    DB_PATH = os.path.join(BASE_DIR, 'portfolio.db')
    # Konversi backslash ke forward slash untuk SQLite compatibility
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DB_PATH.replace('\\', '/')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # Batas upload 5 MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # Akun admin default (dipakai saat seeding database pertama kali)
    DEFAULT_ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'Syadza Haifa')
    DEFAULT_ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'Haifasyadzaa110107')
