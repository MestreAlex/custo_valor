#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para calcular se a entrada foi HOME ou AWAY baseado em:
- Se B365H (odd casa) > (ODD_H_CALC * 1,10) → entrada foi HOME
- Se B365A (odd visitante) > (ODD_A_CALC * 1,10) → entrada foi AWAY
"""

import json
from pathlib import Path
from datetime import datetime

def calcular_entrada(b365h, odd_h_calc, b365a, odd_a_calc):
    """
    Calcula o tipo de entrada baseado nas condições:
    - Se B365H > (ODD_H_CALC * 1.10) → HOME
    - Se B365A > (ODD_A_CALC * 1.10) → AWAY
    - Caso nenhuma condição seja atendida → vazio
    """
    if b365h is None or odd_h_calc is None or b365a is None or odd_a_calc is None:
        return ''
    
    limiar_h = odd_h_calc * 1.10
    limiar_a = odd_a_calc * 1.10
    
    if b365h > limiar_h:
        return 'HOME'
    elif b365a > limiar_a:
        return 'AWAY'
    else:
        return ''

def processar_jogos():
    """Processa todos os jogos e calcula/atualiza o campo BACK"""
    
    salvos_file = Path("fixtures/jogos_salvos.json")
    if not salvos_file.exists():
        print("Arquivo jogos_salvos.json não encontrado!")
        return False
    
    # Carregar jogos salvos
    with open(salvos_file, 'r', encoding='utf-8') as f:
        jogos_salvos = json.load(f)
    
    atualizados = 0
    for jogo in jogos_salvos:
        b365h = jogo.get('B365H')
        odd_h_calc = jogo.get('ODD_H_CALC')
        b365a = jogo.get('B365A')
        odd_a_calc = jogo.get('ODD_A_CALC')
        
        home = jogo.get('HOME', '-')
        away = jogo.get('AWAY', '-')
        data = jogo.get('DATA', '')
        
        entrada = calcular_entrada(b365h, odd_h_calc, b365a, odd_a_calc)
        
        if entrada:
            jogo['BACK'] = entrada
            atualizados += 1
            print(f"✓ {data} | {home} vs {away} | Entrada: {entrada}")
        else:
            jogo['BACK'] = ''
    
    # Salvar jogos atualizados
    with open(salvos_file, 'w', encoding='utf-8') as f:
        json.dump(jogos_salvos, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Total de {atualizados} jogos atualizados com entrada calculada")
    return True

if __name__ == '__main__':
    processar_jogos()
