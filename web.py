from __future__ import annotations

from flask import jsonify, render_template_string, request

from app import Ruangan, RuanganUser, User, app, db


def serialize_user(
    user: User,
    assignments: dict[int, int | None],
    room_lookup: dict[int, str],
) -> dict[str, str | int | None]:
    room_id = assignments.get(user.id)
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "room_id": room_id,
        "room_name": room_lookup.get(room_id),
    }


def build_board_payload() -> dict[str, list[dict[str, str | int | None]]]:
    rooms = Ruangan.query.order_by(Ruangan.id).all()
    users = User.query.order_by(User.id).all()
    assignments = {rel.user_id: rel.ruangan_id for rel in RuanganUser.query.all()}
    room_lookup = {room.id: room.name for room in rooms}

    palette = [serialize_user(user, assignments, room_lookup) for user in users]

    room_payload = []
    for room in rooms:
        room_users = [user for user in palette if user["room_id"] == room.id]
        room_payload.append({
            "id": room.id,
            "name": room.name,
            "users": room_users,
        })

    return {
        "palette": palette,
        "rooms": room_payload,
    }


@app.get("/")
def index():
    return render_template_string(
        """
        <!doctype html>
        <html lang="id">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Manajemen Ruangan Interaktif</title>
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
            <script src="https://cdn.jsdelivr.net/npm/sortablejs@1.15.0/Sortable.min.js"></script>
            <style>
                :root {
                    color-scheme: light dark;
                    font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                }
                body {
                    margin: 0;
                    background: linear-gradient(180deg, #f2f5fb 0%, #ffffff 100%);
                    min-height: 100vh;
                    display: flex;
                    flex-direction: column;
                }
                header {
                    padding: 24px;
                    background: #111827;
                    color: #f9fafb;
                    text-align: center;
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
                }
                header h1 {
                    margin: 0;
                    font-size: 2rem;
                    font-weight: 600;
                }
                header p {
                    margin-top: 8px;
                    color: rgba(249, 250, 251, 0.74);
                }
                main {
                    flex: 1;
                    padding: 24px;
                    display: grid;
                    grid-template-columns: 320px 240px 1fr;
                    gap: 24px;
                }
                @media (max-width: 1100px) {
                    main {
                        grid-template-columns: 1fr;
                    }
                }
                .panel {
                    background: rgba(255, 255, 255, 0.78);
                    backdrop-filter: blur(12px);
                    border-radius: 16px;
                    box-shadow: 0 12px 40px rgba(15, 23, 42, 0.12);
                    padding: 24px;
                }
                .panel h2 {
                    margin-top: 0;
                    font-size: 1.1rem;
                    color: #0f172a;
                    letter-spacing: 0.01em;
                }
                form {
                    display: grid;
                    gap: 16px;
                    margin-top: 16px;
                }
                label span {
                    font-size: 0.9rem;
                    color: #475569;
                    display: block;
                    margin-bottom: 4px;
                }
                input {
                    width: 100%;
                    padding: 10px 12px;
                    border-radius: 10px;
                    border: 1px solid rgba(148, 163, 184, 0.5);
                    background: rgba(255, 255, 255, 0.9);
                    font: inherit;
                }
                button {
                    padding: 12px 16px;
                    border: none;
                    border-radius: 10px;
                    background: linear-gradient(135deg, #6366f1, #8b5cf6);
                    color: #fff;
                    font-weight: 600;
                    cursor: pointer;
                    transition: transform 120ms ease, box-shadow 120ms ease;
                }
                button:hover {
                    transform: translateY(-1px);
                    box-shadow: 0 10px 25px rgba(99, 102, 241, 0.25);
                }
                #board {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                    gap: 18px;
                }
                .column {
                    background: rgba(255, 255, 255, 0.9);
                    border-radius: 16px;
                    padding: 16px;
                    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
                    display: flex;
                    flex-direction: column;
                }
                .column h3 {
                    margin: 0 0 12px;
                    font-size: 1rem;
                    color: #1f2937;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                }
                .user-list {
                    list-style: none;
                    padding: 0;
                    margin: 0;
                    display: flex;
                    flex-direction: column;
                    gap: 10px;
                    min-height: 60px;
                }
                .user-card {
                    cursor: grab;
                    padding: 12px 14px;
                    border-radius: 12px;
                    background: linear-gradient(135deg, rgba(79, 70, 229, 0.1), rgba(59, 130, 246, 0.18));
                    color: #1e293b;
                    display: grid;
                    gap: 4px;
                    border: 1px solid rgba(99, 102, 241, 0.25);
                    transition: transform 120ms ease, box-shadow 120ms ease;
                }
                .user-card:active {
                    cursor: grabbing;
                }
                .user-card strong {
                    font-weight: 600;
                    letter-spacing: 0.01em;
                }
                .user-card span {
                    font-size: 0.85rem;
                    color: rgba(30, 41, 59, 0.74);
                }
                .toast {
                    position: fixed;
                    bottom: 24px;
                    right: 24px;
                    padding: 14px 18px;
                    border-radius: 12px;
                    background: #0f172a;
                    color: #f8fafc;
                    box-shadow: 0 15px 35px rgba(15, 23, 42, 0.25);
                    opacity: 0;
                    transform: translateY(12px);
                    transition: opacity 160ms ease, transform 160ms ease;
                    z-index: 99;
                }
                .toast.visible {
                    opacity: 1;
                    transform: translateY(0);
                }
                .toast.error {
                    background: #dc2626;
                }
                .drop-target {
                    border: 2px dashed rgba(99, 102, 241, 0.45);
                    background: rgba(99, 102, 241, 0.08);
                }
                .user-card.dragging {
                    transform: scale(1.02);
                    box-shadow: 0 15px 35px rgba(79, 70, 229, 0.25);
                }
                .palette-panel {
                    display: flex;
                    flex-direction: column;
                    gap: 16px;
                }
                .palette-panel h2 {
                    margin: 0;
                }
            </style>
        </head>
        <body>
            <header>
                <h1>Papan Manajemen Ruangan</h1>
                <p>Seret dan jatuhkan pengguna antar ruangan layaknya bermain game.</p>
            </header>
            <main>
                <aside class="panel">
                    <h2>Tambah Data</h2>
                    <form id="new-user-form">
                        <label>
                            <span>Nama Pengguna</span>
                            <input name="name" placeholder="Misal: Sinta" required>
                        </label>
                        <label>
                            <span>Email</span>
                            <input name="email" type="email" placeholder="sinta@example.com" required>
                        </label>
                        <button type="submit">Tambah Pengguna</button>
                    </form>
                    <form id="new-room-form">
                        <label>
                            <span>Nama Ruangan</span>
                            <input name="name" placeholder="Misal: Studio Kreatif" required>
                        </label>
                        <button type="submit">Tambah Ruangan</button>
                    </form>
                </aside>
                <section class="panel palette-panel">
                    <h2>Daftar Pengguna</h2>
                    <p style="margin:0;color:#64748b;font-size:0.85rem;">Semua pengguna tersedia. Seret ke ruangan mana pun.</p>
                    <div class="column" style="padding:0;background:transparent;box-shadow:none;">
                        <h3 style="padding:16px 16px 0;">Palet Pengguna</h3>
                        <ul class="user-list" id="palette" data-room-id=""><!-- populated by JS --></ul>
                    </div>
                </section>
                <section class="panel">
                    <h2>Papan Penempatan</h2>
                    <div id="board"></div>
                </section>
            </main>
            <script>
                const boardEl = document.getElementById('board');
                const paletteList = document.getElementById('palette');
                const userForm = document.getElementById('new-user-form');
                const roomForm = document.getElementById('new-room-form');

                async function fetchBoard() {
                    const response = await fetch('/api/board');
                    if (!response.ok) {
                        throw new Error('Gagal memuat data papan.');
                    }
                    const data = await response.json();
                    renderBoard(data);
                }

                function renderBoard(data) {
                    boardEl.innerHTML = '';
                    paletteList.innerHTML = '';
                    data.palette.forEach(user => {
                        paletteList.appendChild(createUserCard(user));
                    });
                    boardEl.appendChild(createColumn('Belum Ter-assign', 'unassigned', data.palette.filter(user => user.room_id === null)));
                    data.rooms.forEach(room => {
                        boardEl.appendChild(createColumn(room.name, `room-${room.id}`, room.users, room.id));
                    });
                    initDragAndDrop();
                }

                function createColumn(title, listId, users, roomId = null) {
                    const column = document.createElement('div');
                    column.className = 'column';
                    const heading = document.createElement('h3');
                    heading.textContent = title;
                    const list = document.createElement('ul');
                    list.className = 'user-list';
                    list.id = listId;
                    list.dataset.roomId = roomId ? String(roomId) : '';

                    users.forEach(user => {
                        list.appendChild(createUserCard(user));
                    });

                    column.appendChild(heading);
                    column.appendChild(list);
                    return column;
                }

                function createUserCard(user) {
                    const item = document.createElement('li');
                    item.className = 'user-card';
                    item.dataset.userId = user.id;
                    const nameEl = document.createElement('strong');
                    nameEl.textContent = user.name;
                    const emailEl = document.createElement('span');
                    emailEl.textContent = user.email;
                    item.appendChild(nameEl);
                    item.appendChild(emailEl);
                    return item;
                }

                function initDragAndDrop() {
                    document.querySelectorAll('.user-list').forEach(list => {
                        Sortable.create(list, {
                            group: 'users',
                            animation: 150,
                            ghostClass: 'dragging',
                            onChoose: (evt) => {
                                evt.item.classList.add('dragging');
                                evt.from.classList.add('drop-target');
                            },
                            onUnchoose: (evt) => {
                                evt.item.classList.remove('dragging');
                                evt.from.classList.remove('drop-target');
                            },
                            onAdd: (evt) => {
                                evt.to.classList.add('drop-target');
                                setTimeout(() => evt.to.classList.remove('drop-target'), 200);
                            },
                            onEnd: handleDrop,
                        });
                    });
                }

                async function handleDrop(evt) {
                    const userId = Number(evt.item.dataset.userId);
                    const targetRoom = evt.to.dataset.roomId;
                    try {
                        const response = await fetch('/api/assign', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                user_id: userId,
                                ruangan_id: targetRoom ? Number(targetRoom) : null,
                            }),
                        });
                        if (!response.ok) {
                            throw new Error('Gagal memperbarui penempatan.');
                        }
                        const data = await response.json();
                        renderBoard(data);
                        showToast('Penempatan berhasil disimpan.');
                    } catch (error) {
                        console.error(error);
                        await fetchBoard();
                        showToast('Terjadi kesalahan ketika memperbarui.', true);
                    }
                }

                function showToast(message, isError = false) {
                    const toast = document.createElement('div');
                    toast.className = 'toast' + (isError ? ' error' : '');
                    toast.textContent = message;
                    document.body.appendChild(toast);
                    requestAnimationFrame(() => toast.classList.add('visible'));
                    setTimeout(() => {
                        toast.classList.remove('visible');
                        toast.addEventListener('transitionend', () => toast.remove(), { once: true });
                    }, 2600);
                }

                userForm.addEventListener('submit', async event => {
                    event.preventDefault();
                    const formData = new FormData(userForm);
                    const payload = Object.fromEntries(formData.entries());
                    try {
                        const response = await fetch('/api/users', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(payload),
                        });
                        if (!response.ok) {
                            const error = await response.json().catch(() => ({}));
                            throw new Error(error.message || 'Gagal menambah pengguna.');
                        }
                        userForm.reset();
                        await fetchBoard();
                        showToast('Pengguna baru ditambahkan.');
                    } catch (error) {
                        console.error(error);
                        showToast(error.message || 'Terjadi kesalahan.', true);
                    }
                });

                roomForm.addEventListener('submit', async event => {
                    event.preventDefault();
                    const formData = new FormData(roomForm);
                    const payload = Object.fromEntries(formData.entries());
                    try {
                        const response = await fetch('/api/rooms', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(payload),
                        });
                        if (!response.ok) {
                            const error = await response.json().catch(() => ({}));
                            throw new Error(error.message || 'Gagal menambah ruangan.');
                        }
                        roomForm.reset();
                        await fetchBoard();
                        showToast('Ruangan baru ditambahkan.');
                    } catch (error) {
                        console.error(error);
                        showToast(error.message || 'Terjadi kesalahan.', true);
                    }
                });

                fetchBoard().catch(error => {
                    console.error(error);
                    showToast('Tidak dapat memuat data awal.', true);
                });
            </script>
        </body>
        </html>
        """
    )


