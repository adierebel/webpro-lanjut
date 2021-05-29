from app import app, db
from flask import g, session, render_template

#
# Middleware
#

@app.before_request
def before_request():
	# Nilai default
	g.user_login = False

	# Dapatkan sesi user
	user_token_session = None
	if "user_token" in session:
		user_token_session = session["user_token"]

	# Periksa apakah user ada dan valid
	if user_token_session:
		cursor = db.connection.cursor()
		cursor.execute("SELECT id, email, nama_lengkap FROM tbl_user WHERE `id`=%s", (user_token_session,))
		user_result = cursor.fetchone()
		if user_result:
			# Set data user ke global object
			g.user_login	= True
			g.user_id		= str(user_result.get("id") or "")
			g.user_email	= str(user_result.get("email") or "")
			g.user_nama		= str(user_result.get("nama_lengkap") or "")

@app.after_request
def after_request(response):
	return response

@app.context_processor
def context_processor():
	# User
	if g.user_login:
		user_data = {
			"id": g.user_id,
			"email": g.user_email,
			"nama": g.user_nama
		}
	else:
		user_data = {}

	return {
		"data": {},
		"user": user_data
	}

#
# HTTP error handler
#

@app.errorhandler(400)
def bad_request(e):
	return render_template("error.html", title="Bad Request", message=str(e)), 400

@app.errorhandler(401)
def unauthorized(e):
	return render_template("error.html", title="Unauthorized", message=str(e)), 401

@app.errorhandler(403)
def access_forbidden(e):
	return render_template("error.html", title="Forbidden", message=str(e)), 403

@app.errorhandler(404)
def not_found(e):
	return render_template("error.html", title="Page Not Found", message=str(e)), 404

@app.errorhandler(413)
def payload_too_large(e):
	return render_template("error.html", title="Payload Too Large", message=str(e)), 413

@app.errorhandler(500)
def internal_error(e):
	return render_template("error.html", title="Internal Server Error", message=str(e)), 500

@app.errorhandler(501)
def not_implemented(e):
	return render_template("error.html", title="Not Implemented", message=str(e)), 501
