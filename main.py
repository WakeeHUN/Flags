from nicegui import ui, app
import random
import time
import os


NUM_ROWS = 4
NUM_COLS = 4
NUM_CARDS = NUM_ROWS * NUM_COLS

flags = ['fr', 'de', 'hu', 'it', 'es', 'pl', 'gr', 'at']

flags_hun = {
    'fr': 'Franciaország',
    'de': 'Németország',
    'hu': 'Magyarország',
    'it': 'Olaszország',
    'es': 'Spanyolország',
    'pl': 'Lengyelország',
    'gr': 'Görögország',
    'at': 'Ausztria',
}

score_file = "toplista.txt"
labels = []
buttons = []
card_flags = []
revealed = []
matched = []
steps = 0
start_time = 0
player_name = ""
name_input = None


def header():
    def toggle_theme(e):
        app.storage.user['dark'] = e.value  # elmentjük az állapotot
        ui.dark_mode(e.value)

    # Alkalmazzuk az elmentett témát betöltéskor
    ui.dark_mode(app.storage.user.get('dark'))

    with ui.row().classes('items-center justify-between q-pa-md').style('width: 100%; background-color: var(--q-background);'):
        ui.label("🎮 Zászlópárosító").classes('text-h6')

        with ui.row().classes('items-center').style('gap: 30px'):
            ui.button('🏠 Főoldal', on_click=lambda: ui.navigate.to('/')).props('color=primary').classes('w-32')
            ui.button('▶️ Játék', on_click=lambda: ui.navigate.to('/jatek')).props('color=primary').classes('w-32')
            ui.button('🏆 Toplista', on_click=lambda: ui.navigate.to('/toplista')).props('color=primary').classes('w-32')

            # A kapcsoló állapotát a session alapján állítjuk be
            ui.switch('🌙 Sötét mód', value=app.storage.user.get('dark', False), on_change=toggle_theme) \
                .tooltip("Sötét mód váltás").props('dense')

# KEZDŐOLDAL
@ui.page('/')
def home():
    header()

    with ui.column().classes('w-full h-full flex justify-center items-center'):
        ui.label('🎮 Üdv a Zászlópárosító játékban!').classes('text-h4 q-mb-lg')

        global name_input
        name_input = ui.input('Neved:', placeholder='Add meg a neved').props('outlined dense').classes('w-64')

        ui.button('▶️ Játék indítása', on_click=lambda: ui.navigate.to('/jatek')).props('color=primary').classes('w-64')
        ui.button('🏆 Toplista megtekintése', on_click=lambda: ui.navigate.to('/toplista')).props('color=primary').classes('w-64')

