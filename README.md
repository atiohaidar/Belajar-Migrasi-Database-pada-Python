# Panduan Migrasi Database dengan Flask-Migrate (Alembic)

![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![Flask 3.x](https://img.shields.io/badge/Flask-3.x-000000?logo=flask&logoColor=white)
![Alembic](https://img.shields.io/badge/Alembic-Migrations-4b8bbe)

README ini menjelaskan cara mengelola perubahan skema database di proyek Flask ini menggunakan **Flask-Migrate** (pembungkus Alembic). Semua contoh diperagakan dengan konfigurasi yang ada di `app.py`.@app.py#1-14

## Ringkasan Cepat
1. Pastikan dependensi terpasang dan `FLASK_APP=app.py`.
2. Saat model berubah, jalankan `flask db migrate -m "Pesan"`.
3. Terapkan ke database dengan `flask db upgrade`.

## Daftar Isi
- [1. Gambaran Umum](#1-gambaran-umum)
- [2. Prasyarat](#2-prasyarat)
- [3. Struktur Minimal Aplikasi](#3-struktur-minimal-aplikasi)
- [4. Alur Kerja Migrasi Standar](#4-alur-kerja-migrasi-standar)
- [5. Contoh: Menambah Kolom pada Tabel `users`](#5-contoh-menambah-kolom-pada-tabel-users)
- [6. Contoh: Menghapus Kolom](#6-contoh-menghapus-kolom)
- [7. Menambahkan Data Seed dengan Migrasi](#7-menambahkan-data-seed-dengan-migrasi)
- [8. Perintah Tambahan yang Berguna](#8-perintah-tambahan-yang-berguna)
- [9. Troubleshooting Umum](#9-troubleshooting-umum)
- [10. Praktik Terbaik](#10-praktik-terbaik)
- [11. Lisensi Dependensi](#11-lisensi-dependensi)

## 1. Gambaran Umum
- **SQLAlchemy** menyediakan ORM dan definisi model (misalnya kelas `User`).
- **Flask-Migrate/Alembic** mencatat perubahan skema ke dalam skrip migrasi, lalu mengeksekusinya ke database.
- Database default menggunakan SQLite (`sqlite:///db.sqlite3`).

## 2. Prasyarat
1. Python 3.11 atau kompatibel.
2. Dependensi terpasang:
   ```powershell
   pip install flask flask-sqlalchemy flask-migrate
   ```
3. Pastikan variabel lingkungan `FLASK_APP` mengarah ke `app.py` sebelum menjalankan perintah Flask CLI:
   ```powershell
   $env:FLASK_APP = "app.py"  # PowerShell
   :: set FLASK_APP=app.py     # Command Prompt (cmd)
   ```

## 3. Struktur Minimal Aplikasi
```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))
```

## 4. Alur Kerja Migrasi Standar
1. **Inisialisasi sekali** (membuat folder `migrations/`):
   ```powershell
   flask db init
   ```
2. **Setiap kali model berubah**:
   1. Sesuaikan model Python (tambah/hapus kolom, tabel, relasi, dll.).
   2. Buat skrip migrasi otomatis:
      ```powershell
      flask db migrate -m "Deskripsi singkat perubahan"
      ```
   3. Tinjau file yang dibuat di `migrations/versions/` (pastikan operasi sesuai harapan).
   4. Terapkan ke database:
      ```powershell
      flask db upgrade
      ```

> 🔁 `migrate` hanya membuat skrip, sedangkan `upgrade` menjalankan skrip tersebut pada database aktif.

## 5. Contoh: Menambah Kolom pada Tabel `users`
1. Edit model `User` dan tambahkan kolom baru, misalnya `password`.
2. Jalankan:
   ```powershell
   flask db migrate -m "Tambah kolom password"
   flask db upgrade
   ```
3. Database kini memiliki kolom baru, sementara Alembic mencatat perubahan tersebut.

## 6. Contoh: Menghapus Kolom
1. Hapus atribut dari model (misalnya hapus `password` dari `User`).
2. Jalankan:
   ```powershell
   flask db migrate -m "Hapus kolom password"
   flask db upgrade
   ```
3. Alembic membuat skrip drop kolom dan menerapkannya saat `upgrade`.

## 7. Menambahkan Data Seed dengan Migrasi
Selain mengubah skema, Anda dapat memasukkan data awal (seed) menggunakan skrip migrasi. Contoh sederhana:

1. Buat revisi baru:
   ```powershell
   flask db revision -m "seed user data"
   ```
2. Edit file di `migrations/versions/` dan tambahkan operasi `bulk_insert`:
   ```python
   from alembic import op
   import sqlalchemy as sa

   users = sa.table(
       'user',
       sa.Column('id', sa.Integer),
       sa.Column('name', sa.String(50)),
       sa.Column('email', sa.String(50)),
   )

   def upgrade():
       op.bulk_insert(
           users,
           [
               {"id": 101, "name": "Contoh 1", "email": "contoh1@example.com"},
               {"id": 102, "name": "Contoh 2", "email": "contoh2@example.com"},
           ],
       )

   def downgrade():
       op.execute(
           users.delete().where(users.c.id.in_([101, 102]))
       )
   ```
3. Simpan file, lalu jalankan:
   ```powershell
   flask db upgrade
   ```

Dengan cara ini, data dummy otomatis terisi saat migrasi dijalankan di lingkungan baru. Pastikan `down_revision` mengarah ke migrasi sebelumnya dan sediakan logika `downgrade` untuk membersihkan data seed jika dilakukan rollback.

> 🔄 **Menjalankan ulang seed**: Jika ingin mengisi ulang data seed yang sama (misalnya setelah melakukan perubahan manual di database), jalankan perintah downgrade ke revisi sebelum seed lalu upgrade kembali. Contoh:
> ```powershell
> flask db downgrade <revision_sebelum_seed>
> flask db upgrade
> ```
> Untuk seed ruangan pada proyek ini, gunakan:
> ```powershell
> flask db downgrade 6d278d92961d
> flask db upgrade
> ```

## 8. Perintah Tambahan yang Berguna
- Lihat status versi saat ini:
  ```powershell
  flask db current
  ```
- Daftar riwayat migrasi:
  ```powershell
  flask db history
  ```
- Kembali ke revisi sebelumnya (gunakan hati-hati, pastikan backup data):
  ```powershell
  flask db downgrade
  ```

## 9. Troubleshooting Umum
| Pesan | Penyebab | Solusi |
|-------|----------|--------|
| `Error: Target database is not up to date.` | Ada migrasi tertunda yang belum dijalankan. | Jalankan `flask db upgrade` lalu ulangi `flask db migrate`. |
| Tidak ada perubahan terdeteksi saat `flask db migrate`. | Model belum berubah atau Alembic tidak melihat perubahan. | Pastikan file model disimpan dan import model dilakukan di `app.py`/`env.py`. |
| Peringatan `FSADeprecationWarning`. | Peringatan bawaan Flask CLI terkait opsi yang akan berubah. | Dapat diabaikan sementara atau atur `FLASK_RUN_FROM_CLI=True/False`. |

## 10. Praktik Terbaik
- Commit file migrasi (`migrations/versions/*.py`) bersama perubahan model untuk menjaga riwayat lengkap.
- Backup database sebelum menjalankan `downgrade` atau perubahan besar.
- Jika menggunakan SQLite, Alembic menangani beberapa operasi dengan "batch mode"; selalu review skrip migrasi sebelum dijalankan produksi.

## 11. Lisensi Dependensi
Proyek ini memanfaatkan beberapa pustaka open source berikut:
- **Flask** – BSD-3-Clause License
- **Flask-SQLAlchemy** – BSD-3-Clause License
- **SQLAlchemy** – MIT License
- **Alembic** – MIT License
- **Flask-Migrate** – MIT License

Lihat repositori resmi masing-masing paket untuk detail lisensi lengkap.

Dengan panduan ini, Anda bisa menambah, mengubah, atau menghapus skema database secara terkontrol menggunakan Alembic melalui antarmuka Flask-Migrate.
