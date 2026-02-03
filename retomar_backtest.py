#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para retomar o backtest do ponto onde parou
"""

import json
from pathlib import Path
import subprocess
import sys

def main():
    projeto_root = Path(__file__).parent
    relatorio_file = projeto_root / 'relatorio_backtest_automatico.json'
    acumulado_file = projeto_root / 'fixtures' / 'backtest_acumulado.json'
    
    print("\n" + "="*80)
    print("🔄 RETOMADOR DE BACKTEST")
    print("="*80 + "\n")
    
    # Verificar status
    if relatorio_file.exists():
        with open(relatorio_file, 'r', encoding='utf-8') as f:
            relatorio = json.load(f)
        
        print(f"📊 Status do backtest anterior:")
        print(f"   Ligas processadas: {relatorio['ligas_processadas']}/31")
        print(f"   Temporadas processadas: {relatorio['temporadas_processadas']}/217")
        print(f"   Sucessos: {len(relatorio['sucesso'])}")
        print(f"   Erros: {len(relatorio['erros'])}")
        
        if relatorio['sucesso']:
            ultima = relatorio['sucesso'][-1]
            print(f"\n   Última processada: {ultima['liga']} - {ultima['temporada']}")
            
            ligas_processadas = set(s['liga'] for s in relatorio['sucesso'])
            print(f"\n✓ Ligas completadas ({len(ligas_processadas)}):")
            print(f"  {', '.join(sorted(ligas_processadas))}")
    else:
        print("⚠️  Nenhum relatório anterior encontrado.")
        print("   O backtest será iniciado do início.\n")
    
    # Verificar arquivo acumulado
    if acumulado_file.exists():
        with open(acumulado_file, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        print(f"\n📁 Arquivo acumulado contém: {len(dados)} entradas")
    else:
        print(f"\n📁 Arquivo acumulado não existe (será criado)")
    
    print("\n" + "="*80)
    print("Opções:")
    print("="*80)
    print("1. Continuar do ponto anterior (retoma automaticamente)")
    print("2. Recomeçar do zero (limpa tudo e começa novamente)")
    print("3. Cancelar")
    print()
    
    while True:
        opcao = input("Escolha uma opção (1-3): ").strip()
        if opcao in ['1', '2', '3']:
            break
        print("Opção inválida. Tente novamente.")
    
    if opcao == '1':
        print("\n🚀 Continuando backtest...")
        print("   (O script detectará automaticamente o que já foi feito)\n")
        resultado = subprocess.run([sys.executable, 'executar_backtest_automatico.py'])
        return resultado.returncode
    
    elif opcao == '2':
        print("\n⚠️  LIMPANDO ARQUIVOS...")
        
        files_to_remove = [
            'fixtures/backtest_acumulado.json',
            'relatorio_backtest_automatico.json',
        ]
        
        # Remover resultados individuais
        backtest_dir = projeto_root / 'backtest'
        if backtest_dir.exists():
            for f in backtest_dir.glob('backtest_resultados_*.json'):
                f.unlink()
                print(f"   ✓ Deletado: {f.name}")
        
        # Remover outros arquivos
        for file in files_to_remove:
            path = projeto_root / file
            if path.exists():
                path.unlink()
                print(f"   ✓ Deletado: {file}")
        
        print("\n✅ Arquivos deletados. Iniciando backtest do zero...\n")
        resultado = subprocess.run([sys.executable, 'executar_backtest_automatico.py'])
        return resultado.returncode
    
    else:
        print("\n❌ Cancelado.")
        return 0

if __name__ == '__main__':
    sys.exit(main())
