#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Monitor de progresso de backtests automáticos
Mostra estatísticas e permite retomar execução
"""

import json
from pathlib import Path
from datetime import datetime
from tabulate import tabulate

def listar_progresso():
    """Lista o progresso de backtests completados"""
    pasta_backtest = Path(__file__).parent / 'backtest'
    
    print("\n" + "="*100)
    print("📊 MONITOR DE BACKTESTS AUTOMÁTICOS")
    print("="*100)
    
    # Procurar arquivos de resultados
    arquivos_resultados = list(pasta_backtest.glob('backtest_resultados_*.json'))
    
    if not arquivos_resultados:
        print("Nenhum resultado de backtest encontrado.")
        return
    
    dados = []
    total_jogos = 0
    total_lucro = 0
    
    for arquivo in sorted(arquivos_resultados):
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                resultado = json.load(f)
            
            # Extrair informações do nome do arquivo
            nome = arquivo.stem  # Ex: backtest_resultados_E0_2024-25
            partes = nome.replace('backtest_resultados_', '').split('_')
            liga = partes[0]
            temporada = '_'.join(partes[1:])
            
            status = resultado.get('status', {})
            
            total_jogos += status.get('total_jogos', 0)
            total_lucro += status.get('lucro_total', 0)
            
            dados.append([
                liga,
                temporada,
                status.get('completo', False),
                status.get('total_jogos', 0),
                status.get('acertos', 0),
                status.get('erros', 0),
                f"{status.get('winrate', 0):.1f}%",
                f"{status.get('roi', 0):+.1f}%",
                f"{status.get('lucro_total', 0):+.2f}",
            ])
        except Exception as e:
            print(f"⚠️  Erro ao ler {arquivo.name}: {e}")
    
    # Exibir tabela
    if dados:
        headers = ['Liga', 'Temporada', 'Completo', 'Jogos', 'Acertos', 'Erros', 'Winrate', 'ROI', 'Lucro']
        print(tabulate(dados, headers=headers, tablefmt='grid'))
        print(f"\nTotal de jogos processados: {total_jogos}")
        print(f"Lucro total: {total_lucro:+.2f}")
        print(f"Número de temporadas completadas: {len(dados)}")
    
    # Verificar relatório final
    relatorio_file = Path(__file__).parent / 'relatorio_backtest_automatico.json'
    if relatorio_file.exists():
        with open(relatorio_file, 'r', encoding='utf-8') as f:
            relatorio = json.load(f)
        
        print(f"\n📈 RELATÓRIO FINAL:")
        print(f"  - Ligas processadas: {relatorio['ligas_processadas']}")
        print(f"  - Temporadas processadas: {relatorio['temporadas_processadas']}")
        print(f"  - Sucessos: {len(relatorio['sucesso'])}")
        print(f"  - Erros: {len(relatorio['erros'])}")
        
        if relatorio['data_fim']:
            data_inicio = datetime.fromisoformat(relatorio['data_inicio'])
            data_fim = datetime.fromisoformat(relatorio['data_fim'])
            tempo_total = (data_fim - data_inicio).total_seconds() / 60
            print(f"  - Tempo total: {tempo_total:.1f} minutos")
    
    print("="*100 + "\n")


def listar_erros():
    """Lista erros encontrados"""
    relatorio_file = Path(__file__).parent / 'relatorio_backtest_automatico.json'
    
    if not relatorio_file.exists():
        print("Nenhum relatório de erros encontrado.")
        return
    
    with open(relatorio_file, 'r', encoding='utf-8') as f:
        relatorio = json.load(f)
    
    if not relatorio['erros']:
        print("✅ Nenhum erro registrado!")
        return
    
    print("\n" + "="*100)
    print("⚠️  ERROS ENCONTRADOS")
    print("="*100)
    
    for erro in relatorio['erros']:
        print(f"❌ {erro['liga']} - {erro['temporada']}")
        print(f"   Erro: {erro['erro']}")
        print()


def main():
    """Função principal"""
    while True:
        print("\n" + "="*100)
        print("MENU DO MONITOR")
        print("="*100)
        print("1. Listar progresso de backtests")
        print("2. Listar erros")
        print("3. Ver arquivo acumulado")
        print("4. Sair")
        
        opcao = input("\nEscolha uma opção (1-4): ").strip()
        
        if opcao == '1':
            listar_progresso()
        elif opcao == '2':
            listar_erros()
        elif opcao == '3':
            arquivo = Path(__file__).parent / 'fixtures' / 'backtest_acumulado.json'
            if arquivo.exists():
                with open(arquivo, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                print(f"\n✅ Total de entradas no arquivo acumulado: {len(dados)}")
                
                # Agrupar por liga
                por_liga = {}
                for entrada in dados:
                    liga = entrada.get('liga', 'Desconhecida')
                    if liga not in por_liga:
                        por_liga[liga] = 0
                    por_liga[liga] += 1
                
                print("\nEntradas por liga:")
                for liga in sorted(por_liga.keys()):
                    print(f"  {liga}: {por_liga[liga]}")
            else:
                print("Arquivo não encontrado.")
        elif opcao == '4':
            break
        else:
            print("Opção inválida!")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSaindo...")
