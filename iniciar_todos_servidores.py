#!/usr/bin/env python3
"""
Script para iniciar todos os servidores e APIs necessárias
Inicia:
1. servidor_api.py (porta 8000) - Páginas: proxima_rodada.html, jogos_salvos.html, analise_salvos.html
2. servidor_analise_backtest.py (porta 5001) - Páginas: backtest.html, backtest_salvos.html, backtest_resumo_entradas.html
3. Gera automaticamente os arquivos HTML necessários
"""

import subprocess
import sys
import time
import os
from pathlib import Path
import signal

# Configurar codificação UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Definir cores para terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

BASE_DIR = Path(__file__).parent
PROCESSES = []

def print_header():
    """Exibe o cabeçalho do script"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("="*80)
    print("🚀 INICIALIZADOR DE SERVIDORES - SISTEMA DE ANÁLISE DE FUTEBOL")
    print("="*80)
    print(f"{Colors.END}\n")
    print(f"{Colors.BLUE}Servidores que serão inicializados:{Colors.END}")
    print(f"  ✓ servidor_api.py (porta 8000)")
    print(f"    - Proxima Rodada: http://localhost:8000/proxima_rodada.html")
    print(f"    - Jogos Salvos: http://localhost:8000/jogos_salvos.html")
    print(f"    - Análise Salvos: http://localhost:8000/analise_salvos.html")
    print(f"\n  ✓ servidor_analise_backtest.py (porta 5001)")
    print(f"    - Backtest: http://localhost:5001/backtest.html")
    print(f"    - Backtests Salvos: http://localhost:5001/backtest_salvos.html")
    print(f"    - Resumo Entradas: http://localhost:5001/backtest_resumo_entradas.html")
    print()

def gerar_paginas_html():
    """Gera os arquivos HTML necessários"""
    print(f"{Colors.YELLOW}[PREPARAÇÃO]{Colors.END} Gerando páginas HTML...")
    
    scripts = [
        ('buscar_proxima_rodada.py', 'proxima_rodada.html'),
        ('salvar_jogo.py gerar', 'jogos_salvos.html'),
        ('salvar_jogo.py gerar_analise', 'analise_salvos.html'),
    ]
    
    for script, arquivo in scripts:
        try:
            print(f"  → Gerando {arquivo}...", end=" ")
            cmd = f"python {script}" if "gerar" not in script else f"python {script}"
            result = subprocess.run(cmd, shell=True, cwd=BASE_DIR, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print(f"{Colors.GREEN}OK{Colors.END}")
            else:
                print(f"{Colors.YELLOW}Aviso{Colors.END}")
        except Exception as e:
            print(f"{Colors.YELLOW}Erro: {str(e)}{Colors.END}")

def iniciar_servidor(script_name, porta, descricao):
    """Inicia um servidor em processo separado"""
    try:
        print(f"{Colors.BLUE}[INICIANDO]{Colors.END} {descricao} (porta {porta})...", end=" ")
        
        # Criar processo
        process = subprocess.Popen(
            [sys.executable, script_name],
            cwd=BASE_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        PROCESSES.append((process, script_name, porta))
        
        # Aguardar para validar se iniciou
        time.sleep(2)
        
        if process.poll() is None:  # Processo ainda está rodando
            print(f"{Colors.GREEN}✓ OK{Colors.END}")
            return True
        else:
            print(f"{Colors.RED}✗ FALHOU{Colors.END}")
            stderr = process.stderr.read() if process.stderr else "Erro desconhecido"
            print(f"  Erro: {stderr[:100]}")
            return False
            
    except Exception as e:
        print(f"{Colors.RED}✗ ERRO: {str(e)}{Colors.END}")
        return False

def aguardar_entrada():
    """Aguarda entrada do usuário para parar os servidores"""
    try:
        input(f"\n{Colors.GREEN}✓ Todos os servidores iniciados com sucesso!{Colors.END}\n"
              f"Pressione {Colors.BOLD}ENTER{Colors.END} para parar os servidores...\n")
    except KeyboardInterrupt:
        print()

def parar_servidores():
    """Para todos os servidores em execução"""
    print(f"\n{Colors.YELLOW}[ENCERRANDO]{Colors.END} Parando servidores...")
    
    for process, nome, porta in PROCESSES:
        try:
            print(f"  → Parando {nome} (porta {porta})...", end=" ")
            process.terminate()
            try:
                process.wait(timeout=5)
                print(f"{Colors.GREEN}OK{Colors.END}")
            except subprocess.TimeoutExpired:
                print(f"{Colors.YELLOW}Forçando encerramento{Colors.END}")
                process.kill()
        except Exception as e:
            print(f"{Colors.RED}Erro: {str(e)}{Colors.END}")
    
    print(f"\n{Colors.CYAN}Todos os servidores foram encerrados.{Colors.END}\n")

def main():
    """Função principal"""
    print_header()
    
    # Gerar páginas HTML
    gerar_paginas_html()
    print()
    
    # Iniciar servidores
    print(f"{Colors.BOLD}{Colors.CYAN}Iniciando Servidores:{Colors.END}\n")
    
    sucesso = True
    
    # Servidor API (porta 8000)
    if not iniciar_servidor('servidor_api.py', 8000, 'Servidor API'):
        sucesso = False
    
    # Servidor Backtest (porta 5001)
    if not iniciar_servidor('servidor_analise_backtest.py', 5001, 'Servidor de Backtest'):
        sucesso = False
    
    if sucesso and len(PROCESSES) > 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}")
        print("="*80)
        print("✓ SISTEMA TOTALMENTE OPERACIONAL")
        print("="*80)
        print(f"{Colors.END}\n")
        
        print(f"{Colors.BOLD}Páginas disponíveis:{Colors.END}\n")
        print(f"  📄 Próxima Rodada")
        print(f"     {Colors.CYAN}http://localhost:8000/proxima_rodada.html{Colors.END}")
        print(f"\n  📄 Jogos Salvos")
        print(f"     {Colors.CYAN}http://localhost:8000/jogos_salvos.html{Colors.END}")
        print(f"\n  📄 Análise Salvos")
        print(f"     {Colors.CYAN}http://localhost:8000/analise_salvos.html{Colors.END}")
        print(f"\n  📊 Backtest")
        print(f"     {Colors.CYAN}http://localhost:5001/backtest.html{Colors.END}")
        print(f"\n  📊 Backtests Salvos")
        print(f"     {Colors.CYAN}http://localhost:5001/backtest_salvos.html{Colors.END}")
        print(f"\n  📊 Resumo de Entradas")
        print(f"     {Colors.CYAN}http://localhost:5001/backtest_resumo_entradas.html{Colors.END}")
        print()
        
        # Aguardar entrada do usuário
        aguardar_entrada()
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ Erro ao iniciar os servidores{Colors.END}\n")
        sys.exit(1)
    
    # Parar servidores
    parar_servidores()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Interrupção detectada...{Colors.END}")
        parar_servidores()
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Erro fatal: {str(e)}{Colors.END}\n")
        parar_servidores()
        sys.exit(1)
