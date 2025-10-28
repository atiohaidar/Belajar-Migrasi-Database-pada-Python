from flask import Flask  # impor kelas inti aplikasi web Flask
from flask_sqlalchemy import SQLAlchemy  # impor ORM yang terintegrasi dengan Flask
from flask_migrate import Migrate  # impor helper migrasi berbasis Alembic

# buat instance aplikasi Flask dan jadikan modul ini sebagai titik masuk
app = Flask(__name__)
# atur koneksi database: gunakan SQLite lokal bernama db.sqlite3
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

# inisialisasi objek ORM SQLAlchemy yang terhubung ke aplikasi
db = SQLAlchemy(app)
# daftarkan Flask-Migrate agar perintah migrasi CLI bisa berjalan
migrate = Migrate(app, db)


class User(db.Model):
    """Model tabel user dengan kolom id, name, dan email."""

    # Penting: mewarisi db.Model agar SQLAlchemy/Alembic mengenali kelas ini sebagai tabel
    # db.Column menerima tipe data dan opsi (mis. primary_key) untuk mendeskripsikan kolom tabel
    id = db.Column(db.Integer, primary_key=True)  # primary key unik pengguna
    name = db.Column(db.String(50))  # nama pengguna maksimal 50 karakter
    email = db.Column(db.String(50))  # email pengguna maksimal 50 karakter


class Ruangan(db.Model):
    """Model tabel ruangan dengan kolom id dan name."""

    # semua kolom di bawah ini juga memakai db.Column dengan parameter tipe dan konfigurasi tambahan
    id = db.Column(db.Integer, primary_key=True)  # primary key ruang
    name = db.Column(db.String(50))  # nama ruangan


class RuanganUser(db.Model):
    """Tabel relasi banyak-ke-banyak antara user dan ruangan."""

    # db.Column digunakan untuk mendefinisikan kolom tabel dengan tipe data dan opsi tambahan
    # db.Model digunakan sebagai dasar untuk mendefinisikan model tabel
    id = db.Column(db.Integer, primary_key=True)  # primary key relasi
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # referensi ke user
    ruangan_id = db.Column(db.Integer, db.ForeignKey('ruangan.id'))  # referensi ke ruangan