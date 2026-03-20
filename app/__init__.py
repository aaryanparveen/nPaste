import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])


def _build_runtime_config():
    database_url = f"sqlite:///{(BASE_DIR / 'site.db').as_posix()}"

    upload_folder_raw = os.getenv('UPLOAD_FOLDER', '').strip()
    if upload_folder_raw:
        upload_folder = Path(upload_folder_raw)
        if not upload_folder.is_absolute():
            upload_folder = BASE_DIR / upload_folder
    else:
        upload_folder = BASE_DIR / 'app' / 'static' / 'uploads'

    try:
        max_content_length = int(os.getenv('MAX_CONTENT_LENGTH', str(25 * 1024 * 1024)))
    except ValueError:
        max_content_length = 25 * 1024 * 1024

    return {
        'SECRET_KEY': os.getenv('SECRET_KEY', 'changeme'),
        'SQLALCHEMY_DATABASE_URI': database_url,
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'UPLOAD_FOLDER': str(upload_folder),
        'MAX_CONTENT_LENGTH': max_content_length,
    }


def create_app():
    app = Flask(__name__)
    app.config.update(_build_runtime_config())

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

                                 
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

                         
    from app.routes import main as main_blueprint
    from app.auth import auth as auth_blueprint
    from app.api import api as api_bp
    
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(api_bp, url_prefix='/api')
    
                                                                     
    @app.context_processor
    def inject_globals():
        import random
        from datetime import datetime, timedelta
        
        def generate_balanced_layout():
                                                         
                            
                                                
                                  
            deck = [
                                 
                ('bento-grey-dark', 'big-box'), 
                ('bento-red-clay', 'big-box'),                                  
                
                                  
                ('bento-red', 'span-2'), 
                ('bento-grey-dark', 'span-2'),
                ('bento-red-faded', 'span-2'), 
                
                                  
                ('bento-grey', 'row-2'), 
                ('bento-grey-light', 'row-2'),
                ('bento-red-deep', 'row-2'),
                
                                   
                ('bento-grey', ''), 
                ('bento-red-faded', ''), 
                ('bento-grey-light', ''), 
                ('bento-red-clay', '')                                  
            ]
            
                                                                      
                                                                   
            best_deck = None
            min_score = float('inf')
            
                                                                   
            for _ in range(200):
                random.shuffle(deck)
                score = 0
                
                for i in range(len(deck) - 1):
                    item1_class, item1_dim = deck[i]
                    item2_class, item2_dim = deck[i+1]
                    
                                                                      
                                                         
                    if item1_class == item2_class:
                        score += 50
                        
                                                                 
                                                                    
                    c1 = item1_class.split('-')[1]                      
                    c2 = item2_class.split('-')[1]
                    if c1 == c2:
                        score += 5 
                        
                                                               
                                                   
                    if item1_dim == item2_dim:
                        score += 2
                        
                if score < min_score:
                    min_score = score
                    best_deck = list(deck)            
                    
                if min_score == 0:                                           
                    break
                    
            return best_deck if best_deck else deck

        return dict(random=random, datetime=datetime, timedelta=timedelta, generate_balanced_layout=generate_balanced_layout)

                            
    from datetime import datetime, timedelta
    
    def to_ist(dt):
        if dt is None:
            return ""
        return dt + timedelta(hours=5, minutes=30)

    def format_datetime(value, format='%Y-%m-%d %H:%M'):
        if value is None:
            return ""
        return value.strftime(format)

    app.jinja_env.filters['to_ist'] = to_ist
    app.jinja_env.filters['strftime'] = format_datetime

                                                                              
    with app.app_context():
        try:
            db.create_all()
                                                
            from app.models import SiteSettings
            SiteSettings.get_instance()
            
                                                                      
            from sqlalchemy import text
            with db.engine.connect() as conn:
                try:
                                                           
                    result = conn.execute(text("PRAGMA table_info(comment)")).fetchall()
                    columns = [row[1] for row in result]
                    if 'ip_address' not in columns:
                        conn.execute(text("ALTER TABLE comment ADD COLUMN ip_address VARCHAR(45)"))
                        conn.commit()
                        print("Migrated: Added ip_address to comment table.")
                except Exception as e:
                    print(f"Migration warning: {e}")

        except Exception as e:
            pass                                                      

    return app
