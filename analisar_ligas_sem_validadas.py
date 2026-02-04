#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

try:
    response = requests.get('http://localhost:5001/api/backtest_acumulado')
    data = response.json()
    
    if not data.get('success'):
        print("❌ API retornou erro:", data.get('message'))
        exit(1)
    
    entradas = data.get('entradas', [])
    
    # Agrupar por liga
    ligas = {}
    for entrada in entradas:
        liga = entrada.get('liga', 'Desconhecida')
        if liga not in ligas:
            ligas[liga] = {
                'total': 0,
                'home_validadas': 0,
                'away_validadas': 0
            }
        
        ligas[liga]['total'] += 1
        
        # Uma entrada é considerada "validada" se tem LP > 0
        lp = float(entrada.get('lp', 0))
        entrada_tipo = entrada.get('entrada', '')
        
        if lp > 0:
            if entrada_tipo == 'HOME':
                ligas[liga]['home_validadas'] += 1
            elif entrada_tipo == 'AWAY':
                ligas[liga]['away_validadas'] += 1
    
    print()
    print("=" * 90)
    print("📊 ANÁLISE DE LIGAS POR ENTRADAS VALIDADAS (LP > 0)")
    print("=" * 90)
    print()
    
    ligas_sem = []
    
    for liga in sorted(ligas.keys()):
        total = ligas[liga]['total']
        home = ligas[liga]['home_validadas']
        away = ligas[liga]['away_validadas']
        validadas = home + away
        
        if validadas == 0:
            ligas_sem.append(liga)
            print(f"❌ {liga:20} | Total: {total:4} | HOME: {home:3} | AWAY: {away:3}")
        else:
            pct = (validadas / total * 100)
            print(f"✅ {liga:20} | Total: {total:4} | HOME: {home:3} | AWAY: {away:3} | {pct:5.1f}%")
    
    print()
    print("=" * 90)
    print(f"📌 LIGAS SEM NENHUMA ENTRADA VALIDADA ({len(ligas_sem)}):")
    print("=" * 90)
    
    if ligas_sem:
        for i, liga in enumerate(sorted(ligas_sem), 1):
            total = ligas[liga]['total']
            print(f"{i:2}. {liga:30} ({total:4} entradas no total)")
    else:
        print("✅ Todas as ligas têm pelo menos uma entrada validada!")
    
    print()
    print("=" * 90)
    print("📊 RESUMO:")
    print(f"   Total de ligas: {len(ligas)}")
    print(f"   Ligas COM entradas validadas: {len(ligas) - len(ligas_sem)}")
    print(f"   Ligas SEM entradas validadas: {len(ligas_sem)}")
    print("=" * 90)
    print()

except requests.exceptions.ConnectionError:
    print("❌ Erro: Não consegui conectar à API em http://localhost:5001")
    print("   Verifique se o servidor está rodando: python servidor_api.py")
except Exception as e:
    print(f"❌ Erro: {e}")
