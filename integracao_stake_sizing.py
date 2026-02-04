#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Integração de Stake Sizing com Análise de Próxima Rodada
Adiciona cálculo automático de stake sugerido para cada jogo
"""

import json
from stake_sizing import StakeSizer

def adicionar_stake_sizing_aos_jogos(jogos_analise, bankroll=10000, roi_medio=0.18):
    """
    Adiciona stake sizing a cada jogo analisado
    
    Args:
        jogos_analise: Lista de jogos com análise (dicts)
        bankroll: Bankroll disponível
        roi_medio: ROI médio do modelo
    
    Returns:
        Lista de jogos com stake sizing adicionado
    """
    sizer = StakeSizer(bankroll=bankroll, roi_medio=roi_medio, kelly_fraction=0.25)
    
    jogos_com_stake = []
    
    for jogo in jogos_analise:
        # Copiar jogo original
        jogo_novo = jogo.copy()
        
        # Pular se não tem dados necessários
        if 'odd' not in jogo or 'cfxgh' not in jogo or 'cfxga' not in jogo:
            jogo_novo['stake_sugerido'] = None
            jogo_novo['stake_info'] = None
            jogos_com_stake.append(jogo_novo)
            continue
        
        try:
            # Calcular stake
            stake_info = sizer.stake_sizing_adaptativo(
                odd=jogo['odd'],
                cfxgh=jogo.get('cfxgh', 0.5),
                cfxga=jogo.get('cfxga', 0.5),
                bankroll_atual=bankroll
            )
            
            # Adicionar ao jogo
            jogo_novo['stake_sugerido'] = round(stake_info['stake'], 2)
            jogo_novo['stake_info'] = {
                'pct_bankroll': round(stake_info['pct_bankroll'], 1),
                'roi_esperado': round(stake_info['roi_esperado_stake'], 2),
                'kelly_puro': round(stake_info['kelly_puro']*100, 2),
                'kelly_fracionado': round(stake_info['kelly_fracionado']*100, 2),
                'prob_ajustada': round(stake_info['prob_ajustada']*100, 1),
                'edge': round(stake_info['edge']*100, 1)
            }
        except Exception as e:
            jogo_novo['stake_sugerido'] = None
            jogo_novo['stake_info'] = {'erro': str(e)}
        
        jogos_com_stake.append(jogo_novo)
    
    return jogos_com_stake


def gerar_resumo_stakes(jogos_com_stake):
    """
    Gera resumo dos stakes calculados
    
    Args:
        jogos_com_stake: Jogos com stake_sugerido adicionado
    
    Returns:
        Dict com resumo
    """
    stakes = [j['stake_sugerido'] for j in jogos_com_stake if j.get('stake_sugerido')]
    
    if not stakes:
        return {
            'total_jogos': len(jogos_com_stake),
            'jogos_com_stake': 0,
            'stake_total': 0,
            'stake_medio': 0,
            'stake_min': 0,
            'stake_max': 0,
            'roi_esperado_total': 0
        }
    
    roi_esperados = [j['stake_info']['roi_esperado'] for j in jogos_com_stake 
                     if j.get('stake_info') and 'roi_esperado' in j['stake_info']]
    
    return {
        'total_jogos': len(jogos_com_stake),
        'jogos_com_stake': len(stakes),
        'stake_total': round(sum(stakes), 2),
        'stake_medio': round(sum(stakes) / len(stakes), 2) if stakes else 0,
        'stake_min': round(min(stakes), 2),
        'stake_max': round(max(stakes), 2),
        'roi_esperado_total': round(sum(roi_esperados), 2) if roi_esperados else 0
    }


def renderizar_tabela_html_com_stakes(jogos_com_stake, titulo="Análise de Próxima Rodada com Stakes"):
    """
    Renderiza tabela HTML com stakes sugeridos
    
    Args:
        jogos_com_stake: Jogos com stake_sugerido
        titulo: Título da tabela
    
    Returns:
        String HTML
    """
    resumo = gerar_resumo_stakes(jogos_com_stake)
    
    html = f"""
    <h2>{titulo}</h2>
    
    <div style="background-color: #f0f0f0; padding: 15px; margin: 15px 0; border-radius: 5px;">
        <h3>📊 Resumo de Stakes</h3>
        <table style="border-collapse: collapse; width: 100%;">
            <tr>
                <td style="padding: 8px; border: 1px solid #ccc;"><b>Total de Jogos:</b></td>
                <td style="padding: 8px; border: 1px solid #ccc;">{resumo['total_jogos']}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ccc;"><b>Jogos com Stakes:</b></td>
                <td style="padding: 8px; border: 1px solid #ccc;">{resumo['jogos_com_stake']}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ccc;"><b>💰 Stake Total Planejado:</b></td>
                <td style="padding: 8px; border: 1px solid #ccc; color: #007bff; font-weight: bold;">R$ {resumo['stake_total']:,.2f}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ccc;"><b>Stake Médio:</b></td>
                <td style="padding: 8px; border: 1px solid #ccc;">R$ {resumo['stake_medio']:,.2f}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ccc;"><b>Range (Mín - Máx):</b></td>
                <td style="padding: 8px; border: 1px solid #ccc;">R$ {resumo['stake_min']:,.2f} - R$ {resumo['stake_max']:,.2f}</td>
            </tr>
            <tr style="background-color: #d4edda;">
                <td style="padding: 8px; border: 1px solid #ccc;"><b>✓ ROI Esperado Total (18%):</b></td>
                <td style="padding: 8px; border: 1px solid #ccc; color: #155724; font-weight: bold;">R$ {resumo['roi_esperado_total']:,.2f}</td>
            </tr>
        </table>
    </div>
    
    <table style="border-collapse: collapse; width: 100%; margin-top: 15px;">
        <thead>
            <tr style="background-color: #007bff; color: white;">
                <th style="padding: 10px; border: 1px solid #007bff; text-align: left;">Data</th>
                <th style="padding: 10px; border: 1px solid #007bff; text-align: left;">Jogo</th>
                <th style="padding: 10px; border: 1px solid #007bff; text-align: center;">Odd</th>
                <th style="padding: 10px; border: 1px solid #007bff; text-align: center;">CF</th>
                <th style="padding: 10px; border: 1px solid #007bff; text-align: center;">💰 Stake Sugerido</th>
                <th style="padding: 10px; border: 1px solid #007bff; text-align: center;">ROI Esperado</th>
                <th style="padding: 10px; border: 1px solid #007bff; text-align: center;">Edge</th>
                <th style="padding: 10px; border: 1px solid #007bff; text-align: center;">Validado ✓</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for jogo in jogos_com_stake:
        data = jogo.get('data', 'N/A')
        jogo_nome = jogo.get('jogo', jogo.get('nome_jogo', 'N/A'))
        odd = jogo.get('odd', 0)
        cf = jogo.get('cfxgh', 0)
        stake = jogo.get('stake_sugerido', 'N/A')
        validado = '✓' if jogo.get('validado') else '✗'
        
        if jogo.get('stake_info') and 'roi_esperado' in jogo['stake_info']:
            roi = f"R$ {jogo['stake_info']['roi_esperado']:.2f}"
            edge = f"{jogo['stake_info']['edge']:.1f}%"
        else:
            roi = 'N/A'
            edge = 'N/A'
        
        stake_str = f"R$ {stake:.2f}" if isinstance(stake, (int, float)) else stake
        
        # Colorir linha baseado em stake
        bg_color = '#f9f9f9' if stake == 'N/A' else '#fff'
        if isinstance(stake, (int, float)) and stake > 0:
            if stake >= 300:
                bg_color = '#fff3cd'  # Amarelo para stakes altos
            elif stake >= 200:
                bg_color = '#d1ecf1'  # Azul para stakes médios
        
        html += f"""
            <tr style="background-color: {bg_color};">
                <td style="padding: 8px; border: 1px solid #ddd;">{data}</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{jogo_nome}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;"><b>{odd:.2f}</b></td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{cf:.1%}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center; font-weight: bold; color: #007bff;">{stake_str}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{roi}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{edge}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{validado}</td>
            </tr>
        """
    
    html += """
        </tbody>
    </table>
    """
    
    return html


