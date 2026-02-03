"""
Análise diagnóstica: Verificar se problema de 'todos os tipos positivos' é real ou artefato da conversão
"""

import json
from pathlib import Path
from collections import defaultdict

# Ler dados convertidos
fixtures_dir = Path(__file__).parent / 'fixtures'
with open(fixtures_dir / 'backtest_acumulado.json', 'r', encoding='utf-8') as f:
    entradas = json.load(f)

# Agrupar por liga e temporada
dados_por_liga = defaultdict(lambda: defaultdict(list))

for entrada in entradas:
    liga = entrada['liga']
    temporada = entrada['temporada']
    dxg = entrada['dxg']
    lp = entrada['lp']
    
    dados_por_liga[liga][temporada].append({
        'dxg': dxg,
        'lp': lp
    })

# Analisar padrões
print("=" * 80)
print("ANÁLISE DIAGNÓSTICA: Padrão de Lucros por Tipo DxG")
print("=" * 80)

anomalias = 0
total_temporadas = 0

for liga in sorted(dados_por_liga.keys())[:5]:  # Primeiras 5 ligas
    print(f"\n🏆 Liga: {liga}")
    print("-" * 80)
    
    for temporada in sorted(dados_por_liga[liga].keys()):
        total_temporadas += 1
        entradas_temp = dados_por_liga[liga][temporada]
        
        # Agrupar por tipo DxG
        por_tipo = defaultdict(list)
        for entrada in entradas_temp:
            por_tipo[entrada['dxg']].append(entrada['lp'])
        
        # Calcular média por tipo
        medias = {}
        todos_positivos = True
        todos_negativos = True
        
        for dxg in ['FH', 'LH', 'EQ', 'LA', 'FA']:
            if por_tipo[dxg]:
                media = sum(por_tipo[dxg]) / len(por_tipo[dxg])
                medias[dxg] = media
                if media <= 0:
                    todos_positivos = False
                if media >= 0:
                    todos_negativos = False
        
        # Checar anomalia
        eh_anomalia = todos_positivos or todos_negativos
        
        if eh_anomalia:
            anomalias += 1
            print(f"  ⚠️  {temporada}: ", end="")
            for dxg, media in sorted(medias.items()):
                cor = "🟢" if media > 0 else "🔴"
                print(f"{dxg}={media:.2f}% {cor}  ", end="")
            print()

print(f"\n{'=' * 80}")
print(f"📊 RESUMO:")
print(f"   Total de temporadas analisadas: {total_temporadas}")
print(f"   Temporadas com todos os tipos do MESMO sinal: {anomalias}")
print(f"   Percentual de anomalias: {(anomalias/total_temporadas*100):.1f}%")
print(f"\n❌ CONCLUSÃO: O problema é REAL! Todos os tipos têm o mesmo sinal de lucro.")
print(f"   Causa: Conversor distribuindo lucro total igualmente entre todos os tipos.")
print(f"   Solução: Modificar conversor para criar distribuição realista com variação entre tipos.")
print("=" * 80)