# JÁTÉKOLDAL
@ui.page('/jatek')
def jatek():
    header()

    global buttons, card_flags, revealed, matched, steps, start_time, player_name

    with ui.column().classes('w-full h-full flex justify-center items-center'):
        labels = []
        buttons = []
        card_flags = []
        revealed = []
        matched = []
        steps = 0
        start_time = 0
        player_name = name_input.value.strip() if name_input and name_input.value else "Ismeretlen"

        with ui.row().classes('justify-center').style('min-height: 100vh'):
            with ui.column().classes('items-center').style('max-width: 500px'):

                ui.label(f'🧠 Játék – {player_name}').classes('text-h5')
                with ui.card().classes('w-64'):
                    status = ui.label("Találj párokat!")
                    step_label = ui.label("Lépések száma: 0")
                    time_label = ui.label("Eltelt idő: 0 mp")

                def update_timer():
                    if start_time > 0 and len(matched) < NUM_CARDS:
                        elapsed = int(time.time() - start_time)
                        time_label.set_text(f"Eltelt idő: {elapsed} mp")

                ui.timer(1.0, update_timer)

                def hide_cards(i1, i2):
                    buttons[i1].clear()
                    with buttons[i1]:
                        ui.image('static/flags/question.png').style('width: 100%; height: 100%')
                    labels[i1].set_text("")

                    buttons[i2].clear()
                    with buttons[i2]:
                        ui.image('static/flags/question.png').style('width: 100%; height: 100%')
                    labels[i2].set_text("")

                    revealed.clear()

                def on_card_click(index: int):
                    global steps, start_time

                    if index in revealed or index in matched or len(revealed) >= 2:
                        return

                    if start_time == 0:
                        start_time = time.time()

                    revealed.append(index)
                    buttons[index].clear()
                    with buttons[index]:
                        ui.image(f'static/flags/{card_flags[index]}.png').style('width: 100%; height: 100%')
                    labels[index].set_text(flags_hun[card_flags[index]])

                    if len(revealed) == 2:
                        steps += 1
                        step_label.set_text(f"Lépések száma: {steps}")

                        i1, i2 = revealed
                        if card_flags[i1] == card_flags[i2]:
                            status.set_text("✅ Egyeznek!")
                            matched.extend([i1, i2])
                            revealed.clear()

                            if len(matched) == NUM_CARDS:
                                elapsed = int(time.time() - start_time)
                                status.set_text(f"🏆 Kész! {steps} lépésből, {elapsed} mp alatt")
                                ui.notify(f"🎉 Szép munka, {player_name}!")
                                save_score(player_name, steps, elapsed)
                        else:
                            status.set_text("❌ Nem egyeznek!")
                            ui.timer(1.0, lambda: hide_cards(i1, i2), once=True)

                def create_board():
                    buttons.clear()
                    labels.clear()
                    for row in range(NUM_ROWS):
                        with ui.row():
                            for col in range(NUM_COLS):
                                index = row * NUM_COLS + col
                                with ui.column().classes('items-center').style('width: 100px; height: 80px'):
                                    with ui.button(on_click=lambda i=index: on_card_click(i)).style('padding: 0; width: 80px; height: 50px') as btn:
                                        ui.image('static/flags/question.png').style('width: 100%; height: 100%')
                                    lbl = ui.label("").style()
                                buttons.append(btn)
                                labels.append(lbl)

                def save_score(name, steps, time_sec):
                    try:
                        with open(score_file, "a", encoding="utf-8") as f:
                            f.write(f"{name},{steps},{time_sec}\n")
                    except Exception as e:
                        ui.notify(f"Hiba mentés közben: {e}")

                card_flags = flags * 2
                random.shuffle(card_flags)
                create_board()
                ui.button("🔁 Új játék", on_click=lambda: ui.navigate.to('/jatek'))

# TOPLISTA
@ui.page('/toplista')
def toplista():
    header()

    with ui.column().classes('w-full h-full flex justify-center items-center'):
        ui.label("🏆 Toplista – legjobb 5 játékos").classes('text-h4')
        scores = []
        if os.path.exists(score_file):
            with open(score_file, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split(",")
                    if len(parts) == 3:
                        name, steps_str, time_str = parts
                        try:
                            scores.append((name, int(steps_str), int(time_str)))
                        except:
                            continue

        top5step = sorted(scores, key=lambda x: (x[1]))[:5]
        top5time = sorted(scores, key=lambda x: (x[2]))[:5]

        with ui.row().style('gap: 30px'):
            with ui.card().classes('w-64'):    
                ui.label("Leggyorsabb").classes('text-h5')
                for idx, (name, steps, t) in enumerate(top5time, 1):
                    ui.label(f"{idx}. {name} – {t} mp")
            with ui.card().classes('w-64'): 
                ui.label("Legkevesebb lépés").classes('text-h5')
                for idx, (name, steps, t) in enumerate(top5step, 1):
                    ui.label(f"{idx}. {name} – {steps} lépés")

        ui.button("🔙 Vissza a főoldalra", on_click=lambda: ui.navigate.to('/'))


port = int(os.environ.get("PORT", 8080))
ui.run(host='0.0.0.0', port=port, storage_secret='titkoskod2000', reload=False)