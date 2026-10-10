#! /usr/bin/env python3
import sys
import os
import struct
import array

def generate(filename):
    ID = 1
    STR = 2

    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    section = None
    msgid = msgstr = ''
    messages = {}

    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('msgid'):
            if section == STR:
                if msgid == '' or msgstr != '':
                    messages[msgid] = msgstr
            section = ID
            msgid = eval(line[5:].strip())
            msgstr = ''
        elif line.startswith('msgstr'):
            section = STR
            msgstr = eval(line[6:].strip())
        elif line.startswith('"') and line.endswith('"'):
            if section == ID:
                msgid += eval(line)
            elif section == STR:
                msgstr += eval(line)

    if section == STR:
        if msgid == '' or msgstr != '':
            messages[msgid] = msgstr

    # Sort keys
    keys = sorted(messages.keys())
    offsets = []
    ids = b''
    strs = b''

    for key in keys:
        key_bytes = key.encode('utf-8')
        val_bytes = messages[key].encode('utf-8')
        offsets.append((len(ids), len(key_bytes), len(strs), len(val_bytes)))
        ids += key_bytes + b'\x00'
        strs += val_bytes + b'\x00'

    keystart = 7 * 4 + 16 * len(keys)
    valuestart = keystart + len(ids)

    koffsets = []
    voffsets = []
    for o1, l1, o2, l2 in offsets:
        koffsets += [l1, o1 + keystart]
        voffsets += [l2, o2 + valuestart]

    output = struct.pack(
        "Iiiiiii",
        0x950412de,       # Magic
        0,                # Version
        len(keys),        # # of strings
        7 * 4,            # Offset of table with original strings
        7 * 4 + len(keys) * 8,  # Offset of table with translation strings
        0, 0              # Hash table size & offset
    )

    output += array.array("i", koffsets).tobytes()
    output += array.array("i", voffsets).tobytes()
    output += ids
    output += strs

    mo_filename = os.path.splitext(filename)[0] + '.mo'
    with open(mo_filename, 'wb') as f:
        f.write(output)
    print(f"Compiled {filename} -> {mo_filename} ({len(messages)} strings, header present: {'' in messages})")

def compile_all_po(locale_root):
    for root, dirs, files in os.walk(locale_root):
        for f in files:
            if f.endswith('.po'):
                po_path = os.path.join(root, f)
                generate(po_path)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if os.path.isdir(arg):
                compile_all_po(arg)
            else:
                generate(arg)
    else:
        locale_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'thonny', 'locale')
        compile_all_po(locale_dir)
