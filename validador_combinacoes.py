#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

def carregar_combinacoes_validadas():
    """
    Carrega as 73 combinações validadas do relatório.
    Retorna um set com as combinações no formato: 'LIGA_TIPO_DXG'
    
    Returns:
        set: Conjunto de combinações validadas
    """
    combinacoes = set()
    
    # As 73 combinações validadas extraídas do relatório
    combinacoes_data = [
        ('IRL', 'AWAY', 'LA'),
        ('BRA', 'AWAY', 'FA'),
        ('CHN', 'AWAY', 'FA'),
        ('IRL', 'HOME', 'LH'),
        ('SWZ', 'AWAY', 'LH'),
        ('FIN', 'AWAY', 'LA'),
        ('CHN', 'HOME', 'FH'),
        ('E0', 'AWAY', 'FA'),
        ('JPN', 'AWAY', 'LH'),
        ('N1', 'AWAY', 'FA'),
        ('SWE', 'AWAY', 'FA'),
        ('RUS', 'AWAY', 'LH'),
        ('P1', 'AWAY', 'FA'),
        ('F1', 'AWAY', 'FA'),
        ('CHN', 'HOME', 'LH'),
        ('JPN', 'AWAY', 'LA'),
        ('SWE', 'AWAY', 'LA'),
        ('BRA', 'HOME', 'FH'),
        ('IRL', 'AWAY', 'FA'),
        ('JPN', 'AWAY', 'FA'),
        ('BRA', 'HOME', 'LH'),
        ('FIN', 'HOME', 'LH'),
        ('I2', 'AWAY', 'FA'),
        ('CHN', 'AWAY', 'EQ'),
        ('SP1', 'AWAY', 'FA'),
        ('IRL', 'HOME', 'FH'),
        ('NOR', 'HOME', 'FH'),
        ('ROU', 'AWAY', 'FA'),
        ('SWZ', 'AWAY', 'FA'),
        ('USA', 'AWAY', 'LA'),
        ('NOR', 'AWAY', 'LH'),
        ('SWE', 'HOME', 'FH'),
        ('CHN', 'AWAY', 'LA'),
        ('T1', 'HOME', 'LH'),
        ('E0', 'AWAY', 'LH'),
        ('BRA', 'AWAY', 'LH'),
        ('P1', 'HOME', 'FH'),
        ('SP2', 'AWAY', 'LA'),
        ('POL', 'AWAY', 'FA'),
        ('ROU', 'HOME', 'LH'),
        ('F1', 'AWAY', 'LA'),
        ('USA', 'AWAY', 'FA'),
        ('SWE', 'HOME', 'LH'),
        ('NOR', 'AWAY', 'LA'),
        ('BRA', 'AWAY', 'LA'),
        ('T1', 'AWAY', 'FA'),
        ('E1', 'HOME', 'FH'),
        ('FIN', 'HOME', 'EQ'),
        ('BRA', 'AWAY', 'EQ'),
        ('E1', 'AWAY', 'FA'),
        ('E1', 'AWAY', 'EQ'),
        ('SWE', 'AWAY', 'EQ'),
        ('E0', 'HOME', 'LH'),
        ('E1', 'AWAY', 'LA'),
        ('N1', 'HOME', 'FH'),
        ('N1', 'AWAY', 'LA'),
        ('E0', 'AWAY', 'LA'),
        ('F1', 'HOME', 'FH'),
        ('SP1', 'HOME', 'FH'),
        ('JPN', 'AWAY', 'EQ'),
        ('USA', 'HOME', 'FH'),
        ('SWE', 'HOME', 'EQ'),
        ('E0', 'HOME', 'FH'),
        ('JPN', 'HOME', 'FH'),
        ('POL', 'HOME', 'LH'),
        ('F2', 'HOME', 'FH'),
        ('JPN', 'HOME', 'LH'),
        ('MEX', 'AWAY', 'EQ'),
        ('T1', 'HOME', 'FH'),
        ('MEX', 'HOME', 'LH'),
        ('USA', 'AWAY', 'EQ'),
        ('I2', 'HOME', 'FH'),
        ('SP2', 'HOME', 'FH'),
    ]
    
    for liga, tipo, dxg in combinacoes_data:
        chave = f"{liga}_{tipo}_{dxg}"
        combinacoes.add(chave)
    
    return combinacoes


def validar_jogo(liga, tipo_entrada, dxg, combinacoes_validadas):
    """
    Valida se uma combinação específica está nas combinações validadas.
    
    Args:
        liga (str): Código da liga (ex: 'BRA', 'E0')
        tipo_entrada (str): Tipo de entrada ('HOME' ou 'AWAY')
        dxg (str): Tipo de DxG ('FH', 'LH', 'EQ', 'LA', 'FA')
        combinacoes_validadas (set): Set com as combinações validadas
    
    Returns:
        bool: True se a combinação está validada, False caso contrário
    """
    chave = f"{liga}_{tipo_entrada}_{dxg}"
    return chave in combinacoes_validadas


if __name__ == "__main__":
    # Teste
    combinacoes = carregar_combinacoes_validadas()
    print(f"Total de combinações validadas: {len(combinacoes)}")
    print(f"Exemplo de combinação: BRA_AWAY_FA - {'Validada' if 'BRA_AWAY_FA' in combinacoes else 'Não validada'}")
