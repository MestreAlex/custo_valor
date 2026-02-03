"""
Script para reverter valores de L/P para bruto (sem desconto).

Os valores foram aumentados em 4,5%, agora precisam voltar ao bruto.
Isso porque o desconto será aplicado apenas na exibição (páginas HTML via JavaScript)
"""
import json
from pathlib import Path

JOGOS_FILE = Path('fixtures/jogos_salvos.json')

def reverter_para_bruto():
    """Reverte todos os valores de LP para bruto (desfaz o desconto único)"""
    
    if not JOGOS_FILE.exists():
        print("✗ Arquivo jogos_salvos.json não encontrado")
        return False
    
    with open(JOGOS_FILE, 'r', encoding='utf-8') as f:
        jogos = json.load(f)
    
    DESCONTO_CORRETO = 0.955
    total_revertidos = 0
    
    print(f"\nAnalisando {len(jogos)} jogos...\n")
    print(f"{'DATA':<12} {'LIGA':<5} {'HOME':<20} {'AWAY':<20} {'LP COM DESC':<15} {'LP BRUTO':<15}")
    print("-" * 97)
    
    for jogo in jogos:
        if 'LP' in jogo:
            try:
                lp_com_desconto = float(jogo['LP'])
                
                # Se LP > 0, precisamos reverter
                if lp_com_desconto > 0:
                    # Desfazer desconto único para voltar ao bruto
                    lp_bruto = lp_com_desconto / DESCONTO_CORRETO
                    
                    # Mostrar antes e depois
                    print(f"{jogo.get('DATA', ''):<12} {jogo.get('LIGA', ''):<5} {str(jogo.get('HOME', '')):<20} {str(jogo.get('AWAY', '')):<20} {lp_com_desconto:<15.4f} {lp_bruto:<15.4f}")
                    
                    # Atualizar valor para bruto
                    jogo['LP'] = round(lp_bruto, 2)
                    total_revertidos += 1
            except (ValueError, TypeError) as e:
                print(f"✗ Erro ao processar LP para jogo {jogo.get('DATA')} {jogo.get('HOME')} vs {jogo.get('AWAY')}: {e}")
    
    print("-" * 97)
    print(f"\n✓ {total_revertidos} valores de LP foram revertidos para bruto")
    
    # Salvar dados revertidos
    with open(JOGOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(jogos, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Arquivo {JOGOS_FILE} atualizado")
    print(f"\n⚠ Desconto será aplicado apenas na exibição (HTML) via JavaScript")
    print(f"  - Valor salvo: bruto (sem desconto)")
    print(f"  - Valor exibido: com desconto de 4.5% (0.955)")
    
    return True

if __name__ == '__main__':
    print("=" * 97)
    print("REVERSOR PARA BRUTO - jogos_salvos.json")
    print("=" * 97)
    
    reverter_para_bruto()
    
    print("\n✓ Processo concluído!")
