# Init custom v1 endpoints
from .stip.process import bp as process_bp
from .stip.upload import bp as upload_bp
from .stip.store import bp as store_bp
from .hello import bp as hello_bp


def init_endpoints(app):
    app.register_blueprint(process_bp, url_prefix="/v1")
    app.register_blueprint(upload_bp, url_prefix="/v1")
    app.register_blueprint(store_bp, url_prefix="/v1")
    app.register_blueprint(hello_bp, url_prefix="/v1")