# Exemplo de uso
if __name__ == '__main__':
    # Exemplo de jogos analisados
    jogos_exemplo = [
        {
            'data': '2026-02-15',
            'jogo': 'Flamengo vs Vasco',
            'odd': 1.95,
            'cfxgh': 0.85,
            'cfxga': 0.80,
            'validado': True
        },
        {
            'data': '2026-02-15',
            'jogo': 'Palmeiras vs São Paulo',
            'odd': 3.50,
            'cfxgh': 0.65,
            'cfxga': 0.70,
            'validado': True
        },
        {
            'data': '2026-02-16',
            'jogo': 'Grêmio vs Internacional',
            'odd': 2.75,
            'cfxgh': 0.75,
            'cfxga': 0.80,
            'validado': False
        }
    ]
    
    # Adicionar stakes
    jogos_com_stakes = adicionar_stake_sizing_aos_jogos(jogos_exemplo, bankroll=10000)
    
    # Exibir resumo
    resumo = gerar_resumo_stakes(jogos_com_stakes)
    print("📊 RESUMO DE STAKES")
    print(json.dumps(resumo, indent=2))
    
    # Exibir HTML
    html = renderizar_tabela_html_com_stakes(jogos_com_stakes)
    with open('exemplo_stakes.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("\n✓ HTML gerado: exemplo_stakes.html")
