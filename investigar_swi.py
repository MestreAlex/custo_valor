import pandas as pd

print("Investigando arquivo SWI.csv...")
print("="*60)

# Tentar diferentes encodings
encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']

for encoding in encodings:
    try:
        df = pd.read_csv('SWI.csv', encoding=encoding, on_bad_lines='skip')
        print(f"\n✓ Sucesso com encoding: {encoding}")
        print(f"  Total de linhas: {len(df)}")
        print(f"  Colunas: {len(df.columns)}")
        print(f"  Primeiras colunas: {list(df.columns[:5])}")
        break
    except Exception as e:
        print(f"\n✗ Erro com {encoding}: {str(e)[:100]}")
