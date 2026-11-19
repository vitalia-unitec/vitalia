-- Esquema de Vitalia generado desde las migraciones de Alembic
-- No editar a mano: python -m scripts.exportar_esquema

CREATE TABLE categorias (
	id INTEGER NOT NULL,
	nombre VARCHAR(60) NOT NULL,
	slug VARCHAR(60) NOT NULL,
	icono VARCHAR(40) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (slug)
);

CREATE TABLE clinica_tipos (
	clinica_id INTEGER NOT NULL,
	tipo VARCHAR(20) NOT NULL,
	PRIMARY KEY (clinica_id, tipo),
	CONSTRAINT ck_clinica_tipos_tipo CHECK (tipo IN ('veterinaria', 'hospital', 'estetica', 'hospedaje', 'adiestramiento')),
	FOREIGN KEY(clinica_id) REFERENCES clinicas (id) ON DELETE CASCADE
);

CREATE TABLE clinicas (
	id INTEGER NOT NULL,
	propietario_id INTEGER,
	nombre VARCHAR(150) NOT NULL,
	descripcion TEXT,
	calle VARCHAR(200) NOT NULL,
	colonia VARCHAR(100) NOT NULL,
	alcaldia_municipio VARCHAR(100) NOT NULL,
	ciudad VARCHAR(100) NOT NULL,
	estado VARCHAR(100) NOT NULL,
	codigo_postal VARCHAR(5) NOT NULL,
	lat FLOAT NOT NULL,
	lng FLOAT NOT NULL,
	telefono VARCHAR(10) NOT NULL,
	whatsapp VARCHAR(13),
	sitio_web VARCHAR(300),
	urgencias_24h BOOLEAN NOT NULL,
	verificada BOOLEAN NOT NULL,
	activa BOOLEAN NOT NULL,
	calificacion_prom FLOAT,
	total_resenas INTEGER NOT NULL,
	creado_en DATETIME NOT NULL,
	actualizado_en DATETIME NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(propietario_id) REFERENCES usuarios (id) ON DELETE SET NULL
);

CREATE TABLE comentarios (
	id INTEGER NOT NULL,
	publicacion_id INTEGER NOT NULL,
	autor_id INTEGER,
	texto TEXT NOT NULL,
	creado_en DATETIME NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(autor_id) REFERENCES usuarios (id) ON DELETE SET NULL,
	FOREIGN KEY(publicacion_id) REFERENCES publicaciones (id) ON DELETE CASCADE
);

CREATE TABLE fotos_clinica (
	id INTEGER NOT NULL,
	clinica_id INTEGER NOT NULL,
	ruta VARCHAR(200) NOT NULL,
	orden INTEGER NOT NULL,
	creado_en DATETIME NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(clinica_id) REFERENCES clinicas (id) ON DELETE CASCADE
);

CREATE TABLE horarios (
	id INTEGER NOT NULL,
	clinica_id INTEGER NOT NULL,
	dia_semana INTEGER NOT NULL,
	abre TIME NOT NULL,
	cierra TIME NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT ck_horarios_rango CHECK (cierra > abre),
	CONSTRAINT ck_horarios_dia CHECK (dia_semana BETWEEN 1 AND 7),
	FOREIGN KEY(clinica_id) REFERENCES clinicas (id) ON DELETE CASCADE
);

CREATE TABLE mascotas (
	id INTEGER NOT NULL,
	dueno_id INTEGER NOT NULL,
	nombre VARCHAR(50) NOT NULL,
	especie VARCHAR(10) NOT NULL,
	raza VARCHAR(60),
	sexo VARCHAR(10) NOT NULL,
	edad_anios INTEGER,
	edad_meses INTEGER,
	color VARCHAR(40),
	foto_url VARCHAR(300),
	creado_en DATETIME NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT ck_mascotas_especie CHECK (especie IN ('perro', 'gato', 'ave', 'conejo', 'reptil', 'otro')),
	CONSTRAINT ck_mascotas_sexo CHECK (sexo IN ('macho', 'hembra')),
	CONSTRAINT ck_mascotas_edad_anios CHECK (edad_anios BETWEEN 0 AND 40),
	CONSTRAINT ck_mascotas_edad_meses CHECK (edad_meses BETWEEN 0 AND 11),
	FOREIGN KEY(dueno_id) REFERENCES usuarios (id) ON DELETE CASCADE
);

CREATE TABLE publicaciones (
	id INTEGER NOT NULL,
	autor_id INTEGER,
	texto TEXT NOT NULL,
	creado_en DATETIME NOT NULL,
	editado_en DATETIME,
	PRIMARY KEY (id),
	FOREIGN KEY(autor_id) REFERENCES usuarios (id) ON DELETE SET NULL
);

CREATE TABLE resenas (
	id INTEGER NOT NULL,
	clinica_id INTEGER NOT NULL,
	autor_id INTEGER,
	calificacion INTEGER NOT NULL,
	comentario TEXT,
	creado_en DATETIME NOT NULL,
	editado_en DATETIME,
	PRIMARY KEY (id),
	CONSTRAINT ck_resenas_calificacion CHECK (calificacion BETWEEN 1 AND 5),
	FOREIGN KEY(autor_id) REFERENCES usuarios (id) ON DELETE SET NULL,
	FOREIGN KEY(clinica_id) REFERENCES clinicas (id) ON DELETE CASCADE,
	CONSTRAINT uq_resenas_clinica_autor UNIQUE (clinica_id, autor_id)
);

CREATE TABLE servicios_clinica (
	id INTEGER NOT NULL,
	clinica_id INTEGER NOT NULL,
	categoria_id INTEGER NOT NULL,
	nombre VARCHAR(100) NOT NULL,
	descripcion VARCHAR(500),
	precio NUMERIC(10, 2),
	es_precio_desde BOOLEAN NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(categoria_id) REFERENCES categorias (id),
	FOREIGN KEY(clinica_id) REFERENCES clinicas (id) ON DELETE CASCADE
);

CREATE TABLE usuarios (
	id INTEGER NOT NULL,
	nombre VARCHAR(100) NOT NULL,
	email VARCHAR(254) NOT NULL,
	password_hash VARCHAR(100) NOT NULL,
	telefono VARCHAR(10),
	rol VARCHAR(10) NOT NULL,
	creado_en DATETIME NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT ck_usuarios_rol CHECK (rol IN ('dueno', 'clinica', 'admin'))
);

CREATE INDEX ix_clinicas_activa ON clinicas (activa);

CREATE INDEX ix_clinicas_lat_lng ON clinicas (lat, lng);

CREATE INDEX ix_clinicas_propietario_id ON clinicas (propietario_id);

CREATE INDEX ix_comentarios_autor_id ON comentarios (autor_id);

CREATE INDEX ix_comentarios_publicacion_id ON comentarios (publicacion_id);

CREATE INDEX ix_fotos_clinica_clinica_id ON fotos_clinica (clinica_id);

CREATE INDEX ix_horarios_clinica_id ON horarios (clinica_id);

CREATE INDEX ix_mascotas_dueno_id ON mascotas (dueno_id);

CREATE INDEX ix_publicaciones_autor_id ON publicaciones (autor_id);

CREATE INDEX ix_publicaciones_creado_en ON publicaciones (creado_en);

CREATE INDEX ix_resenas_autor_id ON resenas (autor_id);

CREATE INDEX ix_resenas_clinica_fecha ON resenas (clinica_id, creado_en);

CREATE INDEX ix_servicios_clinica_clinica_id ON servicios_clinica (clinica_id);

CREATE UNIQUE INDEX ix_usuarios_email ON usuarios (email);
