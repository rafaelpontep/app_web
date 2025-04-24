import sqlite3

def create_tables(connection):
    with open('schema.sql', 'r') as f:
        connection.executescript(f.read())

def insert_sample_data(cur):
    # Insert sample item
    cur.execute("""
        INSERT OR IGNORE INTO Insumo (nomeInsumo, QtdInsumo, descricaoInsumo, Status)
        VALUES (?, ?, ?, ?)
    """, ('Papel A4', 500, 'Resma de papel tamanho A4', 'Ativo'))

    # Get id of inserted item
    id_insumo = cur.lastrowid

    # Insert sample supplier
    cur.execute("""
        INSERT OR IGNORE INTO Fornecedor (
            nomeFornecedor, insumoFornecedor, precoInsumo, 
            contatoTelefone, contatoEmail, idInsumo
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, ('Papelaria XYZ', 'Papel A4', 23.90, '11999999999', 'contato@xyz.com', id_insumo))

def main():
    try:
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        create_tables(conn)
        insert_sample_data(cur)

        conn.commit()
        print("Database schema created and sample data inserted successfully.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Connection closed.")

if __name__ == "__main__":
    main()