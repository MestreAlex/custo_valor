#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sistema de Stake Sizing para Value Bet
Calcula o tamanho ideal da aposta baseado em Kelly Criterion ajustado

Características:
- ROI médio do modelo: 18%
- Ajuste pela odd
- Ajuste pela confiança do modelo
- Aplicação de fractional Kelly (segurança)
- Limites mín/máx de stake
"""

import math

class StakeSizer:
    """Calcula stake sizing usando Kelly Criterion adaptado"""
    
    def __init__(self, bankroll=1000, roi_medio=0.18, kelly_fraction=0.25):
        """
        Args:
            bankroll: Saldo disponível para apostas
            roi_medio: ROI médio do modelo (0.18 = 18%)
            kelly_fraction: Fração do Kelly a usar (0.25 = 1/4 Kelly, mais seguro)
        """
        self.bankroll = bankroll
        self.roi_medio = roi_medio
        self.kelly_fraction = kelly_fraction
        
        # Parâmetros de controle
        self.stake_min = bankroll * 0.01  # Mínimo 1% do bankroll
        self.stake_max = bankroll * 0.05  # Máximo 5% do bankroll
        self.drawdown_limit = bankroll * 0.30  # Limite de drawdown 30%
        
    def calcular_probabilidade_implicita(self, odd):
        """
        Calcula a probabilidade implícita na odd
        
        Args:
            odd: Odd da aposta (ex: 2.50)
        
        Returns:
            float: Probabilidade (ex: 0.40 = 40%)
        """
        return 1 / odd
    
    def calcular_edge(self, odd, roi_esperado=None):
        """
        Calcula o edge real da aposta
        
        Edge = (Odd × Probabilidade Esperada) - 1
        
        Args:
            odd: Odd da aposta
            roi_esperado: ROI esperado para esta aposta (default = roi_medio)
        
        Returns:
            float: Edge (ex: 0.15 = 15% de edge)
        """
        if roi_esperado is None:
            roi_esperado = self.roi_medio
        
        # Edge = ROI × Probabilidade de ganho
        # Para odd X, probabilidade de ganho = 1/X
        prob_ganho = 1 / odd
        edge = roi_esperado * prob_ganho
        
        return edge
    
    def kelly_criterion(self, odd, probabilidade_vitoria, comissao=0.045):
        """
        Kelly Criterion clássico
        
        f* = (b×p - q) / b
        
        Onde:
        - b = odd - 1 (payoff)
        - p = probabilidade de vitória
        - q = 1 - p (probabilidade de derrota)
        - comissão = taxa da exchange (4.5%)
        
        Args:
            odd: Odd da aposta
            probabilidade_vitoria: Probabilidade de vitória (0-1)
            comissao: Taxa da exchange
        
        Returns:
            float: Fração do bankroll a apostar (Kelly puro)
        """
        b = odd - 1
        p = probabilidade_vitoria
        q = 1 - p
        
        # Aplicar desconto de comissão na odd
        b_efetivo = (odd - 1) * (1 - comissao)
        
        # Kelly
        kelly = (b_efetivo * p - q) / b_efetivo
        
        # Se Kelly for negativo, não apostar
        if kelly < 0:
            return 0
        
        return kelly
    
    def stake_sizing_adaptativo(self, odd, cfxgh=0.8, cfxga=0.8, bankroll_atual=None):
        """
        Stake sizing completo com ajustes
        
        Combina:
        1. Kelly Criterion
        2. Ajuste pela confiança do modelo (CF)
        3. Fração de Kelly (segurança)
        4. Ajuste pela odd (odds maiores = menos stake)
        
        Args:
            odd: Odd da aposta
            cfxgh: Coeficiente de confiança (xG Home) - 0 a 1
            cfxga: Coeficiente de confiança (xG Away) - 0 a 1
            bankroll_atual: Bankroll atual (default = self.bankroll)
        
        Returns:
            dict: Detalhes do stake sizing
        """
        if bankroll_atual is None:
            bankroll_atual = self.bankroll
        
        # 1. Calcular probabilidade implícita na odd
        prob_implicita = self.calcular_probabilidade_implicita(odd)
        
        # 2. Calcular confiança média (média geométrica)
        confianca_media = math.sqrt(cfxgh * cfxga) if cfxgh > 0 and cfxga > 0 else 0.5
        
        # 3. Ajustar probabilidade pela confiança
        # Se confiança alta, aumenta a probabilidade implícita (temos mais certeza)
        # Se confiança baixa, reduz (menos certeza)
        prob_ajustada = prob_implicita + (confianca_media - 0.5) * 0.1
        prob_ajustada = max(0.1, min(0.95, prob_ajustada))  # Limitar entre 10% e 95%
        
        # 4. Calcular Kelly
        kelly = self.kelly_criterion(odd, prob_ajustada)
        
        # 5. Aplicar Fractional Kelly (conservador)
        kelly_fracionado = kelly * self.kelly_fraction
        
        # 6. Calcular stake
        stake = kelly_fracionado * bankroll_atual
        
        # 7. Aplicar limites mín/máx
        stake = max(self.stake_min, min(self.stake_max, stake))
        
        # 8. Retornar detalhes
        return {
            'odd': odd,
            'bankroll': bankroll_atual,
            'prob_implicita': prob_implicita,
            'confianca_cf': confianca_media,
            'prob_ajustada': prob_ajustada,
            'edge': self.calcular_edge(odd),
            'kelly_puro': kelly,
            'kelly_fracionado': kelly_fracionado,
            'stake': stake,
            'roi_esperado_stake': stake * self.roi_medio,
            'limite_min': self.stake_min,
            'limite_max': self.stake_max,
            'pct_bankroll': (stake / bankroll_atual) * 100
        }
    
    def stake_por_faixa_odd(self, odd, cfxgh=0.8, cfxga=0.8, bankroll_atual=None):
        """
        Alternativa simplificada: Stakes por faixa de odd
        
        Odds maiores = menos stake (maior risco)
        Odds menores = mais stake (menor risco)
        
        Args:
            odd: Odd da aposta
            cfxgh: Coeficiente de confiança (xG Home)
            cfxga: Coeficiente de confiança (xG Away)
            bankroll_atual: Bankroll atual
        
        Returns:
            dict: Detalhes do stake
        """
        if bankroll_atual is None:
            bankroll_atual = self.bankroll
        
        confianca_media = math.sqrt(cfxgh * cfxga) if cfxgh > 0 and cfxga > 0 else 0.5
        
        # Tabela de stake por faixa de odd
        if odd < 1.5:
            pct_base = 0.05  # 5% do bankroll
        elif odd < 1.75:
            pct_base = 0.04  # 4%
        elif odd < 2.0:
            pct_base = 0.035  # 3.5%
        elif odd < 2.5:
            pct_base = 0.03  # 3%
        elif odd < 3.0:
            pct_base = 0.025  # 2.5%
        elif odd < 3.5:
            pct_base = 0.02  # 2%
        elif odd < 4.0:
            pct_base = 0.015  # 1.5%
        else:  # odd >= 4.0
            pct_base = 0.01  # 1%
        
        # Ajustar pela confiança do modelo
        # Confiança alta = aumenta stake (temos mais certeza)
        # Confiança baixa = reduz stake (menos certeza)
        pct_ajustado = pct_base * (0.7 + confianca_media * 0.6)  # Range 0.7 a 1.3
        
        stake = pct_ajustado * bankroll_atual
        
        return {
            'odd': odd,
            'bankroll': bankroll_atual,
            'faixa_odd': self._obter_faixa_odd(odd),
            'pct_base': pct_base * 100,
            'confianca_cf': confianca_media,
            'pct_ajustado': pct_ajustado * 100,
            'stake': stake,
            'roi_esperado_stake': stake * self.roi_medio
        }
    
    def _obter_faixa_odd(self, odd):
        """Retorna a faixa de odd em formato legível"""
        if odd < 1.5:
            return "Favorita (< 1.50)"
        elif odd < 1.75:
            return "Favorita (1.50-1.75)"
        elif odd < 2.0:
            return "Moderada (1.75-2.00)"
        elif odd < 2.5:
            return "Moderada (2.00-2.50)"
        elif odd < 3.0:
            return "Desafiante (2.50-3.00)"
        elif odd < 3.5:
            return "Desafiante (3.00-3.50)"
        elif odd < 4.0:
            return "Alta (3.50-4.00)"
        else:
            return "Muito Alta (> 4.00)"
    
    def gestao_risco(self, entradas_planejadas=20, stake_total_planejado=None):
        """
        Planejamento de gestão de risco
        
        Args:
            entradas_planejadas: Número de apostas planejadas
            stake_total_planejado: Total planejado em stake
        
        Returns:
            dict: Análise de risco
        """
        if stake_total_planejado is None:
            stake_total_planejado = self.stake_max * entradas_planejadas
        
        roi_esperado = stake_total_planejado * self.roi_medio
        perda_maxima = stake_total_planejado * (1 - self.roi_medio)  # Se tudo der errado
        
        return {
            'entradas_planejadas': entradas_planejadas,
            'stake_total': stake_total_planejado,
            'roi_esperado': roi_esperado,
            'pct_roi_bankroll': (roi_esperado / self.bankroll) * 100,
            'perda_maxima': perda_maxima,
            'pct_perda_bankroll': (perda_maxima / self.bankroll) * 100,
            'bankroll_apos_roi': self.bankroll + roi_esperado,
            'bankroll_apos_perda': self.bankroll - perda_maxima,
            'razao_risco_recompensa': roi_esperado / perda_maxima if perda_maxima > 0 else 0
        }


def main():
    """Exemplos de uso"""
    
    print("=" * 80)
    print("SISTEMA DE STAKE SIZING PARA VALUE BET")
    print("=" * 80)
    print()
    
    # Inicializar
    sizer = StakeSizer(bankroll=10000, roi_medio=0.18, kelly_fraction=0.25)
    
    print(f"Bankroll: R$ {sizer.bankroll:,.2f}")
    print(f"ROI Médio do Modelo: {sizer.roi_medio*100:.1f}%")
    print(f"Kelly Fraction: 1/{int(1/sizer.kelly_fraction)} Kelly")
    print()
    
    # Exemplo 1: Odd 1.95 com alta confiança
    print("-" * 80)
    print("EXEMPLO 1: Odd 1.95 (Favorita) - Alta Confiança")
    print("-" * 80)
    resultado1 = sizer.stake_sizing_adaptativo(odd=1.95, cfxgh=0.85, cfxga=0.80)
    print_resultado(resultado1)
    print()
    
    # Exemplo 2: Odd 3.50 com confiança média
    print("-" * 80)
    print("EXEMPLO 2: Odd 3.50 (Desafiante) - Confiança Média")
    print("-" * 80)
    resultado2 = sizer.stake_sizing_adaptativo(odd=3.50, cfxgh=0.65, cfxga=0.70)
    print_resultado(resultado2)
    print()
    
    # Exemplo 3: Comparação de faixas de odd
    print("-" * 80)
    print("COMPARAÇÃO: Stakes por Faixa de Odd (Confiança 75%)")
    print("-" * 80)
    odds_teste = [1.50, 1.75, 2.00, 2.50, 3.00, 3.50, 4.00, 5.00]
    cf = 0.75
    
    for odd in odds_teste:
        resultado = sizer.stake_por_faixa_odd(odd, cfxgh=cf, cfxga=cf)
        print(f"Odd {odd:5.2f} ({resultado['faixa_odd']:20s}) → "
              f"Stake: R$ {resultado['stake']:8.2f} ({resultado['pct_ajustado']:5.1f}% do bankroll)")
    
    print()
    
    # Exemplo 4: Gestão de risco
    print("-" * 80)
    print("PLANEJAMENTO DE GESTÃO DE RISCO")
    print("-" * 80)
    risco = sizer.gestao_risco(entradas_planejadas=20)
    print(f"Entradas Planejadas: {risco['entradas_planejadas']}")
    print(f"Total de Stake: R$ {risco['stake_total']:,.2f}")
    print(f"ROI Esperado (18%): R$ {risco['roi_esperado']:,.2f} ({risco['pct_roi_bankroll']:.1f}% do bankroll)")
    print(f"Perda Máxima (worst case): R$ {risco['perda_maxima']:,.2f} ({risco['pct_perda_bankroll']:.1f}% do bankroll)")
    print(f"Bankroll após sucesso: R$ {risco['bankroll_apos_roi']:,.2f}")
    print(f"Bankroll após perda: R$ {risco['bankroll_apos_perda']:,.2f}")
    print(f"Razão Risco/Recompensa: 1 : {risco['razao_risco_recompensa']:.2f}")
    print()


def print_resultado(resultado):
    """Formata e exibe resultado do stake sizing"""
    print(f"Odd: {resultado['odd']:.2f}")
    print(f"Bankroll: R$ {resultado['bankroll']:,.2f}")
    print()
    print(f"Análise:")
    print(f"  Probabilidade Implícita: {resultado['prob_implicita']*100:.1f}%")
    print(f"  Confiança do Modelo (CF): {resultado['confianca_cf']:.1%}")
    print(f"  Probabilidade Ajustada: {resultado['prob_ajustada']*100:.1f}%")
    print(f"  Edge: {resultado['edge']*100:.1f}%")
    print()
    print(f"Kelly Criterion:")
    print(f"  Kelly Puro: {resultado['kelly_puro']*100:.2f}%")
    print(f"  Kelly Fracionado (1/4): {resultado['kelly_fracionado']*100:.2f}%")
    print()
    print(f"✓ STAKE CALCULADO: R$ {resultado['stake']:.2f}")
    print(f"  ({resultado['pct_bankroll']:.1f}% do bankroll)")
    print(f"  ROI Esperado desta aposta: R$ {resultado['roi_esperado_stake']:.2f}")
    print(f"  Limites: R$ {resultado['limite_min']:.2f} - R$ {resultado['limite_max']:.2f}")


if __name__ == '__main__':
    main()
