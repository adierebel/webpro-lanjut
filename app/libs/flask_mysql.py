import pymysql
from flask import _app_ctx_stack, current_app

class PyMySQL(object):
	def __init__(self, app=None, prefix=''):
		self.app = app
		self.cfg = {}
		self.prefix = prefix
		self.key = '%spymysql_db' % (self.prefix)
		if app is not None: # pragma: no cover
			self.init_app(app)

	def init_app(self, app):
		# Set config
		app.config.setdefault('%sPYMYSQL_HOST' % (self.prefix), 'localhost')
		app.config.setdefault('%sPYMYSQL_USER' % (self.prefix), None)
		app.config.setdefault('%sPYMYSQL_PASSWORD' % (self.prefix), None)
		app.config.setdefault('%sPYMYSQL_DATABASE' % (self.prefix), None)
		app.config.setdefault('%sPYMYSQL_PORT' % (self.prefix), 3306)
		app.config.setdefault('%sPYMYSQL_UNIX_SOCKET' % (self.prefix), None)
		app.config.setdefault('%sPYMYSQL_CONNECT_TIMEOUT' % (self.prefix), 10)
		app.config.setdefault('%sPYMYSQL_READ_DEFAULT_FILE' % (self.prefix), None)
		app.config.setdefault('%sPYMYSQL_USE_UNICODE' % (self.prefix), True)
		app.config.setdefault('%sPYMYSQL_CHARSET' % (self.prefix), 'utf8')
		app.config.setdefault('%sPYMYSQL_SQL_MODE' % (self.prefix), None)
		app.config.setdefault('%sPYMYSQL_CURSORCLASS' % (self.prefix), pymysql.cursors.DictCursor)

		if hasattr(app, 'teardown_appcontext'):
			app.teardown_appcontext(self.teardown)

	@property
	def connect(self):
		# Loop config
		kwargs = {}
		for k, v in current_app.config.items():
			if k.startswith('%sPYMYSQL_' % (self.prefix)):
				if v:
					key = k.replace("%sPYMYSQL_" % (self.prefix), "").lower()
					kwargs[key] = v
		return pymysql.connect(**kwargs)

	@property
	def connection(self):
		ctx = _app_ctx_stack.top
		if ctx is not None:
			if not hasattr(ctx, self.key):
				setattr(ctx, self.key, self.connect)
			return getattr(ctx, self.key)

	def teardown(self, exception):
		ctx = _app_ctx_stack.top
		if hasattr(ctx, self.key):
			getattr(ctx, self.key).close()
