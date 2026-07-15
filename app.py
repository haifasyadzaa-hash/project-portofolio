import os
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

from config import Config
from models import db, User, Project, Message, Profile, Skill

# Tentukan base directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, 
            template_folder=os.path.join(BASE_DIR, 'templates'),
            static_folder=os.path.join(BASE_DIR, 'static'))
app.config.from_object(Config)

db.init_app(app)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def save_upload(file_storage):
    """Simpan file upload ke folder static/uploads dan kembalikan nama filenya."""
    if file_storage and file_storage.filename and allowed_file(file_storage.filename):
        filename = secure_filename(file_storage.filename)
        # tambahkan prefix agar nama file tidak bentrok
        unique_name = f"{os.urandom(4).hex()}_{filename}"
        file_storage.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_name))
        return unique_name
    return None


def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu.', 'error')
            return redirect(url_for('login'))
        return view_func(*args, **kwargs)
    return wrapped_view


def get_profile():
    profile = Profile.query.first()
    if profile is None:
        profile = Profile()
        db.session.add(profile)
        db.session.commit()
    return profile


# ---------------------------------------------------------------------------
# HALAMAN PUBLIK
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    profile = get_profile()
    projects = Project.query.order_by(Project.created_at.desc()).limit(3).all()
    return render_template('index.html', profile=profile, projects=projects)


@app.route('/about')
def about():
    profile = get_profile()
    skills = Skill.query.all()
    return render_template('about.html', profile=profile, skills=skills)


@app.route('/portfolio')
def portfolio():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('portfolio.html', projects=projects)


@app.route('/portfolio/<int:id>')
def project_detail(id):
    project = Project.query.get_or_404(id)
    return render_template('project_detail.html', project=project)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    profile = get_profile()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        message_text = request.form.get('message', '').strip()

        if not name or not email or not message_text:
            flash('Semua field wajib diisi.', 'error')
            return redirect(url_for('contact'))

        new_message = Message(name=name, email=email, message=message_text)
        db.session.add(new_message)
        db.session.commit()
        flash('Pesan Anda berhasil dikirim. Terima kasih!', 'success')
        return redirect(url_for('contact'))

    return render_template('contact.html', profile=profile)


# ---------------------------------------------------------------------------
# AUTENTIKASI
# ---------------------------------------------------------------------------

@app.route('/dashboard/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login berhasil.', 'success')
            return redirect(url_for('dashboard_index'))

        flash('Username atau password salah.', 'error')

    return render_template('dashboard/login.html')


@app.route('/dashboard/logout')
def logout():
    session.clear()
    flash('Anda telah logout.', 'success')
    return redirect(url_for('login'))


# ---------------------------------------------------------------------------
# DASHBOARD ADMIN
# ---------------------------------------------------------------------------

@app.route('/dashboard')
@login_required
def dashboard_index():
    total_projects = Project.query.count()
    unread_messages = Message.query.filter_by(is_read=False).count()
    return render_template(
        'dashboard/index.html',
        total_projects=total_projects,
        unread_messages=unread_messages,
    )


@app.route('/dashboard/projects')
@login_required
def dashboard_projects():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('dashboard/projects.html', projects=projects)


@app.route('/dashboard/projects/add', methods=['GET', 'POST'])
@login_required
def add_project():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        technologies = request.form.get('technologies', '').strip()
        github_link = request.form.get('github_link', '').strip()
        live_link = request.form.get('live_link', '').strip()
        file = request.files.get('image')

        if not title or not description:
            flash('Judul dan deskripsi wajib diisi.', 'error')
            return redirect(url_for('add_project'))

        img_name = save_upload(file) or 'default.jpg'

        project = Project(
            title=title,
            description=description,
            technologies=technologies,
            image_file=img_name,
            github_link=github_link,
            live_link=live_link,
        )
        db.session.add(project)
        db.session.commit()
        flash('Proyek berhasil ditambahkan.', 'success')
        return redirect(url_for('dashboard_projects'))

    return render_template('dashboard/add_project.html')


