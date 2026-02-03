#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para iniciar API e Servidor HTTP simultaneamente
"""

import subprocess
import os
from pathlib import Path

def main():
    pasta_backtest = Path(__file__).parent
    os.chdir(pasta_backtest)
    
    print("=" * 60)
    print("🚀 Iniciando Backtest com API e Servidor HTTP")
    print("=" * 60)
    
    # Iniciar API em background
    print("\n📡 Iniciando API Backtest (porta 5001)...")
    api_process = subprocess.Popen(['python', 'api_backtest.py'])
    
    # Iniciar Servidor HTTP em background
    print("🌐 Iniciando Servidor HTTP (porta 8001)...")
    http_process = subprocess.Popen(['python', '-m', 'http.server', '8001'])
    
    print("\n" + "=" * 60)
    print("✅ Servidores iniciados com sucesso!")
    print("=" * 60)
    print("\n📍 Acesse: http://localhost:8001/backtest.html")
    print("\n⚠️  Para parar, pressione CTRL+C")
    print("=" * 60)
    
    try:
        # Aguardar indefinidamente (até CTRL+C)
        api_process.wait()
        http_process.wait()
    except KeyboardInterrupt:
        print("\n\n⏹️  Parando servidores...")
        api_process.terminate()
        http_process.terminate()
        api_process.wait()
        http_process.wait()
        print("✅ Servidores parados com sucesso!")

if __name__ == '__main__':
    main()
