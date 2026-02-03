import pandas as pd
import numpy as np

print("="*100)
print("ANÁLISE SIMPLIFICADA - POR QUE ALGUNS JOGOS FICAM 'PARCIAL'?")
print("="*100)

# Carregar dados
fixtures = pd.read_csv('fixtures/proxima_rodada_com_analise.csv')
historico = pd.read_csv('dados_ligas_new/ARG.csv')

arg_jogos = fixtures[fixtures['LIGA'] == 'ARG'].copy()

# Focar nos 6 jogos que estão parciais com ambos times existindo no histórico
casos = [
    ('San Lorenzo', 'Central Cordoba'),  
    ('Boca Juniors', 'Newells Old Boys'),
    ('Gimnasia L.P.', 'Aldosivi'),
    ('Defensa y Justicia', 'Estudiantes L.P.'),
    ('Tigre', 'Racing Club'),
    ('Argentinos Jrs', 'Belgrano'),
]

print("\nAnalisando o que o script analisar_proxima_rodada.py está recebendo:\n")

for home, away in casos:
    jogo = arg_jogos[(arg_jogos['HOME'] == home) & (arg_jogos['AWAY'] == away)]
    
    if len(jogo) == 0:
        print(f"ERRO: {home} vs {away} não encontrado!")
        continue
    
    jogo = jogo.iloc[0]
    
    # Verificar status reportado
    mcgh = jogo.get('MCGH')
    mvgh = jogo.get('MVGH')
    mcga = jogo.get('MCGA')
    mvga = jogo.get('MVGA')
    
    status = "OK"
    if pd.isna(mcgh) or pd.isna(mvgh):
        status = "FALTA HOME"
    if pd.isna(mcga) or pd.isna(mvga):
        if status == "OK":
            status = "FALTA AWAY"
        else:
            status = "FALTA AMBOS"
    
    print(f"{home} vs {away}")
    print(f"  Status: {status}")
    print(f"  MCGH={mcgh}, MVGH={mvgh}")
    print(f"  MCGA={mcga}, MVGA={mvga}")
    
    # Agora, vamos procurar manualmente o que deveria ter sido encontrado
    hist_home = historico[historico['Home'] == home]
    hist_away = historico[historico['Away'] == away]
    
    print(f"  Histórico {home}: {len(hist_home)} jogos como mandante")
    print(f"  Histórico {away}: {len(hist_away)} jogos como visitante")
    
    # Verificar os dados de custo/valor
    if len(hist_home) > 0:
        cgh_count = hist_home['CGH'].notna().sum()
        vgh_count = hist_home['VGH'].notna().sum()
        print(f"    {home}: CGH válidos={cgh_count}, VGH válidos={vgh_count}")
        if cgh_count > 0:
            print(f"    {home}: CGH média={hist_home['CGH'].mean():.4f}, VGH média={hist_home['VGH'].mean():.4f}")
    
    if len(hist_away) > 0:
        cga_count = hist_away['CGA'].notna().sum()
        vga_count = hist_away['VGA'].notna().sum()
        print(f"    {away}: CGA válidos={cga_count}, VGA válidos={vga_count}")
        if cga_count > 0:
            print(f"    {away}: CGA média={hist_away['CGA'].mean():.4f}, VGA média={hist_away['VGA'].mean():.4f}")
    
    print()

print("\n" + "="*100)
print("CONCLUSÃO PROVÁVEL")
print("="*100)
print("""
Os jogos parciais ocorrem porque a função calcular_medias_historicas() 
não encontra jogos no histórico que correspondam ao range de ±7% de 
probabilidade para aquele time.

Quando não encontra, ela retorna NaN em vez de usar uma média geral.

Isso deixa dados parciais (um lado tem cálculo, outro não) porque:
- Home pode ter jogos com a probabilidade certa (dentro do ±7%)
- Away pode NÃO ter jogos com a probabilidade certa (fora do ±7%)

E vice-versa.

A solução seria: quando não encontrar jogos no range ±7%, 
usar um fallback (média geral do time, ou expandir range).
""")
print("="*100)
