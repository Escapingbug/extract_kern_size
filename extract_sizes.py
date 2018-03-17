import sys
import sqlite3

from elftools.elf.elffile import ELFFile

def db_init(conn):
    c = conn.cursor()
    # create structs table to store the information needing
    c.execute('''
CREATE TABLE structs (name text, size integer)
''')
    # create viewed table to store the name of already viewed DIE
    # This is needed because we should avoid walk through the same
    # DIE many times, and put all those in memory is extremely 
    # large cost memory as the kernel dwarf info is huge
    #c.execute('''
    #CREATE TABLE viewed (name text)
    #''')
    conn.commit()

def process_file(filename, db_conn):
    with open(filename, 'rb') as f:
        elffile = ELFFile(f)

        if not elffile.has_dwarf_info():
            print('  file has no DWARF info')
            return

        dwarfinfo = elffile.get_dwarf_info()

        for CU in dwarfinfo.iter_CUs():
            top_DIE = CU.get_top_DIE()
            die_info_rec(top_DIE, db_conn)


def save_struct_info(name, size, conn):
    name = name.decode('UTF-8')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM structs WHERE name=?', (name, ))
    print('name %s size %d ' % (name, size))
    if c.fetchone()[0] > 0:
        # alaready saved
        return
    print('saving struct %s' % name)
    c.execute('INSERT INTO structs VALUES(?, ?)', (name, size))
    conn.commit()


def die_info_rec(die, db_conn):
    # Struct definition
    if die.tag == 'DW_TAG_structure_type':
        try:
            struct_name = die.attributes['DW_AT_name'].value
            struct_size = int(die.attributes['DW_AT_byte_size'].value)
            print('struct name %s' % struct_name)
            save_struct_info(struct_name, struct_size, db_conn)
        except KeyError:
            pass

    for cu in die.iter_children():
        die_info_rec(cu, db_conn)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('usage: %s KERN_IMG DATABASE_NAME' % sys.argv[0])
    conn = sqlite3.connect(sys.argv[2])
    db_init(conn)
    process_file(sys.argv[1], conn)
