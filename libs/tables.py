import os
import re
import random
import shutil
import zipfile
import subprocess
import tempfile
from datetime import datetime


SYMBOLS = list("ETAOINSHRDLCUMWFGYPBVKJXQZ_")
WORDS = [
    'Abyss', 'Addiction', 'Affection', 'Badapple', 'Bitrot', 'Blackout', 
    'Blindness', 'Blood', 'Bloodpoison', 'Brainfog', 'Breakdown', 
    'Buffering', 'Butcher', 'Carnage', 'Collapse', 'Crash', 'Darkseed', 
    'Datacorrupt', 'Deadzone', 'Deepvoid', 'Delirium', 'Disaster', 
    'Dread', 'Dusk', 'Execution', 'Failure', 'Fallout', 'Femboy', 
    'Frenzy', 'Furry', 'Heart', 'Heartattack', 'Heartbleed', 'Heartbreak', 
    'Heartburn', 'Infection', 'Insane', 'Insomnia', 'Interference', 
    'Ischemia', 'Lifedrain', 'Logicbomb', 'Madness', 'Meatgrinder', 
    'Meltdown', 'Memoryleak', 'Monodrama', 'Necrosis', 'Nervebreak', 
    'Nightmare', 'Nirvana', 'Oblivion', 'Overflow', 'Paralysis', 'Predator', 
    'Resurrection', 'Rupture', 'Scatterbrain', 'Sickness', 'Signalnoise', 
    'Systemfailure', 'Tenebris', 'Torment', 'Torture', 'Wasteland', 'Wrath', 
    'Reckless','Solution','Humankind','Disbelief','Vanity','Vein','Viscera',
    'Worship','Patience','Virtue','Desire','Desecrate','Devourer','Scar',
    'Rectify','Deify','Gory','Protocol','Kerosene','Betray','Contemplate','Mistake'
]


FOLDER = "tables"
TRITS = ['-', '=', '+']
EXCEPTIONS = {
    "Badapple": 5,
    "Lain": 25,
    "Furry": 25
}



def true_choice(seq):
    idx = int.from_bytes(os.urandom(4), "little") % len(seq)
    return seq[idx]


def rotate_logs():
    base = "data"
    logs = os.path.join(base, "logs")
    if not os.path.exists(logs):
        return
    i = 1
    while os.path.exists(os.path.join(base, f"logs_old{'' if i==1 else i}")):
        i += 1
    os.rename(logs, os.path.join(base, f"logs_old{'' if i==1 else i}"))
    os.makedirs(logs)
    for name in ("history.txt", "logs.txt", "temp.txt"):
        open(os.path.join(logs, name), "w").close()


def gen_tables():
    rotate_logs()
    if os.path.exists(FOLDER):
        i = 1
        while True:
            old_name = f"tables_old{i}" if i > 1 else "tables_old"
            if not os.path.exists(old_name):
                shutil.move(FOLDER, old_name)
                break
            i += 1

        base = "data"
        old_logs = None
        j = 1
        last = None
        while True:
            candidate = os.path.join(base, f"logs_old{'' if j==1 else j}")
            if os.path.exists(candidate):
                last = candidate
                j += 1
            else:
                break
        old_logs = last

        os.makedirs("archives", exist_ok=True)
        timestamp = datetime.now().strftime("%Y_%m_%d")
        archive_path = os.path.join("archives", f"archive_{timestamp}.tar.xz")

        with tempfile.TemporaryDirectory() as tmp:
            shutil.copytree(old_name, os.path.join(tmp, "tables"))
            if old_logs:
                history = os.path.join(old_logs, "history.txt")
                if os.path.exists(history):
                    shutil.copy(history, os.path.join(tmp, "history.txt"))
            letters = "data/codemap.txt"
            if os.path.exists(letters):
                shutil.copy(letters, os.path.join(tmp, "codemap.txt"))
            subprocess.run(
                ["tar", "-cJf", os.path.abspath(archive_path), "-C", tmp, "."],
                check=True
            )

        shutil.rmtree(old_name)
        if old_logs and os.path.exists(old_logs):
            shutil.rmtree(old_logs)

    os.makedirs(FOLDER, exist_ok=True)
    for word in WORDS:
        filename = os.path.join(FOLDER, word.upper() + ".txt")
        count = EXCEPTIONS.get(word, 256)
        keys = [' '.join(''.join(random.choices(TRITS, k=3)) for _ in range(11)) for _ in range(count)]
        with open(filename, "w") as f:
            f.write('\n'.join(keys))


def get_random_line(rand_number_int, folder=FOLDER):
    files = [f for f in os.listdir(folder) if f.endswith(".txt")]
    if not files:
        return None, None, None, None
    chosen_file = true_choice(files)
    file_path = os.path.join(folder, chosen_file)
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    if not lines:
        return None, os.path.splitext(chosen_file)[0], None, None
    line_index = (rand_number_int - 1) % len(lines)
    line = lines[line_index].rstrip("\n")
    if not line.startswith("old "):
        lines[line_index] = f"old {rand_number_int} {line}\n"
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        rand_number_str = f"{rand_number_int:06d}"
        return rand_number_str, os.path.splitext(chosen_file)[0], line, line_index + 1
    return None, os.path.splitext(chosen_file)[0], None, None


def generate_codemap(path):
    if os.path.exists(path):
        os.remove(path)
    symbols = SYMBOLS[:]
    random.shuffle(symbols)
    trits = ['-', '=', '+']
    triplets = [a+b+c for a in trits for b in trits for c in trits]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        for sym, trip in zip(symbols, triplets):
            f.write(f"{sym} {trip}\n")
