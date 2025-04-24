from flask import Flask, render_template, jsonify, request, g
import sqlite3

app = Flask('__name__')
DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def modify_db(query, args=()):
    conn = get_db()
    cur = conn.execute(query, args)
    conn.commit()
    cur.close()
    return cur.lastrowid

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

# Insumo CRUD endpoints
@app.route('/insumos', methods=['GET'])
def get_insumos():
    insumos = query_db('SELECT * FROM Insumo')
    result = [dict(row) for row in insumos]
    return jsonify(result)

@app.route('/insumos/<int:id>', methods=['GET'])
def get_insumo(id):
    insumo = query_db('SELECT * FROM Insumo WHERE idInsumo = ?', [id], one=True)
    if insumo is None:
        return jsonify({"error": "Insumo not found"}), 404
    return jsonify(dict(insumo))

@app.route('/insumos', methods=['POST'])
def create_insumo():
    if not request.json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    required = ['nomeInsumo', 'QtdInsumo', 'descricaoInsumo', 'Status']
    if not all(field in request.json for field in required):
        return jsonify({"error": "Missing required fields"}), 400
    
    new_id = modify_db(
        'INSERT INTO Insumo (nomeInsumo, QtdInsumo, descricaoInsumo, Status) VALUES (?, ?, ?, ?)',
        [request.json['nomeInsumo'], request.json['QtdInsumo'], request.json['descricaoInsumo'], request.json['Status']]
    )
    
    return jsonify({"id": new_id, **request.json}), 201

@app.route('/insumos/<int:id>', methods=['PUT'])
def update_insumo(id):
    if not request.json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    insumo = query_db('SELECT * FROM Insumo WHERE idInsumo = ?', [id], one=True)
    if insumo is None:
        return jsonify({"error": "Insumo not found"}), 404
    
    nome = request.json.get('nomeInsumo', dict(insumo)['nomeInsumo'])
    qtd = request.json.get('QtdInsumo', dict(insumo)['QtdInsumo'])
    desc = request.json.get('descricaoInsumo', dict(insumo)['descricaoInsumo'])
    status = request.json.get('Status', dict(insumo)['Status'])
    
    modify_db(
        'UPDATE Insumo SET nomeInsumo = ?, QtdInsumo = ?, descricaoInsumo = ?, Status = ? WHERE idInsumo = ?',
        [nome, qtd, desc, status, id]
    )
    
    return jsonify({"id": id, "nomeInsumo": nome, "QtdInsumo": qtd, "descricaoInsumo": desc, "Status": status})

@app.route('/insumos/<int:id>', methods=['DELETE'])
def delete_insumo(id):
    insumo = query_db('SELECT * FROM Insumo WHERE idInsumo = ?', [id], one=True)
    if insumo is None:
        return jsonify({"error": "Insumo not found"}), 404
    
    modify_db('DELETE FROM Insumo WHERE idInsumo = ?', [id])
    return jsonify({"result": "Insumo deleted"})

# Fornecedor CRUD endpoints
@app.route('/fornecedores', methods=['GET'])
def get_fornecedores():
    fornecedores = query_db('SELECT * FROM Fornecedor')
    result = [dict(row) for row in fornecedores]
    return jsonify(result)

@app.route('/fornecedores/<int:id>', methods=['GET'])
def get_fornecedor(id):
    fornecedor = query_db('SELECT * FROM Fornecedor WHERE idFornecedor = ?', [id], one=True)
    if fornecedor is None:
        return jsonify({"error": "Fornecedor not found"}), 404
    return jsonify(dict(fornecedor))

@app.route('/fornecedores', methods=['POST'])
def create_fornecedor():
    if not request.json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    required = ['nomeFornecedor', 'insumoFornecedor', 'precoInsumo', 'contatoTelefone', 'contatoEmail', 'idInsumo']
    if not all(field in request.json for field in required):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Check if referenced Insumo exists
    insumo = query_db('SELECT * FROM Insumo WHERE idInsumo = ?', [request.json['idInsumo']], one=True)
    if insumo is None:
        return jsonify({"error": "Referenced Insumo does not exist"}), 400
    
    new_id = modify_db(
        'INSERT INTO Fornecedor (nomeFornecedor, insumoFornecedor, precoInsumo, contatoTelefone, contatoEmail, idInsumo) VALUES (?, ?, ?, ?, ?, ?)',
        [request.json['nomeFornecedor'], request.json['insumoFornecedor'], request.json['precoInsumo'], 
         request.json['contatoTelefone'], request.json['contatoEmail'], request.json['idInsumo']]
    )
    
    return jsonify({"id": new_id, **request.json}), 201

@app.route('/fornecedores/<int:id>', methods=['PUT'])
def update_fornecedor(id):
    if not request.json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    fornecedor = query_db('SELECT * FROM Fornecedor WHERE idFornecedor = ?', [id], one=True)
    if fornecedor is None:
        return jsonify({"error": "Fornecedor not found"}), 404
    
    f_dict = dict(fornecedor)
    nome = request.json.get('nomeFornecedor', f_dict['nomeFornecedor'])
    insumo = request.json.get('insumoFornecedor', f_dict['insumoFornecedor'])
    preco = request.json.get('precoInsumo', f_dict['precoInsumo'])
    telefone = request.json.get('contatoTelefone', f_dict['contatoTelefone'])
    email = request.json.get('contatoEmail', f_dict['contatoEmail'])
    id_insumo = request.json.get('idInsumo', f_dict['idInsumo'])
    
    # Check if referenced Insumo exists if being updated
    if 'idInsumo' in request.json:
        insumo_check = query_db('SELECT * FROM Insumo WHERE idInsumo = ?', [id_insumo], one=True)
        if insumo_check is None:
            return jsonify({"error": "Referenced Insumo does not exist"}), 400
    
    modify_db(
        'UPDATE Fornecedor SET nomeFornecedor = ?, insumoFornecedor = ?, precoInsumo = ?, contatoTelefone = ?, contatoEmail = ?, idInsumo = ? WHERE idFornecedor = ?',
        [nome, insumo, preco, telefone, email, id_insumo, id]
    )
    
    return jsonify({
        "id": id, 
        "nomeFornecedor": nome, 
        "insumoFornecedor": insumo, 
        "precoInsumo": preco,
        "contatoTelefone": telefone,
        "contatoEmail": email,
        "idInsumo": id_insumo
    })

@app.route('/fornecedores/<int:id>', methods=['DELETE'])
def delete_fornecedor(id):
    fornecedor = query_db('SELECT * FROM Fornecedor WHERE idFornecedor = ?', [id], one=True)
    if fornecedor is None:
        return jsonify({"error": "Fornecedor not found"}), 404
    
    modify_db('DELETE FROM Fornecedor WHERE idFornecedor = ?', [id])
    return jsonify({"result": "Fornecedor deleted"})

if __name__ == '__main__':
    app.run(debug=True)