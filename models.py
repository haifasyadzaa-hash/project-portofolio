from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    """Akun admin untuk login ke dashboard."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Project(db.Model):
    """Data proyek/karya yang ditampilkan di halaman Portofolio."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    technologies = db.Column(db.String(200))  # disimpan sebagai string, dipisah koma
    image_file = db.Column(db.String(120), default='default.jpg')
    github_link = db.Column(db.String(200))
    live_link = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def tech_list(self):
        if not self.technologies:
            return []
        return [t.strip() for t in self.technologies.split(',') if t.strip()]


class Message(db.Model):
    """Pesan yang dikirim pengunjung melalui form kontak."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Profile(db.Model):
    """Data profil pemilik portofolio (hanya ada 1 baris)."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), default='Nama Anda')
    headline = db.Column(db.String(200), default='Web Developer')
    about = db.Column(db.Text, default='Tuliskan deskripsi tentang diri Anda di sini.')
    education = db.Column(db.Text, default='')
    photo_file = db.Column(db.String(500), default='default-profile.jpg')
    email = db.Column(db.String(120), default='email@example.com')
    github_url = db.Column(db.String(200), default='')
    linkedin_url = db.Column(db.String(200), default='')


class Skill(db.Model):
    """Daftar skill/keahlian yang ditampilkan di halaman About."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
