from flask import Flask
from app.libs.flask_mysql import PyMySQL
from app.libs.reverse_proxy import ReverseProxied

# Init aplikasi
app = Flask(
	__name__,
	static_url_path	= '/files',
	static_folder	= 'files',
	template_folder	= 'templates'
)

# Muat pengaturan
app.config.from_object('config')

# Proxied
app.wsgi_app = ReverseProxied(app.wsgi_app, app.config)

# Database
db = PyMySQL()
db.init_app(app)

# Import module
from app.modules.middleware import *
from app.modules.karyawan import *
from app.modules.user import *
