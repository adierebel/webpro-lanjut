from app import app, db
from flask import request, abort, url_for, render_template, redirect, session, g, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app.modules.helper import login_required


@app.route("/")
def index():
	return "OK"


@app.route("/admin/user/")
@login_required()
def user_index():
	# Data untuk tampilan
	data_tampilan = {
		"title": "Pengguna",
		"menu": "user"
	}

	# Cursor
	cursor = db.connection.cursor()

	# Ambil data pencarian
	cari = request.args.get('cari', default=None, type=str)
	data_tampilan["cari"] = cari
	if cari:
		cursor.execute("SELECT id, email, nama_lengkap, jenis_kelamin FROM tbl_user WHERE nama_lengkap LIKE CONCAT('%%', %s, '%%') ORDER BY nama_lengkap ASC", (cari,))
	else:
		cursor.execute("SELECT id, email, nama_lengkap, jenis_kelamin FROM tbl_user ORDER BY nama_lengkap ASC", ())

	# Ambil data user
	user_result = cursor.fetchall()

	# Set data ke tampilan
	data_tampilan["users"]		= user_result
	data_tampilan["user_id"]	= g.user_id

	# Render tampilan
	return render_template("user/index.html", data=data_tampilan)


@app.route("/admin/user/editor/", methods=["GET", "POST"], defaults={"id_": None})
@app.route("/admin/user/editor/<id_>/", methods=["GET", "POST"])
@login_required()
def user_editor(id_):
	# Data untuk tampilan
	data_tampilan = {
		"title": "Tambah Pengguna",
		"menu": "user",
		"user": {}
	}

	# Nilai default untuk data user
	user_result = None
	reload_resp = redirect(url_for('user_editor', id_=id_))

	# Cursor
	cursor = db.connection.cursor()

	# Periksa apakah ada nilai pada id_
	if id_:
		# Cari user yang bersangkutan
		cursor.execute("SELECT * FROM tbl_user WHERE `id`=%s", (id_,))
		user_result = cursor.fetchone()
		data_tampilan['user'] = user_result

	# Ubah
	if user_result:
		data_tampilan["title"] = "Ubah Pengguna"

	# Handle form ketika di submit
	if request.method == "POST":
		# Dapatkan data dari form
		email			= (request.form.get("email") or "").strip()
		password		= (request.form.get("password") or "").strip()
		nama_lengkap	= (request.form.get("nama_lengkap") or "").strip()
		jenis_kelamin	= (request.form.get("jenis_kelamin") or "").strip()
		kontak			= (request.form.get("kontak") or "").strip()
		alamat			= (request.form.get("alamat") or "").strip()

		# Periksa apakah semua kolom sudah diisi
		if not nama_lengkap:
			# Tampilkan pesan
			flash("Nama lengkap tidak boleh kosong", category="gagal")
			return reload_resp

		# Periksa apakah user ada
		if user_result:
			# Update data user
			if password:
				cursor.execute(
					"UPDATE tbl_user SET `password`=%s, `nama_lengkap`=%s, `jenis_kelamin`=%s, `kontak`=%s, `alamat`=%s WHERE `id`=%s",
					(generate_password_hash(password), nama_lengkap, jenis_kelamin, kontak, alamat, id_,)
				)
			else:
				cursor.execute(
					"UPDATE tbl_user SET `nama_lengkap`=%s, `jenis_kelamin`=%s, `kontak`=%s, `alamat`=%s WHERE `id`=%s",
					(nama_lengkap, jenis_kelamin, kontak, alamat, id_,)
				)
			db.connection.commit()

			# Alihkan ke halaman detail
			return redirect(url_for('user_detail', id_=id_))

		# Tidak ada user, berarti tambah user
		else:
			# Periksa password
			if not email or not password:
				# Tampilkan pesan
				flash("Email atau password tidak boleh kosong", category="gagal")
				return reload_resp

			# Periksa apakah email sudah dipakai orang lain
			cursor.execute("SELECT id FROM tbl_user WHERE `email`=%s", (email,))
			email_sudah_dipakai = cursor.fetchone()

			# Email sudah dipakai
			if email_sudah_dipakai:
				# Tampilkan pesan
				flash("Alamat email sudah dipakai user lain", category="gagal")
				return reload_resp

			else:
				# Insert
				cursor.execute(
					"INSERT INTO tbl_user (`email`, `password`, `nama_lengkap`, `jenis_kelamin`, `kontak`, `alamat`) VALUES (%s, %s, %s, %s, %s, %s)",
					(email, generate_password_hash(password), nama_lengkap, jenis_kelamin, kontak, alamat,)
				)
				db.connection.commit()
				last_id = cursor.lastrowid

				# Alihkan ke halaman detail
				return redirect(url_for('user_detail', id_=last_id))

	# Render tampilan
	return render_template("user/editor.html", data=data_tampilan)


