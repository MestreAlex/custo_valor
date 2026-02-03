import json
import sys
sys.path.insert(0, 'backtest')
from backtest_engine import BacktestEngine
from datetime import datetime

# Carregar arquivo original
with open('fixtures/backtest_acumulado.json', 'r', encoding='utf-8') as f:
    dados = json.load(f)

print(f"✓ Carregados {len(dados)} registros")

# Criar um engine temporário para detectar temporada
# Usar primeiro jogo para detectar
engine = None

# Processar cada jogo e adicionar temporada
for i, jogo in enumerate(dados):
    if 'temporada' not in jogo:  # Só processar se não tiver temporada
        data_str = jogo['data']
        
        try:
            # Parse data format: DD/MM/YYYY
            data_obj = datetime.strptime(data_str, '%d/%m/%Y')
            ano = data_obj.year
            mes = data_obj.month
            
            # Detectar temporada baseado no mês
            # Temporadas normalmente: setembro(9) a maio(5)
            # 2025-26: setembro 2025 a maio 2026
            # 2024-25: setembro 2024 a maio 2025
            # etc
            
            if mes >= 9:  # setembro em diante
                temporada = f"{ano}-{str(ano+1)[-2:]}"
            else:  # janeiro a maio
                temporada = f"{ano-1}-{str(ano)[-2:]}"
            
            jogo['temporada'] = temporada
            
            if (i + 1) % 100 == 0:
                print(f"  {i+1}: {data_str} → {temporada}")
        except Exception as e:
            print(f"✗ Erro ao processar {jogo}: {e}")

# Salvar arquivo atualizado
with open('fixtures/backtest_acumulado.json', 'w', encoding='utf-8') as f:
    json.dump(dados, f, ensure_ascii=False, indent=2)

print(f"\n✓ Arquivo atualizado com sucesso! {len(dados)} registros processados")

# Contar por temporada
from collections import Counter
temporadas = Counter(jogo.get('temporada', 'SEM TEMPORADA') for jogo in dados)
print("\nDistribuição por temporada:")
for temp, count in sorted(temporadas.items()):
    print(f"  {temp}: {count} jogos")
