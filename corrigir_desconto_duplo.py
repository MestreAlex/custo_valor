"""
Script para corrigir valores de L/P que tiveram desconto duplo aplicado.

Situação:
- Valores antigos: lp_antigo = lp_original * 0.955 * 0.955 (desconto duplo = 0.912025)
- Valores novos: lp_novo = lp_original * 0.955 (desconto único correto)

Solução:
1. Desfazer desconto duplo: lp_original = lp_antigo / 0.912025
2. Aplicar desconto correto: lp_corrigido = lp_original * 0.955
"""
import json
from pathlib import Path

JOGOS_FILE = Path('fixtures/jogos_salvos.json')
BACKUP_FILE = Path('fixtures/jogos_salvos.json.backup')

def corrigir_desconto_duplo():
    """Corrige todos os valores de LP que tiveram desconto duplo"""
    
    # Fazer backup antes de modificar
    if JOGOS_FILE.exists():
        import shutil
        shutil.copy(JOGOS_FILE, BACKUP_FILE)
        print(f"✓ Backup criado: {BACKUP_FILE}")
    
    # Carregar dados
    if not JOGOS_FILE.exists():
        print("✗ Arquivo jogos_salvos.json não encontrado")
        return False
    
    with open(JOGOS_FILE, 'r', encoding='utf-8') as f:
        jogos = json.load(f)
    
    DESCONTO_DUPLO = 0.912025  # 0.955 * 0.955
    DESCONTO_CORRETO = 0.955
    total_corrigidos = 0
    
    print(f"\nAnalisando {len(jogos)} jogos...\n")
    print(f"{'DATA':<12} {'LIGA':<5} {'HOME':<20} {'AWAY':<20} {'LP ANTIGO':<12} {'LP CORRIGIDO':<12} {'DIFERENÇA':<12}")
    print("-" * 101)
    
    for jogo in jogos:
        if 'LP' in jogo:
            try:
                lp_antigo = float(jogo['LP'])
                
                # Se LP > 0, precisamos corrigir
                if lp_antigo > 0:
                    # Desfazer desconto duplo
                    lp_original = lp_antigo / DESCONTO_DUPLO
                    # Aplicar desconto correto
                    lp_corrigido = lp_original * DESCONTO_CORRETO
                    
                    diferenca = lp_corrigido - lp_antigo
                    
                    # Mostrar antes e depois
                    print(f"{jogo.get('DATA', ''):<12} {jogo.get('LIGA', ''):<5} {str(jogo.get('HOME', '')):<20} {str(jogo.get('AWAY', '')):<20} {lp_antigo:<12.4f} {lp_corrigido:<12.4f} {diferenca:<12.4f}")
                    
                    # Atualizar valor
                    jogo['LP'] = round(lp_corrigido, 2)
                    total_corrigidos += 1
            except (ValueError, TypeError) as e:
                print(f"✗ Erro ao processar LP para jogo {jogo.get('DATA')} {jogo.get('HOME')} vs {jogo.get('AWAY')}: {e}")
    
    print("-" * 101)
    print(f"\n✓ {total_corrigidos} valores de LP foram corrigidos")
    
    # Salvar dados corrigidos
    with open(JOGOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(jogos, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Arquivo {JOGOS_FILE} atualizado com sucesso")
    print(f"✓ Backup preservado em: {BACKUP_FILE}")
    
    return True

if __name__ == '__main__':
    print("=" * 101)
    print("CORRETOR DE DESCONTO DUPLO - jogos_salvos.json")
    print("=" * 101)
    
    corrigir_desconto_duplo()
    
    print("\n✓ Processo concluído!")
    print("  - Novos salvamentos utilizarão desconto único (4.5%)")
    print("  - Dados antigos foram corrigidos para o valor esperado")
