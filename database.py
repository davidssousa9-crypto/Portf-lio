import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "usuarios.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def criar_tabela():
    conn = get_connection()
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                senha TEXT NOT NULL,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def inserir_usuario(nome, email, senha):
    conn = get_connection()
    try:
        with conn:
            cur = conn.execute(
                "INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)",
                (nome, email, senha),
            )
        return True, cur.lastrowid
    except sqlite3.IntegrityError:
        return False, "E-mail já cadastrado"


def verificar_login(email, senha):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM usuarios WHERE email = ? AND senha = ?",
        (email, senha),
    ).fetchone()
    return row


def listar_usuarios():
    conn = get_connection()
    return conn.execute("SELECT * FROM usuarios ORDER BY id DESC").fetchall()
