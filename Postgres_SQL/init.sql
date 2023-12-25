CREATE TABLE pokemon (
    numero VARCHAR(10) PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    image_mini VARCHAR(255),
    lien VARCHAR(255),
    image VARCHAR(255)
);

CREATE TABLE type (
    type_id SERIAL PRIMARY KEY,
    type_nom VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE pokemon_type (
    numero VARCHAR(10),
    type_id INT,
    FOREIGN KEY (numero) REFERENCES pokemon(numero),
    FOREIGN KEY (type_id) REFERENCES type(type_id),
    PRIMARY KEY (numero, type_id)
);

CREATE TABLE statistiques (
    numero VARCHAR(10),
    pv INT,
    attaque INT,
    defense INT,
    attaque_speciale INT,
    defense_speciale INT,
    vitesse INT,
    special INT,
    FOREIGN KEY (numero) REFERENCES pokemon(numero),
    PRIMARY KEY (numero)
);

CREATE TABLE evolution (
    numero VARCHAR(10),
    evolution VARCHAR(255),
    FOREIGN KEY (numero) REFERENCES pokemon(numero),
    PRIMARY KEY (numero, evolution)
);
