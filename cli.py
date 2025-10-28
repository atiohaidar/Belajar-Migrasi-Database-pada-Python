import sys
from typing import Callable

from app import Ruangan, RuanganUser, User, db


def list_users() -> None:
    users = User.query.order_by(User.id).all()
    if not users:
        print("Tidak ada data pengguna.")
        return

    print("\nDaftar Pengguna:")
    print("================")
    for user in users:
        assignments = (
            RuanganUser.query.filter_by(user_id=user.id)
            .join(Ruangan, RuanganUser.ruangan_id == Ruangan.id)
            .add_columns(Ruangan.name.label("ruangan_name"))
            .all()
        )
        ruang_list = ", ".join(row.ruangan_name for row in assignments) if assignments else "-"

        print(
            "ID: {id}\nNama: {nama}\nEmail: {email}\nRuangan: {ruang}\n-".format(
                id=user.id,
                nama=user.name,
                email=user.email,
                ruang=ruang_list,
            )
        )


def create_user() -> None:
    try:
        name = input("Masukkan nama: ").strip()
        email = input("Masukkan email: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nInput dibatalkan.")
        return

    if not name or not email:
        print("Nama dan email wajib diisi.")
        return

    user = User(name=name, email=email)
    db.session.add(user)
    db.session.commit()
    print(f"Pengguna {name} berhasil dibuat dengan ID {user.id}.")


def get_user_by_id() -> User | None:
    try:
        user_id = int(input("Masukkan ID pengguna: "))
    except (ValueError, EOFError, KeyboardInterrupt):
        print("Input ID tidak valid atau dibatalkan.")
        return None

    user = User.query.get(user_id)
    if user is None:
        print("Pengguna tidak ditemukan.")
    return user


def list_rooms() -> None:
    rooms = Ruangan.query.order_by(Ruangan.id).all()
    if not rooms:
        print("Tidak ada data ruangan.")
        return

    print("\nDaftar Ruangan:")
    print("================")
    for room in rooms:
        occupancy = (
            RuanganUser.query.filter_by(ruangan_id=room.id)
            .join(User, RuanganUser.user_id == User.id)
            .add_columns(User.name.label("user_name"))
            .all()
        )
        penghuni = ", ".join(row.user_name for row in occupancy) if occupancy else "-"

        print(
            "ID: {id}\nNama Ruangan: {nama}\nPenghuni: {penghuni}\n-".format(
                id=room.id,
                nama=room.name,
                penghuni=penghuni,
            )
        )


def create_room() -> None:
    try:
        name = input("Masukkan nama ruangan: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nInput dibatalkan.")
        return

    if not name:
        print("Nama ruangan wajib diisi.")
        return

    room = Ruangan(name=name)
    db.session.add(room)
    db.session.commit()
    print(f"Ruangan {name} berhasil dibuat dengan ID {room.id}.")


def get_room_by_id() -> Ruangan | None:
    try:
        room_id = int(input("Masukkan ID ruangan: "))
    except (ValueError, EOFError, KeyboardInterrupt):
        print("Input ID tidak valid atau dibatalkan.")
        return None

    room = Ruangan.query.get(room_id)
    if room is None:
        print("Ruangan tidak ditemukan.")
    return room


def update_room() -> None:
    room = get_room_by_id()
    if room is None:
        return

    try:
        name = input(f"Nama ruangan baru ({room.name}): ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nInput dibatalkan.")
        return

    if name:
        room.name = name
        db.session.commit()
        print("Data ruangan berhasil diperbarui.")
    else:
        print("Tidak ada perubahan yang disimpan.")


def delete_room() -> None:
    room = get_room_by_id()
    if room is None:
        return

    try:
        konfirmasi = input(f"Hapus ruangan {room.name}? (y/N): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\nInput dibatalkan.")
        return

    if konfirmasi == "y":
        # hapus relasi terlebih dahulu
        RuanganUser.query.filter_by(ruangan_id=room.id).delete()
        db.session.delete(room)
        db.session.commit()
        print("Ruangan berhasil dihapus.")
    else:
        print("Penghapusan dibatalkan.")


