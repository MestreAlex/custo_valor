import pandas as pd
import os

def filtrar_dados_treino():
    """
    Remove jogos da temporada 2024/2025 e 2025/2026 para criar dataset de treino
    """
    arquivo_original = 'E0_completo_original.csv'
    arquivo_treino = 'E0_treino.csv'
    
    # Ler o arquivo completo
    df = pd.read_csv(arquivo_original)
    
    print(f"Total de jogos no arquivo original: {len(df)}")
    print(f"Temporadas presentes: {sorted(df['Season'].unique())}")
    
    # Filtrar apenas temporadas até 2023/2024
    df_treino = df[~df['Season'].isin(['2024/2025', '2025/2026'])].copy()
    
    print(f"\nTotal de jogos após filtrar temporadas 2024/2025 e 2025/2026: {len(df_treino)}")
    print(f"Temporadas no arquivo de treino: {sorted(df_treino['Season'].unique())}")
    
    # Salvar arquivo de treino
    df_treino.to_csv(arquivo_treino, index=False)
    print(f"\nArquivo de treino criado: {arquivo_treino}")
    
    return df, df_treino

if __name__ == '__main__':
    os.chdir(os.path.dirname(__file__))
    df_original, df_treino = filtrar_dados_treino()
