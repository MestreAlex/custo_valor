import json

with open('fixtures/jogos_salvos.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

resultados = [j for j in data if j.get('GH') is not None and j.get('GA') is not None]

print(f"Total de jogos com resultado: {len(resultados)}\n")
print("Primeiros 10 exemplos de cálculos LP:\n")

for j in resultados[:10]:
    home = j['HOME']
    away = j['AWAY']
    gh = j['GH']
    ga = j['GA']
    b365h = j.get('B365H')
    b365a = j.get('B365A')
    odd_h_calc = j.get('ODD_H_CALC')
    odd_a_calc = j.get('ODD_A_CALC')
    lp = j.get('LP')
    
    resultado = "Home Win" if gh > ga else "Away Win" if ga > gh else "Draw"
    
    print(f"{home} {gh}x{ga} {away}")
    print(f"  Resultado: {resultado}")
    print(f"  B365: Home={b365h:.2f}, Away={b365a:.2f}")
    print(f"  ODD_CALC: Home={odd_h_calc:.2f}, Away={odd_a_calc:.2f}")
    print(f"  LP calculado: {lp}")
    print()
