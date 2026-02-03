import json

with open('fixtures/jogos_salvos.json', 'r', encoding='utf-8') as f:
    jogos = json.load(f)

resultados = [j for j in jogos if j.get('GH') is not None]

print(f'Total jogos com resultado: {len(resultados)}\n')

for i, jogo in enumerate(resultados[:5], 1):
    print(f'{i}. {jogo.get("HOME")} vs {jogo.get("AWAY")}')
    print(f'   Data: {jogo.get("DATA")}')
    print(f'   CFxGH: {jogo.get("CFxGH")}')
    print(f'   CFxGA: {jogo.get("CFxGA")}')
    print()