@app.route('/dashboard/projects/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_project(id):
    project = Project.query.get_or_404(id)

    if request.method == 'POST':
        project.title = request.form.get('title', '').strip()
        project.description = request.form.get('description', '').strip()
        project.technologies = request.form.get('technologies', '').strip()
        project.github_link = request.form.get('github_link', '').strip()
        project.live_link = request.form.get('live_link', '').strip()

        file = request.files.get('image')
        new_img = save_upload(file)
        if new_img:
            project.image_file = new_img

        db.session.commit()
        flash('Proyek berhasil diperbarui.', 'success')
        return redirect(url_for('dashboard_projects'))

    return render_template('dashboard/edit_project.html', project=project)


@app.route('/dashboard/projects/delete/<int:id>', methods=['POST'])
@login_required
def delete_project(id):
    project = Project.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    flash('Proyek berhasil dihapus.', 'success')
    return redirect(url_for('dashboard_projects'))


@app.route('/dashboard/profile', methods=['GET', 'POST'])
@login_required
def dashboard_profile():
    profile = get_profile()
    skills = Skill.query.all()

    if request.method == 'POST':
        profile.name = request.form.get('name', '').strip()
        profile.headline = request.form.get('headline', '').strip()
        profile.about = request.form.get('about', '').strip()
        profile.education = request.form.get('education', '').strip()
        profile.email = request.form.get('email', '').strip()
        profile.github_url = request.form.get('github_url', '').strip()
        profile.linkedin_url = request.form.get('linkedin_url', '').strip()

        file = request.files.get('photo')
        new_photo = save_upload(file)
        if new_photo:
            profile.photo_file = new_photo

        db.session.commit()
        flash('Profil berhasil diperbarui.', 'success')
        return redirect(url_for('dashboard_profile'))

    return render_template('dashboard/profile.html', profile=profile, skills=skills)


@app.route('/dashboard/profile/skills/add', methods=['POST'])
@login_required
def add_skill():
    name = request.form.get('skill_name', '').strip()
    if name:
        db.session.add(Skill(name=name))
        db.session.commit()
        flash('Skill berhasil ditambahkan.', 'success')
    return redirect(url_for('dashboard_profile'))


@app.route('/dashboard/profile/skills/delete/<int:id>', methods=['POST'])
@login_required
def delete_skill(id):
    skill = Skill.query.get_or_404(id)
    db.session.delete(skill)
    db.session.commit()
    flash('Skill berhasil dihapus.', 'success')
    return redirect(url_for('dashboard_profile'))


@app.route('/dashboard/messages')
@login_required
def dashboard_messages():
    messages = Message.query.order_by(Message.created_at.desc()).all()
    return render_template('dashboard/messages.html', messages=messages)


@app.route('/dashboard/messages/read/<int:id>', methods=['POST'])
@login_required
def mark_message_read(id):
    message = Message.query.get_or_404(id)
    message.is_read = True
    db.session.commit()
    return redirect(url_for('dashboard_messages'))


@app.route('/dashboard/messages/delete/<int:id>', methods=['POST'])
@login_required
def delete_message(id):
    message = Message.query.get_or_404(id)
    db.session.delete(message)
    db.session.commit()
    flash('Pesan berhasil dihapus.', 'success')
    return redirect(url_for('dashboard_messages'))


# ---------------------------------------------------------------------------
# INISIALISASI DATABASE & SEED DATA AWAL
# ---------------------------------------------------------------------------

def seed_initial_data():
    """Membuat akun admin default & profil kosong jika database masih baru."""
    if User.query.count() == 0:
        admin = User(username=app.config['DEFAULT_ADMIN_USERNAME'])
        admin.set_password(app.config['DEFAULT_ADMIN_PASSWORD'])
        db.session.add(admin)

    if Profile.query.count() == 0:
        db.session.add(Profile())

    db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            seed_initial_data()
            print("✓ Database initialized successfully")
        except Exception as e:
            print(f"✗ Error initializing database: {e}")
            import traceback
            traceback.print_exc()
    
    app.run(debug=True)
