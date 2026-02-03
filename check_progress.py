import json

# Ler o relatório
with open('relatorio_backtest_automatico.json', 'r', encoding='utf-8') as f:
    rel = json.load(f)

print(f"📊 Status do backtest anterior:")
print(f"   Ligas processadas: {rel['ligas_processadas']}/31")
print(f"   Temporadas processadas: {rel['temporadas_processadas']}/217")
print(f"   Sucessos: {len(rel['sucesso'])}")
print(f"   Erros: {len(rel['erros'])}")

# Última entrada
if rel['sucesso']:
    ultima = rel['sucesso'][-1]
    print(f"\n   Última liga processada: {ultima['liga']} - {ultima['temporada']}")
    print(f"   Timestamp: {ultima['timestamp']}")

# Listar ligas processadas
ligas_processadas = set()
for item in rel['sucesso']:
    ligas_processadas.add(item['liga'])

print(f"\n✓ Ligas completadas ({len(ligas_processadas)}):")
print(f"   {', '.join(sorted(ligas_processadas))}")
