#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
EXEMPLO: Como integrar Stake Sizing em analisar_proxima_rodada.py

Este arquivo mostra EXATAMENTE onde adicionar o stake sizing
Copie e cole as seções marcadas com <<<ADICIONAR>>> em seu arquivo
"""

# <<<ADICIONAR>>> No topo do arquivo, após imports:
from stake_sizing import StakeSizer
from integracao_stake_sizing import adicionar_stake_sizing_aos_jogos, gerar_resumo_stakes

# <<<ADICIONAR>>> Na função principal, após criar lista de jogos:

def analisar_proxima_rodada_com_stakes(liga, bankroll=10000, roi_medio=0.18):
    """
    Versão melhorada com stake sizing incluído
    
    Segue exatamente a lógica original, apenas adicionando stakes
    """
    
    # ... seu código original de análise ...
    
    # Após criar a lista 'jogos' com análise (com odd, cfxgh, cfxga):
    
    # <<<ADICIONAR>>> Estas linhas:
    jogos_com_stakes = adicionar_stake_sizing_aos_jogos(
        jogos,
        bankroll=bankroll,
        roi_medio=roi_medio
    )
    
    # <<<ADICIONAR>>> Adicionar resumo antes das tabelas:
    resumo_stakes = gerar_resumo_stakes(jogos_com_stakes)
    
    # <<<ADICIONAR>>> Renderizar resumo no HTML:
    resumo_html = f"""
    <div style="background-color: #e7f3ff; padding: 15px; margin: 15px 0; border-radius: 5px; border-left: 4px solid #007bff;">
        <h3 style="margin-top: 0;">💰 Resumo de Stakes para Próxima Rodada</h3>
        <table style="border-collapse: collapse; width: 100%;">
            <tr>
                <td style="padding: 10px; border: 1px solid #007bff;"><b>Total Planejado:</b></td>
                <td style="padding: 10px; border: 1px solid #007bff; color: #007bff; font-weight: bold;">
                    R$ {resumo_stakes['stake_total']:,.2f}
                </td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #007bff;"><b>Stakes: Mín - Máx</b></td>
                <td style="padding: 10px; border: 1px solid #007bff;">
                    R$ {resumo_stakes['stake_min']:,.2f} - R$ {resumo_stakes['stake_max']:,.2f}
                </td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #007bff;"><b>ROI Esperado (18%):</b></td>
                <td style="padding: 10px; border: 1px solid #007bff; color: #28a745; font-weight: bold;">
                    R$ {resumo_stakes['roi_esperado_total']:,.2f}
                </td>
            </tr>
        </table>
    </div>
    """
    
    # <<<ADICIONAR>>> Adicionar coluna de stake na tabela de jogos:
    # Na hora de renderizar cada linha da tabela, adicionar:
    
    for jogo in jogos_com_stakes:
        stake = jogo.get('stake_sugerido', 'N/A')
        stake_str = f"<td style='padding: 10px; text-align: center; font-weight: bold; color: #007bff;'>R$ {stake:.2f}</td>" \
                    if isinstance(stake, (int, float)) else "<td>N/A</td>"
        
        # Adicionar esta coluna à tabela:
        # Entre <td>odd</td> e <td>validado</td>
        # <th>Stake Sugerido</th>  # No header


# <<<EXEMPLO COMPLETO>>> Seção a adicionar na tabela HTML:

def renderizar_tabela_jogos_com_stakes(jogos_com_stakes):
    """
    Exemplo completo de como renderizar a tabela
    """
    html = """
    <table style="border-collapse: collapse; width: 100%; margin-top: 20px;">
        <thead>
            <tr style="background-color: #007bff; color: white;">
                <th style="padding: 12px; border: 1px solid #007bff; text-align: left;">Data</th>
                <th style="padding: 12px; border: 1px solid #007bff; text-align: left;">Jogo</th>
                <th style="padding: 12px; border: 1px solid #007bff; text-align: center;">Odd</th>
                <th style="padding: 12px; border: 1px solid #007bff; text-align: center;">CF xGH</th>
                <th style="padding: 12px; border: 1px solid #007bff; text-align: center;">CF xGA</th>
                <!-- <<<ADICIONAR>>> Esta coluna: -->
                <th style="padding: 12px; border: 1px solid #007bff; text-align: center;">💰 Stake Sugerido</th>
                <!-- Fim da adição -->
                <th style="padding: 12px; border: 1px solid #007bff; text-align: center;">Validado</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for jogo in jogos_com_stakes:
        data = jogo.get('data', 'N/A')
        nome = jogo.get('jogo', 'N/A')
        odd = jogo.get('odd', 0)
        cfxgh = jogo.get('cfxgh', 0)
        cfxga = jogo.get('cfxga', 0)
        validado = '✓' if jogo.get('validado') else '✗'
        
        # <<<ADICIONAR>>> Extrair stake:
        stake = jogo.get('stake_sugerido', 'N/A')
        if isinstance(stake, (int, float)):
            stake_str = f"<b style='color: #007bff;'>R$ {stake:.2f}</b>"
            bg = '#f0f8ff'  # Azul claro
        else:
            stake_str = 'N/A'
            bg = '#fff'
        
        html += f"""
        <tr style="background-color: {bg};">
            <td style="padding: 10px; border: 1px solid #ddd;">{data}</td>
            <td style="padding: 10px; border: 1px solid #ddd;">{nome}</td>
            <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">{odd:.2f}</td>
            <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">{cfxgh:.1%}</td>
            <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">{cfxga:.1%}</td>
            <!-- <<<ADICIONAR>>> Esta célula: -->
            <td style="padding: 10px; border: 1px solid #ddd; text-align: center; font-weight: bold;">
                {stake_str}
            </td>
            <!-- Fim da adição -->
            <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">{validado}</td>
        </tr>
        """
    
    html += """
        </tbody>
    </table>
    """
    
    return html


# <<<COPIAR E COLAR>>> Esta seção inteira no final do seu analisar_proxima_rodada.py:

if __name__ == '__main__':
    # Teste rápido
    print("✓ Imports de stake sizing configurados!")
    print("✓ Pronto para integração com analisar_proxima_rodada.py")
    
    # Teste com dados fictícios
    teste_jogos = [
        {
            'data': '2026-02-15',
            'jogo': 'Exemplo 1',
            'odd': 1.95,
            'cfxgh': 0.85,
            'cfxga': 0.80,
            'validado': True
        },
        {
            'data': '2026-02-15',
            'jogo': 'Exemplo 2',
            'odd': 3.50,
            'cfxgh': 0.65,
            'cfxga': 0.70,
            'validado': True
        }
    ]
    
    # Aplicar stake sizing
    jogos_com_stakes = adicionar_stake_sizing_aos_jogos(teste_jogos, bankroll=10000)
    
    # Renderizar tabela
    tabela = renderizar_tabela_jogos_com_stakes(jogos_com_stakes)
    
    # Salvar exemplo
    with open('exemplo_tabela_com_stakes.html', 'w', encoding='utf-8') as f:
        f.write(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Exemplo: Tabela com Stakes</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #007bff; }}
            </style>
        </head>
        <body>
            <h1>Exemplo: Como Integrar Stakes</h1>
            <p>Veja a coluna "💰 Stake Sugerido" na tabela abaixo:</p>
            {tabela}
        </body>
        </html>
        """)
    
    print("✓ Exemplo salvo: exemplo_tabela_com_stakes.html")
