from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    ip_address = db.Column(db.String(45))
    pastes = db.relationship('Paste', backref='author', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

                            
paste_tags = db.Table('paste_tags',
    db.Column('paste_id', db.Integer, db.ForeignKey('paste.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f'<Tag {self.name}>'

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    paste_id = db.Column(db.Integer, db.ForeignKey('paste.id'), nullable=False)
    ip_address = db.Column(db.String(45))
    
                   
    author = db.relationship('User', backref='comments')

class Paste(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    custom_id = db.Column(db.String(7), unique=True, nullable=False)
    title = db.Column(db.String(100), nullable=True)
    content = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(20), nullable=False, default='text')
    filename = db.Column(db.String(100), nullable=True)                 
    is_public = db.Column(db.Boolean, default=True)
    password_hash = db.Column(db.String(128), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    views = db.Column(db.Integer, default=0)
    ip_address = db.Column(db.String(45))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)                     
    
                   
    tags = db.relationship('Tag', secondary=paste_tags, lazy='subquery',
        backref=db.backref('pastes', lazy=True))
    comments = db.relationship('Comment', backref='paste', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        if password:
            self.password_hash = generate_password_hash(password)
        else:
            self.password_hash = None

    def check_password(self, password):
        if not self.password_hash:
            return True
        return check_password_hash(self.password_hash, password)

class SiteSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lockdown_mode = db.Column(db.Boolean, default=False)                       
    panic_mode = db.Column(db.Boolean, default=False)                       

    @staticmethod
    def get_instance():
        settings = SiteSettings.query.first()
        if not settings:
            settings = SiteSettings()
            db.session.add(settings)
            db.session.commit()
        return settings
