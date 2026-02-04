#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from datetime import datetime

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
    
    # Agrupar por liga, tipo e dxg
    combinacoes = {}
    
    for entrada in entradas:
        liga = entrada.get('liga', 'Desconhecida')
        entrada_tipo = entrada.get('entrada', 'UNKNOWN')
        dxg = entrada.get('dxg', 'EQ')
        
        chave = f"{liga}_{entrada_tipo}_{dxg}"
        
        if chave not in combinacoes:
            combinacoes[chave] = {
                'liga': liga,
                'tipo': entrada_tipo,
                'dxg': dxg,
                'total': 0,
                'lucro': 0.0,
                'acertos': 0
            }
        
        combinacoes[chave]['total'] += 1
        lp = float(entrada.get('lp', 0))
        combinacoes[chave]['lucro'] += lp
        if lp > 0:
            combinacoes[chave]['acertos'] += 1
    
    # Filtrar combinações que atendem aos critérios
    combinacoes_validadas = []
    
    for chave, dados in combinacoes.items():
        total = dados['total']
        lucro = dados['lucro']
        roi = (lucro / total * 100) if total > 0 else 0
        winrate = (dados['acertos'] / total * 100) if total > 0 else 0
        
        # Verificar critérios
        atende_quantidade = total >= CRITERIOS['min_entradas']
        atende_roi = roi >= CRITERIOS['min_roi_pct']
        atende_lucro = lucro >= CRITERIOS['min_lucro']
        
        if atende_quantidade and atende_roi and atende_lucro:
            combinacoes_validadas.append({
                'liga': dados['liga'],
                'tipo': dados['tipo'],
                'dxg': dados['dxg'],
                'total': total,
                'lucro': lucro,
                'roi': roi,
                'winrate': winrate
            })
    
    # Ordenar por ROI decrescente
    combinacoes_validadas.sort(key=lambda x: x['roi'], reverse=True)
    
    # Salvar em arquivo
    with open('RELATORIO_COMBINACOES_VALIDADAS.txt', 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        f.write("📊 RELATÓRIO - COMBINAÇÕES VALIDADAS\n")
        f.write("=" * 100 + "\n")
        f.write("Critérios Aplicados:\n")
        f.write(f"  - Quantidade de entradas >= {CRITERIOS['min_entradas']}\n")
        f.write(f"  - ROI >= {CRITERIOS['min_roi_pct']}%\n")
        f.write(f"  - Lucro mínimo >= {CRITERIOS['min_lucro']}\n")
        f.write("\n")
        f.write(f"Total de Combinações Qualificadas: {len(combinacoes_validadas)}\n")
        f.write("=" * 100 + "\n\n")
        
        if combinacoes_validadas:
            f.write("Nº   Liga         Tipo   DxG   Entradas   Lucro      ROI %      Winrate % \n")
            f.write("-" * 100 + "\n")
            
            for idx, combo in enumerate(combinacoes_validadas, 1):
                f.write(f"{idx:<4} {combo['liga']:<13} {combo['tipo']:<6} {combo['dxg']:<5} "
                       f"{combo['total']:<10} {combo['lucro']:<10.2f} {combo['roi']:<10.2f} "
                       f"{combo['winrate']:<.2f}\n")
            
            f.write("\n" + "=" * 100 + "\n")
            f.write("📈 ESTATÍSTICAS GERAIS:\n")
            f.write(f"Total de combinações qualificadas: {len(combinacoes_validadas)}\n\n")
            
            # Distribuição por tipo
            tipos = {}
            for combo in combinacoes_validadas:
                tipos[combo['tipo']] = tipos.get(combo['tipo'], 0) + 1
            
            f.write("Distribuição por Tipo:\n")
            for tipo in sorted(tipos.keys()):
                f.write(f"  {tipo}: {tipos[tipo]} entradas\n")
            
            f.write("\n")
            
            # Distribuição por DxG
            dxgs = {}
            for combo in combinacoes_validadas:
                dxgs[combo['dxg']] = dxgs.get(combo['dxg'], 0) + 1
            
            f.write("Distribuição por DxG:\n")
            for dxg in sorted(dxgs.keys()):
                f.write(f"  {dxg}: {dxgs[dxg]} entradas\n")
            
            f.write("\n")
            
            # Distribuição por Liga
            ligas = {}
            for combo in combinacoes_validadas:
                ligas[combo['liga']] = ligas.get(combo['liga'], 0) + 1
            
            f.write("Distribuição por Liga:\n")
            for liga in sorted(ligas.keys()):
                f.write(f"  {liga}: {ligas[liga]} entradas\n")
        else:
            f.write("❌ NENHUMA combinação atende aos critérios especificados!\n")
        
        f.write("\n" + "=" * 100 + "\n")
    
    # Exibir no console
    print()
    print("=" * 100)
    print("📊 RELATÓRIO - COMBINAÇÕES VALIDADAS")
    print("=" * 100)
    print("Critérios Aplicados:")
    print(f"  - Quantidade de entradas >= {CRITERIOS['min_entradas']}")
    print(f"  - ROI >= {CRITERIOS['min_roi_pct']}%")
    print(f"  - Lucro mínimo >= {CRITERIOS['min_lucro']}")
    print()
    print(f"Total de Combinações Qualificadas: {len(combinacoes_validadas)}")
    print("=" * 100)
    print()
    
    if combinacoes_validadas:
        print("Nº   Liga         Tipo   DxG   Entradas   Lucro      ROI %      Winrate %")
        print("-" * 100)
        
        for idx, combo in enumerate(combinacoes_validadas, 1):
            print(f"{idx:<4} {combo['liga']:<13} {combo['tipo']:<6} {combo['dxg']:<5} "
                  f"{combo['total']:<10} {combo['lucro']:<10.2f} {combo['roi']:<10.2f} "
                  f"{combo['winrate']:<.2f}")
        
        print()
        print("=" * 100)
        print("✅ Relatório salvo em: RELATORIO_COMBINACOES_VALIDADAS.txt")
    else:
        print("❌ NENHUMA combinação atende aos critérios especificados!")
    
    print("=" * 100)
    print()

except requests.exceptions.ConnectionError:
    print("❌ Erro: Não consegui conectar à API em http://localhost:5001")
    print("   Verifique se o servidor está rodando: python servidor_api.py")
except Exception as e:
    print(f"❌ Erro: {e}")
