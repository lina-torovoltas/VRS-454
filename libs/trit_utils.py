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


def ternary_xor_encrypt(triplet, key_triplet):
    return "".join([bt_to_char((char_to_bt(m) + char_to_bt(k) + 1) % 3 - 1) for m,k in zip(triplet, key_triplet)])


def ternary_xor_decrypt(triplet, key_triplet):
    return "".join([bt_to_char((char_to_bt(c) - char_to_bt(k) + 1) % 3 - 1) for c,k in zip(triplet, key_triplet)])


def encrypt_message(message, key_triples, table):
    msg_triples = [table[ch.upper()] for ch in message]
    full_key = [key_triples[i % len(key_triples)] for i in range(len(msg_triples))]
    return [ternary_xor_encrypt(m,k) for m,k in zip(msg_triples, full_key)]


def decrypt_message(cipher_triples, key_triples, table):
    rev_table = {v: k for k,v in table.items()}
    full_key = [key_triples[i % len(key_triples)] for i in range(len(cipher_triples))]
    decoded_triples = [ternary_xor_decrypt(c,k) for c,k in zip(cipher_triples, full_key)]
    return "".join([rev_table[t] for t in decoded_triples])


def trit_to_dec(string):
    string = string[::-1]
    decimal = 0
    for position, char in enumerate(string):
        if char == '+': value = 1
        elif char == '=': value = 0
        elif char == '-': value = -1
        else: raise ValueError()
        decimal += value * (3 ** position)
    return decimal


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
