#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

CRITERIOS = {
    'min_entradas': 75,
    'min_roi_pct': 5.0,
    'min_lucro': 20.0
}

try:
    response = requests.get('http://localhost:5001/api/backtest_acumulado')
    data = response.json()
    
    if not data.get('success'):
        print("❌ API retornou erro:", data.get('message'))
        exit(1)
    
    entradas = data.get('entradas', [])
    
    # Agrupar por liga e tipo de entrada
    combinacoes = {}
    
    for entrada in entradas:
        liga = entrada.get('liga', 'Desconhecida')
        entrada_tipo = entrada.get('entrada', 'UNKNOWN')
        
        chave = f"{liga}_{entrada_tipo}"
        
        if chave not in combinacoes:
            combinacoes[chave] = {
                'liga': liga,
                'tipo': entrada_tipo,
                'total': 0,
                'lucro': 0.0,
                'entradas_list': []
            }
        
        combinacoes[chave]['total'] += 1
        lp = float(entrada.get('lp', 0))
        combinacoes[chave]['lucro'] += lp
        combinacoes[chave]['entradas_list'].append(entrada)
    
    # Filtrar combinações que atendem aos critérios
    combinacoes_validadas = {}
    combinacoes_invalidas = {}
    
    for chave, dados in combinacoes.items():
        total = dados['total']
        lucro = dados['lucro']
        roi = (lucro / total * 100) if total > 0 else 0
        
        # Verificar critérios
        atende_quantidade = total >= CRITERIOS['min_entradas']
        atende_roi = roi >= CRITERIOS['min_roi_pct']
        atende_lucro = lucro >= CRITERIOS['min_lucro']
        
        dados['roi'] = roi
        
        if atende_quantidade and atende_roi and atende_lucro:
            combinacoes_validadas[chave] = dados
        else:
            combinacoes_invalidas[chave] = dados
    
    print()
    print("=" * 110)
    print("🎯 ANÁLISE DE COMBINAÇÕES VALIDADAS")
    print(f"   Critérios: Entradas >= {CRITERIOS['min_entradas']} | ROI >= {CRITERIOS['min_roi_pct']}% | Lucro >= {CRITERIOS['min_lucro']}")
    print("=" * 110)
    print()
    
    # Mostrar combinações validadas
    print("✅ COMBINAÇÕES VALIDADAS:")
    print("-" * 110)
    
    if combinacoes_validadas:
        for chave in sorted(combinacoes_validadas.keys()):
            dados = combinacoes_validadas[chave]
            print(f"   {dados['liga']:5} {dados['tipo']:6} | Entradas: {dados['total']:4} | ROI: {dados['roi']:6.2f}% | Lucro: {dados['lucro']:8.2f}")
    else:
        print("   ❌ Nenhuma combinação validada encontrada!")
    
    print()
    print("-" * 110)
    print(f"Total de combinações validadas: {len(combinacoes_validadas)}")
    print()
    
    # Mostrar combinações inválidas com motivos
    print("❌ COMBINAÇÕES INVÁLIDAS:")
    print("-" * 110)
    
    if combinacoes_invalidas:
        for chave in sorted(combinacoes_invalidas.keys()):
            dados = combinacoes_invalidas[chave]
            total = dados['total']
            lucro = dados['lucro']
            roi = dados['roi']
            
            motivos = []
            if total < CRITERIOS['min_entradas']:
                motivos.append(f"Entradas: {total}/{CRITERIOS['min_entradas']}")
            if roi < CRITERIOS['min_roi_pct']:
                motivos.append(f"ROI: {roi:.2f}%/{CRITERIOS['min_roi_pct']}%")
            if lucro < CRITERIOS['min_lucro']:
                motivos.append(f"Lucro: {lucro:.2f}/{CRITERIOS['min_lucro']}")
            
            motivo_texto = " | ".join(motivos)
            print(f"   {dados['liga']:5} {dados['tipo']:6} | {motivo_texto}")
    else:
        print("   ✅ Todas as combinações são válidas!")
    
    print()
    print("=" * 110)
    print("📊 RESUMO:")
    print(f"   Total de combinações: {len(combinacoes)}")
    print(f"   Combinações VALIDADAS: {len(combinacoes_validadas)}")
    print(f"   Combinações INVÁLIDAS: {len(combinacoes_invalidas)}")
    print("=" * 110)
    print()
    
    # Análise detalhada por critério não atendido
    print("📈 ANÁLISE DE CRITÉRIOS NÃO ATENDIDOS:")
    print("-" * 110)
    
    falha_entradas = sum(1 for d in combinacoes_invalidas.values() if d['total'] < CRITERIOS['min_entradas'])
    falha_roi = sum(1 for d in combinacoes_invalidas.values() if d['roi'] < CRITERIOS['min_roi_pct'])
    falha_lucro = sum(1 for d in combinacoes_invalidas.values() if d['lucro'] < CRITERIOS['min_lucro'])
    
    print(f"   Falham na quantidade de entradas (< {CRITERIOS['min_entradas']}): {falha_entradas}")
    print(f"   Falham no ROI (< {CRITERIOS['min_roi_pct']}%): {falha_roi}")
    print(f"   Falham no lucro mínimo (< {CRITERIOS['min_lucro']}): {falha_lucro}")
    print("=" * 110)
    print()

except requests.exceptions.ConnectionError:
    print("❌ Erro: Não consegui conectar à API em http://localhost:5001")
    print("   Verifique se o servidor está rodando: python servidor_api.py")
except Exception as e:
    print(f"❌ Erro: {e}")
