from app import app, db
from flask import request, abort, url_for, render_template, redirect, session, g, flash
from app.modules.helper import login_required
from datetime import datetime


@app.route("/", methods=["GET", "POST"])
def karyawan_daftar():
	# Data untuk tampilan
	data_tampilan = {
		"title": "Pendaftaran Karyawan"
	}

	# Cursor
	cursor = db.connection.cursor()

	# Handle form ketika di submit
	if request.method == "POST":
		# Dapatkan data dari form
		nomor_induk		= (request.form.get("nomor_induk") or "").strip()
		nama_lengkap	= (request.form.get("nama_lengkap") or "").strip()
		jenis_kelamin	= (request.form.get("jenis_kelamin") or "").strip()
		tempat_lahir	= (request.form.get("tempat_lahir") or "").strip()
		tanggal_lahir	= (request.form.get("tanggal_lahir") or "").strip()
		alamat_lengkap	= (request.form.get("alamat_lengkap") or "").strip()
		nomor_hp		= (request.form.get("nomor_hp") or "").strip()
		alamat_email	= (request.form.get("alamat_email") or "").strip()
		posisi_dilamar	= (request.form.get("posisi_dilamar") or "").strip()
		status			= "Baru"
		tanggal_daftar	= datetime.now().strftime("%Y/%m/%d")

		# Insert
		cursor.execute(
			"""
				INSERT INTO tbl_karyawan (`nomor_induk`, `nama_lengkap`, `jenis_kelamin`, `tempat_lahir`, `tanggal_lahir`, `alamat_lengkap`, `nomor_hp`, `alamat_email`, `posisi_dilamar`, `status`, `tanggal_daftar`)
				VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
			""",
			(nomor_induk, nama_lengkap, jenis_kelamin, tempat_lahir, tanggal_lahir, alamat_lengkap, nomor_hp, alamat_email, posisi_dilamar, status, tanggal_daftar,)
		)
		db.connection.commit()

		# Alihkan ke halaman detail
		flash("Data anda berhasil dikirim, kami akan memeriksa data anda dan mengirim pemberitahuan.", category="sukses")
		return redirect("/")

	# Render tampilan
	return render_template("karyawan/daftar.html", data=data_tampilan)


@app.route("/karyawan/")
@login_required()
def karyawan_index():
	# Data untuk tampilan
	data_tampilan = {
		"title": "Pendaftar",
		"menu": "karyawan"
	}

	# Cursor
	cursor = db.connection.cursor()

	# Ambil data pencarian
	cari = request.args.get('cari', default=None, type=str)
	data_tampilan["cari"] = cari
	if cari:
		cursor.execute("SELECT id, nama_lengkap, nomor_induk, jenis_kelamin, tanggal_lahir, tanggal_daftar, status FROM tbl_karyawan WHERE nama_lengkap LIKE CONCAT('%%', %s, '%%') ORDER BY tanggal_daftar DESC", (cari,))
	else:
		cursor.execute("SELECT id, nama_lengkap, nomor_induk, jenis_kelamin, tanggal_lahir, tanggal_daftar, status FROM tbl_karyawan ORDER BY tanggal_daftar DESC", ())

	# Ambil data karyawan
	karyawan_result = cursor.fetchall()

	# Set data ke tampilan
	data_tampilan["karyawan"] = karyawan_result

	# Render tampilan
	return render_template("karyawan/index.html", data=data_tampilan)


@app.route("/karyawan/detail/<id_>/")
@login_required()
def karyawan_detail(id_):
	# Data untuk tampilan
	data_tampilan = {
		"title": "Detail Pendaftar",
		"menu": "karyawan"
	}

	# Ambil data
	cursor = db.connection.cursor()
	cursor.execute("SELECT * FROM tbl_karyawan WHERE `id`=%s", (id_,))
	karyawan_result = cursor.fetchone()

	# Periksa data karyawan
	if not karyawan_result:
		return abort(404)

	# Handle tindakan hapus
	tindakan = request.args.get('tindakan', default=None, type=str)
	if tindakan == "hapus":
		# Hapus
		cursor.execute("DELETE FROM tbl_karyawan WHERE `id`=%s", (id_,))
		db.connection.commit()
		# Alihkan ke karyawan index
		return redirect(url_for('karyawan_index'))

	# Handle tindakan ubah status
	if tindakan in ['interview', 'diterima', 'ditolak']:
		# Update
		cursor.execute("UPDATE tbl_karyawan SET `status`=%s WHERE `id`=%s", (tindakan.strip().title(), id_,))
		db.connection.commit()
		# Alihkan ke karyawan detail
		return redirect(url_for('karyawan_detail', id_=id_))

	# Set
	data_tampilan["karyawan"] = karyawan_result

	# Render tampilan
	return render_template("karyawan/detail.html", data=data_tampilan)
