import os
import sys



def load_table(filename):
    table = {}
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            ch, code = line.split()
            table[ch.upper()] = code
    return table


char_to_bt = lambda c: {"-": -1, "=": 0, "+": 1}[c]
bt_to_char = lambda b: {-1: "-", 0: "=", 1: "+"}[b]


def ternary_xor_decrypt(triplet, key_triplet):
    return "".join([bt_to_char((char_to_bt(c) - char_to_bt(k) + 1) % 3 - 1) for c,k in zip(triplet, key_triplet)])


def decrypt_message(cipher_triples, key_triples, table):
    rev_table = {v: k for k,v in table.items()}
    full_key = [key_triples[i % len(key_triples)] for i in range(len(cipher_triples))]
    decoded_triples = [ternary_xor_decrypt(c,k) for c,k in zip(cipher_triples, full_key)]
    return "".join([rev_table[t] for t in decoded_triples])


def dec_to_trit(number):
    if number == 0:
        return '='
    string = ''
    while number != 0:
        number, remainder = divmod(number, 3)
        if remainder == 2:
            remainder = -1
            number += 1
        string = ('-','=','+')[remainder + 1] + string
    return string


def get_key(table_name, key_number, folder="tables"):
    filepath = os.path.join(folder, table_name.upper() + ".txt")
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    count = len(lines)
    line_index = (key_number - 1) % count
    line = lines[line_index].strip()
    if line.startswith("old "):
        parts = line.split(" ", 2)
        return parts[2]
    return line


def decode_message(message):
    parts = message.strip().split()
    callsign = parts[0]
    key_number = int(parts[1] + parts[2])
    table = load_table("codemap.txt")
    result = ""
    i = 3
    while i < len(parts):
        if parts[i].isalpha():
            table_name = parts[i]
            i += 1
            num_parts = []
            while i < len(parts) and not parts[i].isalpha():
                num_parts.append(parts[i])
                i += 1
            enc_number = int("".join(num_parts))
            trit_str = dec_to_trit(enc_number)
            if trit_str.startswith('+'):
                trit_str = trit_str[1:]
            cipher_triples = [trit_str[j:j+3] for j in range(0, len(trit_str), 3)]
            key_raw = get_key(table_name, key_number)
            key_triples = key_raw.split()
            result += decrypt_message(cipher_triples, key_triples, table)
        else:
            i += 1
    return result



if __name__ == "__main__":
    if len(sys.argv) > 1:
        msg = " ".join(sys.argv[1:])
    else:
        msg = input("MESSAGE: ")
    print(decode_message(msg))
