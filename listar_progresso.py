ligas = ['B1', 'D1', 'D2', 'E0', 'E1', 'F1', 'F2', 'G1', 'I1', 'I2', 'N1', 'P1', 'SP1', 'SP2', 'T1', 'ARG', 'AUT', 'BRA', 'CHN', 'DNK', 'FIN', 'IRL', 'JPN', 'MEX', 'NOR', 'POL', 'ROU', 'RUS', 'SWE', 'SWZ', 'USA']

processed = ['AUT', 'B1', 'BRA', 'CHN', 'D1', 'D2', 'DNK', 'E0', 'E1', 'F1', 'F2', 'FIN', 'G1', 'I1', 'I2', 'IRL', 'JPN', 'MEX', 'N1', 'NOR', 'P1', 'POL', 'ROU', 'RUS', 'SP1', 'SP2']

# SP2 só tem 1 de 7 temporadas completadas
print(f"✓ Ligas completadas: {len(processed)}/31")
print(f"\n⚠️ Liga incompleta:")
print(f"   SP2 - Precisa de 6 temporadas mais (apenas 2020/2021 foi concluída)")

remaining = [l for l in ligas if l not in processed]
print(f"\n📌 Ligas não iniciadas ({len(remaining)}):")
for i, liga in enumerate(remaining, 1):
    print(f"   {i}. {liga}")

print(f"\n🔄 Para continuar do ponto onde parou:")
print(f"   1. Simplesmente execute: python executar_backtest_automatico.py")
print(f"   2. O script verificará cada arquivo e pulará as temporadas já completadas")
print(f"   3. Continuará a partir de SP2 2021/2022")
