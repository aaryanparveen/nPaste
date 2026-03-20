import os

import uvicorn
from uvicorn.middleware.wsgi import WSGIMiddleware

from app import create_app

flask_app = create_app()
app = WSGIMiddleware(flask_app)

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '5000'))
    reload_enabled = os.getenv('UVICORN_RELOAD', 'true').strip().lower() in {
        '1',
        'true',
        'yes',
        'on',
    }
    uvicorn.run('run:app', host=host, port=port, reload=reload_enabled)
