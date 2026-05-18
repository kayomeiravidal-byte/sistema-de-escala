#!/usr/bin/env python
"""
main.py - Ponto de entrada para o servidor web local
- Inicia o servidor Django com Waitress
- Abre o navegador automaticamente
- Porta fixa: 5000
"""

import os
import sys
import threading
import webbrowser
import socket

# Garante que o Django encontre o projeto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Configura o Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scheduling_system.settings")

# Importa o WSGI do Django
from scheduling_system.wsgi import application

# Configurações do servidor
HOST = "127.0.0.1"
PORT = 5000
URL = f"http://{HOST}:{PORT}"
BROWSER_DELAY = 2  # segundos


def is_port_in_use(port):
    """Verifica se a porta está em uso"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((HOST, port))
            return False
        except OSError:
            return True


def open_browser_once():
    """Abre o navegador automaticamente apenas uma vez"""
    try:
        # Tenta abrir o navegador
        browser = webbrowser.get()
        browser.open(URL, new=0, autoraise=True)
    except Exception as e:
        print(f"Aviso: Não foi possível abrir o navegador automaticamente: {e}")
        print(f"Por favor, abra manualmente: {URL}")


def start_server():
    """Inicia o servidor Waitress"""
    from waitress import serve
    
    print("=" * 50)
    print(f"🚀 Servidor iniciado com sucesso!")
    print(f"   URL: {URL}")
    print(f"   Porta: {PORT}")
    print("=" * 50)
    print("Pressione Ctrl+C para encerrar o servidor")
    print()
    
    # Serve o aplicativo Django
    serve(application, host=HOST, port=PORT)


def main():
    """Função principal"""
    # Verifica se a porta está em uso
    if is_port_in_use(PORT):
        print(f"⚠️  A porta {PORT} já está em uso!")
        print(f"   Tente fechar outros aplicativos que usem a porta {PORT}")
        print(f"   Ou mude a porta no código (variável PORT)")
        
        # Pergunta se quer continuar mesmo assim
        try:
            response = input("Deseja continuar mesmo assim? (s/n): ")
            if response.lower() != 's':
                return
        except EOFError:
            # Em ambiente não interativo, sai
            print("Encerrando...")
            return
    
    try:
        # Inicia o servidor em uma thread separada
        # O navegador abre após um pequeno delay
        timer = threading.Timer(BROWSER_DELAY, open_browser_once)
        timer.daemon = True
        timer.start()
        
        # Inicia o servidor principal
        start_server()
        
    except KeyboardInterrupt:
        print("\n👋 Servidor encerrado pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erro ao iniciar o servidor: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
