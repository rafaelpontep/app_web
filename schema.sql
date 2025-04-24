DROP TABLE IF EXISTS Fornecedor;
DROP TABLE IF EXISTS Insumo;

CREATE TABLE Insumo (
    idInsumo INTEGER PRIMARY KEY AUTOINCREMENT,
    nomeInsumo VARCHAR(45),
    QtdInsumo INTEGER,
    descricaoInsumo VARCHAR(150),
    Status VARCHAR(45)
);

CREATE TABLE Fornecedor (
    idFornecedor INTEGER PRIMARY KEY AUTOINCREMENT,
    nomeFornecedor VARCHAR(45),
    insumoFornecedor VARCHAR(45),
    precoInsumo FLOAT,
    contatoTelefone VARCHAR(20),
    contatoEmail VARCHAR(45),
    idInsumo INTEGER,
    FOREIGN KEY (idInsumo) REFERENCES Insumo(idInsumo)
);