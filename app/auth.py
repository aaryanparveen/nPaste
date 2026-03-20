from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_user, current_user, logout_user, login_required
from app import db, limiter
from app.models import User, Paste, Comment, SiteSettings
from app.forms import RegistrationForm, LoginForm
from werkzeug.security import generate_password_hash
import os

auth = Blueprint('auth', __name__)


def _get_or_create_admin_from_env(login_email, login_password, ip_address):
    admin_email = os.getenv('ADMIN_EMAIL', '').strip().lower()
    admin_password = os.getenv('ADMIN_PASSWORD', '').strip()
    admin_username = os.getenv('ADMIN_USERNAME', 'admin').strip() or 'admin'

    if not admin_email or not admin_password:
        return None

    if login_email.strip().lower() != admin_email or login_password != admin_password:
        return None

    user = User.query.filter_by(email=admin_email).first()
    if not user:
        candidate_username = admin_username
        suffix = 1
        while User.query.filter_by(username=candidate_username).first():
            candidate_username = f"{admin_username}{suffix}"
            suffix += 1

        user = User(
            username=candidate_username,
            email=admin_email,
            is_admin=True,
            ip_address=ip_address,
        )
        user.set_password(admin_password)
        db.session.add(user)
        db.session.commit()
        return user

    updated = False
    if not user.is_admin:
        user.is_admin = True
        updated = True
    if not user.check_password(admin_password):
        user.set_password(admin_password)
        updated = True
    if updated:
        db.session.commit()

    return user

@auth.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per 10 minutes")
def register():
                      
    from app.models import SiteSettings
    settings = SiteSettings.get_instance()
    if settings.panic_mode:
        flash('New registrations are currently disabled.', 'danger')
        return redirect(url_for('auth.login'))

    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password, ip_address=request.remote_addr)
        db.session.add(user)
        db.session.commit()
        flash('You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', title='Register', form=form)

@auth.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()

    if request.method == 'POST':
        admin_user = _get_or_create_admin_from_env(
            form.email.data or '',
            form.password.data or '',
            request.remote_addr,
        )
        if admin_user:
            login_user(admin_user, remember=True)
            return redirect(url_for('auth.admin_dashboard'))

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@auth.route('/profile')
@login_required
def profile():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q')
    
    query = Paste.query.filter_by(author=current_user)
    
    if search_query:
        search = f"%{search_query}%"
        query = query.filter(
            (Paste.title.ilike(search)) | 
            (Paste.language.ilike(search)) |
            (Paste.content.ilike(search) & (Paste.password_hash == None))
        )
        
    pastes = query.order_by(Paste.created_at.desc()).paginate(page=page, per_page=20)
    
                                                
    from datetime import datetime, timedelta
    return render_template('profile.html', title='Your Profile', pastes=pastes, search_query=search_query, timedelta=timedelta)

@auth.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        abort(403)
    
                            
    if request.method == 'POST' and 'toggle_setting' in request.form:
        settings = SiteSettings.get_instance()
        setting_name = request.form.get('toggle_setting')
        if setting_name == 'lockdown':
            settings.lockdown_mode = not settings.lockdown_mode
            flash(f'Lockdown Mode {"Enabled" if settings.lockdown_mode else "Disabled"}', 'warning')
        elif setting_name == 'panic':
            settings.panic_mode = not settings.panic_mode
            flash(f'Panic Mode {"Enabled" if settings.panic_mode else "Disabled"}', 'danger')
        db.session.commit()
        return redirect(url_for('auth.admin_dashboard'))

    users = User.query.all()
    pastes = Paste.query.order_by(Paste.created_at.desc()).all()
    comments = Comment.query.order_by(Comment.created_at.desc()).all()
    settings = SiteSettings.get_instance()
    
    return render_template('admin.html', title='Admin Dashboard', users=users, pastes=pastes, comments=comments, settings=settings)

@auth.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        abort(403)
    
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Cannot delete yourself!', 'danger')
        return redirect(url_for('auth.admin_dashboard'))
        
                                     
    Paste.query.filter_by(user_id=user.id).delete()
    Comment.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.username} nuked.', 'success')
    return redirect(url_for('auth.admin_dashboard'))

@auth.route('/admin/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment_admin(comment_id):
    if not current_user.is_admin:
        abort(403)
        
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted.', 'success')
    return redirect(url_for('auth.admin_dashboard'))

@auth.route('/admin/delete/<int:paste_id>', methods=['POST'])
@login_required
def delete_paste(paste_id):
    print(f"DEBUG: Delete requested for {paste_id}")
    if not current_user.is_admin:
        print("DEBUG: Access denied - not admin")
        abort(403)
    paste = Paste.query.get_or_404(paste_id)
    try:
        if paste.filename:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], paste.filename)
            if os.path.exists(file_path):
                os.remove(file_path)
    except Exception as e:
        print(f"Error deleting file: {e}")
    db.session.delete(paste)
    db.session.commit()
    print("DEBUG: Paste deleted successfully")
    flash('Paste has been deleted.', 'success')
    return redirect(url_for('auth.admin_dashboard'))

@auth.route('/admin/nuke', methods=['POST'])
@login_required
def nuke_everything():
    print("DEBUG: NUKE requested")
    if not current_user.is_admin:
        print("DEBUG: Access denied - not admin")
        abort(403)
    
                                       
    try:
        folder = current_app.config['UPLOAD_FOLDER']
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
    except Exception as e:
        print(f"Error clearing upload folder: {e}")

                       
    Paste.query.delete()
    db.session.commit()
    
    flash('All pastes and files have been nuked.', 'success')
    return redirect(url_for('auth.admin_dashboard'))

@auth.route("/admin/user/<int:user_id>")
@login_required
def admin_user_detail(user_id):
    if not current_user.is_admin:
        abort(403)
    user = User.query.get_or_404(user_id)
    return render_template('admin_user.html', user=user, title=f"Admin: {user.username}")

@auth.route("/admin/user/<int:user_id>/nuke", methods=['POST'])
@login_required
def admin_nuke_user(user_id):
    if not current_user.is_admin:
        abort(403)
    user = User.query.get_or_404(user_id)
    
                       
    for paste in user.pastes:
                               
        if paste.filename:
            try:
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], paste.filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass
        db.session.delete(paste)
        
    db.session.commit()
    flash(f"Nuked all pastes for user {user.username}", 'success')
    return redirect(url_for('auth.admin_user_detail', user_id=user.id))

@auth.route("/admin/user/<int:user_id>/reset_password", methods=['POST'])
@login_required
def admin_reset_password(user_id):
    if not current_user.is_admin:
        abort(403)
    user = User.query.get_or_404(user_id)
    new_pass = request.form.get('new_password')
    
    if new_pass:
        user.password_hash = generate_password_hash(new_pass)
        db.session.commit()
        flash(f"Password reset for {user.username}", 'success')
    
    return redirect(url_for('auth.admin_user_detail', user_id=user.id))
