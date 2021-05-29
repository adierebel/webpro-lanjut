from app import app
from flask import url_for, redirect, g
from functools import wraps
from re import sub as re_sub

def login_required():
	def decorator(f):
		@wraps(f)
		def decorated(*args, **kwargs):
			try:
				if g.user_login:
					return f(*args, **kwargs)
				else:
					return redirect(url_for('user_login'))
			except Exception as e:
				raise e
		return decorated
	return decorator

def mask_ribuan(value):
	return re_sub(r"\B(?=(?:\d{3})+$)", ".", str(value))

def mask_rupiah(value):
	return "Rp %s,-" % (ribuan(value))

def mask_tanggal(value, singkat=False):
	tanggal_split = (str(value) or "").split("-")
	if len(tanggal_split) < 3:
		return None
	nama_bulan = {
		1: "Januari",
		2: "Februari",
		3: "Maret",
		4: "April",
		5: "Mei",
		6: "Juni",
		7: "Juli",
		8: "Agustus",
		9: "September",
		10: "Oktober",
		11: "November",
		12: "Desember",
	}
	if singkat:
		output = "%s %s %s" % (
				tanggal_split[2],
				(nama_bulan.get(int(tanggal_split[1])) or "Bulan")[:3],
				tanggal_split[0]
			)
	else:
		output = "%s %s %s" % (
				tanggal_split[2],
				(nama_bulan.get(int(tanggal_split[1])) or "Bulan"),
				tanggal_split[0]
			)
	return output

def mask_bulan(value, singkat=False):
	tanggal_split = (str(value) or "").split("-")
	if len(tanggal_split) < 2:
		return None
	nama_bulan = {
		1: "Januari",
		2: "Februari",
		3: "Maret",
		4: "April",
		5: "Mei",
		6: "Juni",
		7: "Juli",
		8: "Agustus",
		9: "September",
		10: "Oktober",
		11: "November",
		12: "Desember",
	}
	if singkat:
		output = "%s %s" % (
				(nama_bulan.get(int(tanggal_split[0])) or "Bulan")[:3],
				tanggal_split[1]
			)
	else:
		output = "%s %s" % (
				(nama_bulan.get(int(tanggal_split[0])) or "Bulan"),
				tanggal_split[1]
			)
	return output

# Register
app.add_template_filter(mask_ribuan, 'ribuan')
app.add_template_filter(mask_rupiah, 'rupiah')
app.add_template_filter(mask_tanggal, 'tanggal')
app.add_template_filter(mask_bulan, 'bulan')
