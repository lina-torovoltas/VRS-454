from libs.trit_utils import encrypt_message, load_table, trit_to_dec
from libs.tables import get_random_line
import os




def rand_int(a, b):
    val = int.from_bytes(os.urandom(4), "little")
    return a + val % (b - a + 1)


def split_digits(s, group=4):
    s = str(s)
    if len(s) % group == 3:
        parts = [s[i:i+group] for i in range(0, len(s) - 3, group)]
        parts.append(s[-3:])
    else:
        parts = [s[i:i+group] for i in range(0, len(s), group)]
    return " ".join(parts)


def chunk_message(message, size=20):
    return [message[i:i+size] for i in range(0, len(message), size)]


def encode_message(callsign, message, table):
    message_chunks = chunk_message(message, 11)
    rand_number_int = rand_int(1, 999999)

    chunk_num = 0
    for chunk in message_chunks:
        chunk_num += 1
        key = None
        n = 0
        while key == None and n < 100:
            n += 1
            print(f'attempt {n}')
            key_rand_number, table_name, key, num = get_random_line(rand_number_int)
    
        if key is None:
            print(f"Key not found for chunk {chunk_num}")
            break

        enc_trits = encrypt_message(chunk, key.strip().split(), table)
        enc_number = trit_to_dec('+' + ''.join(enc_trits))

        key_rand_number_fmt = split_digits(key_rand_number)
        enc_number_fmt = split_digits(enc_number)

        if chunk_num == 1:
            output_string = f'{callsign} {key_rand_number_fmt} {table_name} {enc_number_fmt}'
        else:
            output_string += f' {table_name} {enc_number_fmt}'
        
    return output_string


def process_message(callsign="VRS-545"):
    table = load_table("data/codemap.txt")
    with open("data/messages.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
    if not lines:
        return "failure"
    original = lines[0].strip()
    remaining = lines[1:]
    encoded = encode_message(callsign, original, table)
    with open("data/logs/temp.txt", "w", encoding="utf-8") as f:
        f.write(encoded)
    if os.path.exists("data/logs/history.txt"):
        with open("data/logs/history.txt", "r", encoding="utf-8") as f:
            hist_lines = f.read().splitlines()
    else:
        hist_lines = []
    hist_lines.insert(0, encoded)
    with open("data/logs/history.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(hist_lines) + "\n")
    with open("data/logs/logs.txt", "a", encoding="utf-8") as f:
        f.write(f"{original.upper()} - {encoded}\n")
    with open("data/messages.txt", "w", encoding="utf-8") as f:
        f.writelines(remaining)
    return encoded