@app.route("/admin/user/detail/<id_>/")
@login_required()
def user_detail(id_):
	# Data untuk tampilan
	data_tampilan = {
		"title": "Detail Pengguna",
		"menu": "user"
	}

	# Ambil data
	cursor = db.connection.cursor()
	cursor.execute("SELECT * FROM tbl_user WHERE `id`=%s", (id_,))
	user_result = cursor.fetchone()

	# Periksa data user
	if not user_result:
		return abort(404)

	# Handle tindakan hapus
	tindakan = request.args.get('tindakan', default=None, type=str)
	if tindakan == "hapus":
		# Jangin izinkan menghapus diri sendiri
		if str(id_) == (g.user_id):
			# Alihkan ke user index
			return redirect(url_for('user_index'))
		else:
			# Hapus
			cursor.execute("DELETE FROM tbl_user WHERE `id`=%s", (id_,))
			db.connection.commit()
			# Alihkan ke user index
			return redirect(url_for('user_index'))

	# Set
	data_tampilan["user"] = user_result

	# Render tampilan
	return render_template("user/detail.html", data=data_tampilan)


@app.route("/admin/user/pengaturan/", methods=["GET", "POST"])
@login_required()
def user_pengaturan():
	# Data untuk tampilan
	data_tampilan = {
		"title": "Pengaturan",
		"menu": "user"
	}

	# Ambil data
	reload_resp = redirect(url_for('user_pengaturan'))
	user_id = g.user_id
	cursor = db.connection.cursor()
	cursor.execute("SELECT * FROM tbl_user WHERE `id`=%s", (user_id,))
	user_result = cursor.fetchone()
	data_tampilan["user"] = user_result

	# Handle form ketika di submit
	if request.method == "POST":
		# Dapatkan data dari form
		password_old	= (request.form.get("password_old") or "").strip()
		password_new	= (request.form.get("password_new") or "").strip()
		nama_lengkap	= (request.form.get("nama_lengkap") or "").strip()
		jenis_kelamin	= (request.form.get("jenis_kelamin") or "").strip()
		kontak			= (request.form.get("kontak") or "").strip()
		alamat			= (request.form.get("alamat") or "").strip()
		password_hash	= None

		# Periksa kolom
		if not nama_lengkap:
			# Tampilkan pesan
			flash("Nama lengkap tidak boleh kosong", category="gagal")
			return reload_resp

		# Periksa kolom perubahan password
		if password_old:
			# Periksa password baru
			if not password_new:
				# Tampilkan pesan
				flash("Password baru tidak boleh kosong", category="gagal")
				return reload_resp

			# Cocokan password lama
			if check_password_hash(user_result.get("password"), password_old):
				password_hash = generate_password_hash(password_new)
			else:
				# Tampilkan pesan
				flash("Password lama anda tidak cocok", category="gagal")
				return reload_resp

		# Update data ke database
		if password_hash:
			cursor.execute(
				"UPDATE tbl_user SET `password`=%s, `nama_lengkap`=%s, `jenis_kelamin`=%s, `kontak`=%s, `alamat`=%s WHERE `id`=%s",
				(password_hash, nama_lengkap, jenis_kelamin, kontak, alamat, user_id,)
			)
		else:
			cursor.execute(
				"UPDATE tbl_user SET `nama_lengkap`=%s, `jenis_kelamin`=%s, `kontak`=%s, `alamat`=%s WHERE `id`=%s",
				(nama_lengkap, jenis_kelamin, kontak, alamat, user_id,)
			)
		db.connection.commit()

		# Tampilkan pesan
		flash("Berhasil disimpan", category="sukses")

		# Reload halaman
		return reload_resp

	# Render tampilan
	return render_template("user/pengaturan.html", data=data_tampilan)


@app.route("/user/login/", methods=["GET", "POST"])
def user_login():
	# Data untuk tampilan
	data_tampilan = {
		"title": "Masuk"
	}

	# Handle form ketika di submit
	if request.method == "POST":
		# Dapatkan data dari form
		email		= request.form.get("email")
		password	= request.form.get("password")

		# Periksa data
		if email and password:
			# Periksa apakah informasi user valid
			cursor = db.connection.cursor()
			cursor.execute("SELECT id, password FROM tbl_user WHERE `email`=%s", (email,))
			user_result = cursor.fetchone()
			if user_result:
				# Cocokan password
				if check_password_hash(user_result.get("password"), password):
					# Set status user sudah login ke session
					session['user_token'] = str(user_result.get("id"))
					# Alihkan ke halaman utama jika login berhasil
					return redirect(url_for("index"))
				else:
					flash("Password yang anda masukan salah", "gagal")
			else:
				flash("Email tidak ditemukan", "gagal")
		else:
			flash("Email dan password tidak boleh kosong", "gagal")

	# Render tampilan
	return render_template("user/login.html", data=data_tampilan)


@app.route("/user/logout/")
def user_logout():
	# Hapus session
	session.pop('user_token', None)
	# Alihkan ke halaman utama
	return redirect(url_for("index"))


@app.route("/user/init/")
def user_init():
	# init user jika belum ada user dalam database
	cursor = db.connection.cursor()
	cursor.execute("SELECT email FROM tbl_user")
	user_result = cursor.fetchone()

	# Jika tidak ada user, tambahkan baru
	if not user_result:
		# Data
		email			= "admin@email.com"
		password		= generate_password_hash("nimda")
		nama_lengkap	= "Admin"

		# Insert user
		cursor.execute("INSERT INTO tbl_user (`email`, `password`, `nama_lengkap`) VALUES (%s, %s, %s)", (email, password, nama_lengkap,))
		db.connection.commit()

		# Tampilkan pesan
		return "OK: User berhasil ditambahkan"

	else:
		# Tampilkan pesan
		return "SKIP: User sudah ada"
