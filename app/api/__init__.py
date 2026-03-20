from flask import Blueprint, request, jsonify, url_for
from app import db, csrf
from app.models import Paste, Tag
from datetime import datetime, timedelta
import secrets

api = Blueprint('api', __name__)
csrf.exempt(api)

def generate_short_id():
    return secrets.token_urlsafe(5)[:7]

@api.route('/paste', methods=['POST'])
def create_paste():
    data = request.get_json() or {}
    
    content = data.get('content')
    if not content:
        return jsonify({'error': 'Content is required'}), 400
        
    title = data.get('title')
    language = data.get('language', 'text')
    is_private = data.get('private', False)
    
    custom_id = generate_short_id()
    while Paste.query.filter_by(custom_id=custom_id).first():
        custom_id = generate_short_id()
        
            
    expires_at = None
    expiry_input = data.get('expiry')
    if expiry_input:
        time_map = {
            '10m': timedelta(minutes=10),
            '1h': timedelta(hours=1),
            '1d': timedelta(days=1),
            '1w': timedelta(weeks=1),
            '1m': timedelta(days=30)
        }
        if expiry_input in time_map:
            expires_at = datetime.utcnow() + time_map[expiry_input]
            
    paste = Paste(
        custom_id=custom_id,
        title=title,
        content=content,
        language=language,
        is_public=not is_private,
        expires_at=expires_at,
        ip_address=request.remote_addr
    )
    
          
    tags_input = data.get('tags')
    if tags_input:
                                                                
        if isinstance(tags_input, str):
            tag_names = [t.strip().lower() for t in tags_input.split(',') if t.strip()]
        elif isinstance(tags_input, list):
            tag_names = [str(t).strip().lower() for t in tags_input if str(t).strip()]
        else:
            tag_names = []
            
        for name in tag_names:
            tag = Tag.query.filter_by(name=name).first()
            if not tag:
                tag = Tag(name=name)
            paste.tags.append(tag)
            
    db.session.add(paste)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'id': custom_id,
        'url': url_for('main.view_paste', custom_id=custom_id, _external=True),
        'raw_url': url_for('main.raw_paste', custom_id=custom_id, _external=True)
    }), 201

@api.route('/p/<custom_id>', methods=['GET'])
def get_paste(custom_id):
    paste = Paste.query.filter_by(custom_id=custom_id).first_or_404()
    
                                                 
    if paste.password_hash:
        return jsonify({'error': 'Password protected'}), 403
        
    return jsonify({
        'id': paste.custom_id,
        'title': paste.title,
        'content': paste.content,
        'language': paste.language,
        'created_at': paste.created_at.isoformat(),
        'views': paste.views,
        'tags': [t.name for t in paste.tags]
    })

@api.route('/search', methods=['GET'])
def search_pastes():
    query_text = request.args.get('q')
    tag_text = request.args.get('tag')
    
    query = Paste.query.filter_by(is_public=True)
    
    if tag_text:
        query = query.join(Paste.tags).filter(Tag.name == tag_text.lower())
        
    if query_text:
        search = f"%{query_text}%"
        query = query.filter(
            (Paste.title.ilike(search)) | 
            (Paste.language.ilike(search)) |
            (Paste.content.ilike(search) & (Paste.password_hash == None))
        )
        
    pastes = query.order_by(Paste.created_at.desc()).limit(20).all()
    
    results = []
    for paste in pastes:
        results.append({
            'id': paste.custom_id,
            'title': paste.title or 'Untitled',
            'language': paste.language,
            'content': paste.content,
            'url': url_for('main.view_paste', custom_id=paste.custom_id, _external=True),
            'tags': [t.name for t in paste.tags]
        })
        
    return jsonify(results)