def assign_user_to_room() -> None:
    user = get_user_by_id()
    if user is None:
        return

    room = get_room_by_id()
    if room is None:
        return

    existing = RuanganUser.query.filter_by(user_id=user.id, ruangan_id=room.id).first()
    if existing:
        print("Pengguna sudah terdaftar di ruangan tersebut.")
        return

    assignment = RuanganUser(user_id=user.id, ruangan_id=room.id)
    db.session.add(assignment)
    db.session.commit()
    print(f"Pengguna {user.name} berhasil ditempatkan di {room.name}.")


def remove_assignment() -> None:
    user = get_user_by_id()
    if user is None:
        return

    room = get_room_by_id()
    if room is None:
        return

    assignment = RuanganUser.query.filter_by(user_id=user.id, ruangan_id=room.id).first()
    if assignment is None:
        print("Relasi pengguna-ruangan tidak ditemukan.")
        return

    db.session.delete(assignment)
    db.session.commit()
    print("Relasi berhasil dihapus.")


def list_assignments() -> None:
    assignments = (
        RuanganUser.query
        .join(User, RuanganUser.user_id == User.id)
        .join(Ruangan, RuanganUser.ruangan_id == Ruangan.id)
        .add_columns(User.name.label('user_name'), Ruangan.name.label('ruangan_name'), RuanganUser.id.label('assignment_id'))
        .order_by(RuanganUser.id)
        .all()
    )

    if not assignments:
        print("Belum ada relasi pengguna-ruangan.")
        return

    print("\nDaftar Relasi Pengguna-Ruangan:")
    print("==============================")
    for row in assignments:
        print(
            f"ID Relasi: {row.assignment_id}\nPengguna: {row.user_name}\nRuangan: {row.ruangan_name}\n-"
        )


def update_user() -> None:
    user = get_user_by_id()
    if user is None:
        return

    try:
        name = input(f"Nama baru ({user.name}): ").strip()
        email = input(f"Email baru ({user.email}): ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nInput dibatalkan.")
        return

    if name:
        user.name = name
    if email:
        user.email = email

    db.session.commit()
    print("Data pengguna berhasil diperbarui.")


def delete_user() -> None:
    user = get_user_by_id()
    if user is None:
        return

    try:
        konfirmasi = input(f"Hapus pengguna {user.name}? (y/N): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\nInput dibatalkan.")
        return

    if konfirmasi == "y":
        db.session.delete(user)
        db.session.commit()
        print("Pengguna berhasil dihapus.")
    else:
        print("Penghapusan dibatalkan.")


def menu() -> None:
    actions: dict[str, Callable[[], None]] = {
        "1": list_users,
        "2": create_user,
        "3": update_user,
        "4": delete_user,
        "5": list_rooms,
        "6": create_room,
        "7": update_room,
        "8": delete_room,
        "9": assign_user_to_room,
        "10": remove_assignment,
        "11": list_assignments,
        "0": exit_program,
    }

    while True:
        print(
            "\nMenu CRUD Pengguna\n"
            "1. Lihat semua pengguna\n"
            "2. Tambah pengguna baru\n"
            "3. Ubah pengguna\n"
            "4. Hapus pengguna\n"
            "5. Lihat semua ruangan\n"
            "6. Tambah ruangan baru\n"
            "7. Ubah ruangan\n"
            "8. Hapus ruangan\n"
            "9. Tempatkan pengguna ke ruangan\n"
            "10. Hapus relasi pengguna-ruangan\n"
            "11. Lihat semua relasi\n"
            "0. Keluar"
        )
        choice = input("Pilih menu: ").strip()
        action = actions.get(choice)
        if action:
            action()
        else:
            print("Pilihan tidak valid. Coba lagi.")


def exit_program() -> None:
    print("Keluar dari aplikasi.")
    sys.exit(0)


if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        print("\nAplikasi dihentikan.")
        sys.exit(0)