@app.get("/api/board")
def api_board():
    return jsonify(build_board_payload())


@app.post("/api/assign")
def api_assign():
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    room_id = data.get("ruangan_id")

    if user_id is None:
        return jsonify({"message": "user_id wajib diisi"}), 400

    user = User.query.get(user_id)
    if user is None:
        return jsonify({"message": "Pengguna tidak ditemukan"}), 404

    room = None
    if room_id is not None:
        room = Ruangan.query.get(room_id)
        if room is None:
            return jsonify({"message": "Ruangan tidak ditemukan"}), 404

    # Hapus seluruh relasi lama user
    RuanganUser.query.filter_by(user_id=user.id).delete()

    if room_id is not None:
        assignment = RuanganUser(user_id=user.id, ruangan_id=room.id)
        db.session.add(assignment)

    db.session.commit()
    return jsonify(build_board_payload())


@app.post("/api/users")
def api_create_user():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()

    if not name or not email:
        return jsonify({"message": "Nama dan email wajib diisi"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email sudah terdaftar"}), 409

    user = User(name=name, email=email)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Pengguna dibuat", "board": build_board_payload()}), 201


@app.post("/api/rooms")
def api_create_room():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()

    if not name:
        return jsonify({"message": "Nama ruangan wajib diisi"}), 400

    room = Ruangan(name=name)
    db.session.add(room)
    db.session.commit()

    return jsonify({"message": "Ruangan dibuat", "board": build_board_payload()}), 201


@app.delete("/api/rooms/<int:room_id>")
def api_delete_room(room_id: int):
    room = Ruangan.query.get(room_id)
    if room is None:
        return jsonify({"message": "Ruangan tidak ditemukan"}), 404

    RuanganUser.query.filter_by(ruangan_id=room.id).delete()
    db.session.delete(room)
    db.session.commit()
    return jsonify(build_board_payload())


@app.delete("/api/users/<int:user_id>")
def api_delete_user(user_id: int):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"message": "Pengguna tidak ditemukan"}), 404

    RuanganUser.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()
    return jsonify(build_board_payload())


if __name__ == "__main__":
    app.run(debug=True)
