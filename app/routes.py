from flask import Blueprint, render_template, url_for, flash, redirect, request, abort, send_from_directory, current_app
from flask_login import current_user, login_required
from app import db, limiter
import secrets
import os
from app.models import Paste, Tag, Comment
from app.forms import PasteForm, PasswordCheckForm, CommentForm
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter

main = Blueprint('main', __name__)

def generate_short_id():
                                            
    return secrets.token_urlsafe(5)[:7]

@main.before_request
def check_lockdown():
    from app.models import SiteSettings
    settings = SiteSettings.get_instance()
    
    if settings.lockdown_mode:
        if not current_user.is_authenticated:
                                                                  
            if request.endpoint and request.endpoint not in ['auth.login', 'static']:
                flash('Site is in Lockdown Mode. Login required.', 'warning')
                return redirect(url_for('auth.login'))

@main.route("/", methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def home():
    form = PasteForm()
                            
    if form.validate_on_submit():
        custom_id = generate_short_id()
        while Paste.query.filter_by(custom_id=custom_id).first():
            custom_id = generate_short_id()
            
        filename = None
        if form.attachment.data:
            file = form.attachment.data
            filename = secrets.token_hex(4) + '_' + file.filename
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        
                          
        from datetime import datetime, timedelta
        expires_at = None
        if form.expiry.data != 'never':
            time_map = {
                '10m': timedelta(minutes=10),
                '1h': timedelta(hours=1),
                '1d': timedelta(days=1),
                '1w': timedelta(weeks=1),
                '1m': timedelta(days=30)
            }
            if form.expiry.data in time_map:
                expires_at = datetime.utcnow() + time_map[form.expiry.data]

        paste = Paste(
            custom_id=custom_id,
            title=form.title.data,
            content=form.content.data,
            language=form.language.data,
            filename=filename,
            is_public=not form.is_private.data,
            expires_at=expires_at,
            ip_address=request.remote_addr,
            author=current_user if current_user.is_authenticated else None
        )
        
                      
        if form.tags.data:
            tag_names = [t.strip().lower() for t in form.tags.data.split(',') if t.strip()]
            for name in tag_names:
                tag = Tag.query.filter_by(name=name).first()
                if not tag:
                    tag = Tag(name=name)
                                                                             
                paste.tags.append(tag)
        
        if form.custom_password.data:
            paste.set_password(form.custom_password.data)
            
        db.session.add(paste)
        db.session.commit()
        flash('Paste created!', 'success')
        return redirect(url_for('main.view_paste', custom_id=custom_id))
    return render_template('index.html', form=form)

@main.route("/browse")
def browse():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q')
    tag_query = request.args.get('tag')
    
    if current_user.is_authenticated and current_user.is_admin:
        query = Paste.query                 
    else:
        query = Paste.query.filter_by(is_public=True)
    
    if tag_query:
        query = query.join(Paste.tags).filter(Tag.name == tag_query.lower())
    
    if search_query:
        search = f"%{search_query}%"
        query = query.filter(
            (Paste.title.ilike(search)) | 
            (Paste.language.ilike(search)) |
            (Paste.content.ilike(search) & (Paste.password_hash == None)) 
        )
        
                                                
    pastes = query.order_by(Paste.created_at.desc()).paginate(page=page, per_page=20)
    from datetime import timedelta
    return render_template('browse.html', pastes=pastes, timedelta=timedelta, search_query=search_query, tag_query=tag_query)

@main.route("/p/<custom_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_paste(custom_id):
    paste = Paste.query.filter_by(custom_id=custom_id).first_or_404()
    if paste.author != current_user:
        abort(403)
        
    form = PasteForm()
    
    if form.validate_on_submit():
        paste.title = form.title.data
        paste.content = form.content.data
        paste.language = form.language.data
        paste.is_public = not form.is_private.data
        
                                                                                
                                                                      
        if form.expiry.data != 'never':
            from datetime import datetime, timedelta
            time_map = {
                '10m': timedelta(minutes=10),
                '1h': timedelta(hours=1),
                '1d': timedelta(days=1),
                '1w': timedelta(weeks=1),
                '1m': timedelta(days=30)
            }
            if form.expiry.data in time_map:
                paste.expires_at = datetime.utcnow() + time_map[form.expiry.data]
        else:
                                                                         
                                                                      
             paste.expires_at = None

        if form.custom_password.data:
             paste.set_password(form.custom_password.data)
             
        db.session.commit()
        flash('Paste updated!', 'success')
        return redirect(url_for('main.view_paste', custom_id=custom_id))
    
                   
    elif request.method == 'GET':
        form.title.data = paste.title
        form.content.data = paste.content
        form.language.data = paste.language
        form.is_private.data = not paste.is_public
        form.submit.label.text = 'Update Paste'
        
    return render_template('index.html', form=form, title='Edit Paste')

@main.route("/p/<custom_id>", methods=['GET', 'POST'])
def view_paste(custom_id):
    paste = Paste.query.filter_by(custom_id=custom_id).first_or_404()
    
                  
    from datetime import datetime
    if paste.expires_at and paste.expires_at < datetime.utcnow():
        db.session.delete(paste)
        db.session.commit()
        abort(404)
        
                            
    paste.views += 1
    db.session.commit()
    
                                             
    form = PasswordCheckForm()
    is_admin = current_user.is_authenticated and current_user.is_admin
    
    if paste.password_hash and not is_admin:
                                              
        if f'unlocked_{custom_id}' not in request.cookies:
            if form.validate_on_submit():
                if paste.check_password(form.password.data):
                                        
                    resp = redirect(url_for('main.view_paste', custom_id=custom_id))
                    resp.set_cookie(f'unlocked_{custom_id}', 'true')
                    return resp
                else:
                    flash('Incorrect password', 'danger')
            return render_template('password.html', form=form, paste=paste)

                  
    comment_form = CommentForm()
    
                         
    try:
        lexer = get_lexer_by_name(paste.language, stripall=True)
    except:
        lexer = get_lexer_by_name('text', stripall=True)
        
    formatter = HtmlFormatter(linenos=True, cssclass="source")
    highlighted_code = highlight(paste.content, lexer, formatter)
    css_style = formatter.get_style_defs('.source')
    
    return render_template('view.html', paste=paste, highlighted_code=highlighted_code, css_style=css_style, comment_form=comment_form)

@main.route("/p/<custom_id>/comment", methods=['POST'])
@login_required
@limiter.limit("20 per hour")
def post_comment(custom_id):
    paste = Paste.query.filter_by(custom_id=custom_id).first_or_404()
    form = CommentForm()
    
    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            user_id=current_user.id,
            paste_id=paste.id,
            ip_address=request.remote_addr
        )
        db.session.add(comment)
        db.session.commit()
        flash('Comment posted!', 'success')
    else:
        flash('Error posting comment.', 'danger')
        
    return redirect(url_for('main.view_paste', custom_id=custom_id))


@main.route("/p/<custom_id>/delete", methods=['POST'])
@login_required
def delete_paste(custom_id):
    paste = Paste.query.filter_by(custom_id=custom_id).first_or_404()
    if not (current_user.is_admin or paste.author == current_user):
        abort(403)
        
    db.session.delete(paste)
    db.session.commit()
    flash('Paste deleted.', 'success')
    return redirect(url_for('main.home'))

@main.route("/comment/<int:comment_id>/delete", methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
                                                             
    if not (current_user.is_admin or comment.author == current_user or comment.paste.author == current_user):
        abort(403)
        
    paste_id = comment.paste.custom_id
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted.', 'success')
    return redirect(url_for('main.view_paste', custom_id=paste_id))

@main.app_errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@main.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@main.route("/raw/<custom_id>")
def raw_paste(custom_id):
    paste = Paste.query.filter_by(custom_id=custom_id).first_or_404()
    
                                                                                   
                                                                                  
    if paste.password_hash:
        return "Password Protected Paste. Please view in browser.", 403
        
    from flask import Response
    return Response(paste.content, mimetype='text/plain')

@main.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
