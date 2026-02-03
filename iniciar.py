#!/usr/bin/env python3
"""
Script de inicialização do sistema de análise de jogos
"""
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

def menu():
    """Exibe menu principal"""
    print("\n" + "="*80)
    print("Sistema de Análise de Jogos de Futebol")
    print("="*80)
    print("\n[1] Buscar próximos jogos e gerar análise")
    print("[2] Iniciar servidor API (necessário para salvar jogos)")
    print("[3] Iniciar servidor HTTP para visualizar páginas")
    print("[4] Gerar página de jogos salvos")
    print("[5] Abrir página de próximos jogos no navegador")
    print("[6] Abrir página de jogos salvos no navegador")
    print("[7] Iniciar tudo (API + HTTP + abrir páginas)")
    print("[0] Sair\n")
    
    opcao = input("Escolha uma opção: ")
    return opcao

def buscar_jogos():
    """Busca próximos jogos"""
    print("\nBuscando próximos jogos e gerando análise...")
    subprocess.run([sys.executable, "buscar_proxima_rodada.py"])
    input("\nPressione Enter para continuar...")

def iniciar_api():
    """Inicia servidor API"""
    print("\nIniciando servidor API em http://localhost:5000...")
    print("Pressione Ctrl+C para parar o servidor")
    subprocess.run([sys.executable, "servidor_api.py"])

def iniciar_http():
    """Inicia servidor HTTP"""
    print("\nIniciando servidor HTTP em http://localhost:8000...")
    print("Pressione Ctrl+C para parar o servidor")
    subprocess.run([sys.executable, "-m", "http.server", "8000"], cwd="fixtures")

def gerar_salvos():
    """Gera página de jogos salvos"""
    print("\nGerando página de jogos salvos...")
    subprocess.run([sys.executable, "salvar_jogo.py", "gerar"])
    input("\nPressione Enter para continuar...")

def abrir_proximos():
    """Abre página de próximos jogos"""
    print("\nAbrindo página de próximos jogos...")
    webbrowser.open("http://localhost:8000/proxima_rodada.html")
    time.sleep(2)

def abrir_salvos():
    """Abre página de jogos salvos"""
    print("\nAbrindo página de jogos salvos...")
    webbrowser.open("http://localhost:8000/jogos_salvos.html")
    time.sleep(2)

def iniciar_tudo():
    """Inicia todos os servidores e abre páginas"""
    print("\nIniciando servidor API...")
    api_proc = subprocess.Popen([sys.executable, "servidor_api.py"])
    time.sleep(3)
    
    print("Iniciando servidor HTTP...")
    http_proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", "8000"],
        cwd="fixtures"
    )
    time.sleep(3)
    
    print("Abrindo páginas no navegador...")
    webbrowser.open("http://localhost:8000/proxima_rodada.html")
    time.sleep(2)
    webbrowser.open("http://localhost:8000/jogos_salvos.html")
    
    print("\n" + "="*80)
    print("Sistema iniciado com sucesso!")
    print("\nServidor API: http://localhost:5000")
    print("Servidor HTTP: http://localhost:8000")
    print("\nPáginas abertas no navegador.")
    print("Pressione Ctrl+C para parar os servidores.")
    print("="*80)
    
    try:
        # Manter processos rodando
        api_proc.wait()
        http_proc.wait()
    except KeyboardInterrupt:
        print("\n\nParando servidores...")
        api_proc.terminate()
        http_proc.terminate()
        print("Servidores parados.")

def main():
    """Loop principal"""
    while True:
        try:
            opcao = menu()
            
            if opcao == "1":
                buscar_jogos()
            elif opcao == "2":
                iniciar_api()
            elif opcao == "3":
                iniciar_http()
            elif opcao == "4":
                gerar_salvos()
            elif opcao == "5":
                abrir_proximos()
            elif opcao == "6":
                abrir_salvos()
            elif opcao == "7":
                iniciar_tudo()
            elif opcao == "0":
                print("\nSaindo...")
                break
            else:
                print("\nOpção inválida!")
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\nSaindo...")
            break

if __name__ == "__main__":
    main()
