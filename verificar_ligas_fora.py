#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests

try:
    response = requests.get('http://localhost:5001/api/backtest_acumulado')
    data = response.json()
    
    entradas = data.get('entradas', [])
    
    # Todas as ligas do dataset
    todas_ligas = sorted(set(e.get('liga') for e in entradas))
    
    # Ligas com combinações validadas (do relatório)
    ligas_validadas = {
        'BRA', 'CHN', 'E0', 'E1', 'F1', 'F2', 'FIN', 'I2', 'IRL', 
        'JPN', 'MEX', 'N1', 'NOR', 'P1', 'POL', 'ROU', 'RUS', 'SP1', 
        'SP2', 'SWE', 'SWZ', 'T1', 'USA'
    }
    
    # Ligas que ficaram de fora
    ligas_fora = [l for l in todas_ligas if l not in ligas_validadas]
    
    print()
    print("=" * 80)
    print("📋 ANÁLISE DE LIGAS")
    print("=" * 80)
    print()
    print(f"Total de ligas: {len(todas_ligas)}")
    print(f"Ligas COM combinações validadas: {len(ligas_validadas)}")
    print(f"Ligas FORA (sem combinações validadas): {len(ligas_fora)}")
    print()
    
    if ligas_fora:
        print("❌ LIGAS SEM COMBINAÇÕES VALIDADAS (Critério: >= 75 entradas, >= 5% ROI, >= 20 lucro):")
        print("-" * 80)
        for i, liga in enumerate(sorted(ligas_fora), 1):
            total_entrada = sum(1 for e in entradas if e.get('liga') == liga)
            print(f"{i:2}. {liga:5} ({total_entrada:4} entradas no total)")
    else:
        print("✅ Todas as ligas têm pelo menos uma combinação validada!")
    
    print()
    print("=" * 80)
    print()

except Exception as e:
    print(f"❌ Erro: {e}")
