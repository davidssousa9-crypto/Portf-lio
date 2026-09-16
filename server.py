import json
import os
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

import database

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PORT = 8000

COMMON_ARQUIVOS = {
    "/index.html", "/login.html", "/atividades.html", "/atividades.css", "/atividades.js",
    "/eixos.html", "/humanas.html", "/linguagens.html", "/matematica.html",
    "/natureza.html", "/ppe.html", "/senai.html", "/style.css", "/favicon.ico",
}


class Handler(BaseHTTPRequestHandler):

    def _enviar_arquivo(self, caminho):
        if caminho == "/":
            caminho = "/index.html"
        arquivo = os.path.normpath(BASE_DIR + caminho)
        if not arquivo.startswith(BASE_DIR):
            self._resposta(403, "text/plain", b"Proibido")
            return
        if os.path.isdir(arquivo) or not os.path.exists(arquivo):
            self._resposta(404, "text/plain", b"Arquivo nao encontrado")
            return
        ext = os.path.splitext(arquivo)[1]
        tipo = {
            ".html": "text/html",
            ".css": "text/css",
            ".js": "application/javascript",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".svg": "image/svg+xml",
            ".ico": "image/x-icon",
        }.get(ext, "application/octet-stream")
        with open(arquivo, "rb") as f:
            self._resposta(200, tipo, f.read())

    def _enviar_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _resposta(self, codigo, tipo, corpo):
        self.send_response(codigo)
        self._enviar_cors()
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", len(corpo))
        self.end_headers()
        self.wfile.write(corpo)

    def _json(self, dados, codigo=200):
        corpo = json.dumps(dados, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self._enviar_cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", len(corpo))
        self.end_headers()
        self.wfile.write(corpo)

    def do_OPTIONS(self):
        self.send_response(204)
        self._enviar_cors()
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        caminho = urlparse(self.path).path
        if caminho == "/api/usuarios":
            usuarios = [dict(u) for u in database.listar_usuarios()]
            self._json({"usuarios": usuarios})
            return
        self._enviar_arquivo(caminho)

    def do_POST(self):
        caminho = urlparse(self.path).path
        try:
            tamanho = int(self.headers.get("Content-Length", 0))
            corpo = json.loads(self.rfile.read(tamanho)) if tamanho else {}
        except Exception:
            self._json({"erro": "JSON invalido"}, 400)
            return

        if caminho == "/api/cadastro":
            nome = (corpo.get("nome") or "").strip()
            email = (corpo.get("email") or "").strip().lower()
            senha = corpo.get("senha") or ""
            if not nome or not email or not senha:
                self._json({"erro": "Preencha todos os campos"}, 400)
                return
            ok, resultado = database.inserir_usuario(nome, email, senha)
            if ok:
                self._json({"sucesso": True, "id": resultado})
            else:
                self._json({"erro": resultado}, 400)
            return

        if caminho == "/api/login":
            email = (corpo.get("email") or "").strip().lower()
            senha = corpo.get("senha") or ""
            usuario = database.verificar_login(email, senha)
            if usuario:
                self._json({"sucesso": True, "nome": usuario["nome"]})
            else:
                self._json({"erro": "Credenciais invalidas"}, 401)
            return

        self._json({"erro": "Rota nao encontrada"}, 404)

    def log_message(self, formato, *args):
        print("[%s] %s" % (self.address_string(), formato % args))


def main():
    database.criar_tabela()
    servidor = HTTPServer(("localhost", PORT), Handler)
    print("=" * 60)
    print(" Servidor rodando em: http://localhost:%d/login.html" % PORT)
    print(" Banco de dados: usuarios.db")
    print(" Pressione Ctrl+C para parar")
    print("=" * 60)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
        servidor.server_close()


if __name__ == "__main__":
    main()
