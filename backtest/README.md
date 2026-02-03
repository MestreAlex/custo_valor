# Backtest - Sistema Multi-Liga

## 📋 Resumo

Este é um sistema de backtest para testar a estratégia de **Value Bets** em múltiplas ligas de futebol. O sistema funciona com dados de 31 ligas diferentes ao redor do mundo.

## 🏆 Ligas Disponíveis

### Europa
- **B1**: Bélgica - Primeira Divisão
- **D1**: Alemanha - Bundesliga
- **D2**: Alemanha - Segunda Divisão
- **E0**: Inglaterra - Premier League (padrão)
- **E1**: Inglaterra - Championship
- **F1**: França - Ligue 1
- **F2**: França - Ligue 2
- **G1**: Grécia - Super League
- **I1**: Itália - Serie A
- **I2**: Itália - Serie B
- **N1**: Holanda - Eredivisie
- **P1**: Portugal - Primeira Liga
- **SP1**: Espanha - La Liga
- **SP2**: Espanha - Segunda Divisão
- **T1**: Turquia - Super Lig
- **AUT**: Áustria - Bundesliga
- **DNK**: Dinamarca - Superligaen
- **FIN**: Finlândia - Veikkausliiga
- **IRL**: Irlanda - Premier Division
- **POL**: Polônia - Ekstraklasa
- **ROU**: Romênia - Liga I
- **RUS**: Rússia - RPL
- **SWE**: Suécia - Allsvenskan
- **SWZ**: Suíça - Super Liga

### Outros Continentes
- **ARG**: Argentina - Super Liga
- **BRA**: Brasil - Serie A
- **CHN**: China - Super League
- **JPN**: Japão - J-League
- **MEX**: México - Liga MX
- **NOR**: Noruega - Eliteserien
- **USA**: EUA - MLS

## 🚀 Como Usar

### 1. Iniciar a API
```bash
cd backtest
python api_backtest.py
```

### 2. Acessar a Interface
```
http://localhost:8001/backtest.html
```

### 3. Selecionar a Liga
- Na caixa "Liga", escolha a liga desejada
- O sistema recarrega automaticamente com os dados da liga selecionada

### 4. Processar Rodadas
- **Processar Próxima Rodada**: Analisa a próxima rodada e identifica value bets
- **Processar Todas as Rodadas**: Executa o backtest completo automaticamente
- **Resetar Backtest**: Retorna ao início (sem dados processados)

## 📊 Dados e Estrutura

### Arquivos de Dados
- **`{LIGA}_completo_original.csv`**: Arquivo original com todos os jogos (incluindo 2024/2025)
- **`{LIGA}_treino.csv`**: Arquivo de treino com dados até 2023/2024 (temporadas anteriores)
- **`backtest_resultados_{LIGA}.json`**: Resultados salvos do backtest para cada liga

### Estrutura de Dados
```
backtest/
├── api_backtest.py              # API Flask
├── backtest_engine.py           # Motor do backtest
├── backtest.html                # Interface web
├── {LIGA}_completo_original.csv # Dados originais (31 ligas)
├── {LIGA}_treino.csv            # Dados de treino (31 ligas)
└── backtest_resultados_{LIGA}.json  # Resultados (31 ligas)
```

## 🔍 Filtros Disponíveis

### Na Página de Backtest
- **DxG**: Filtra por categoria (FH, LH, EQ, LA, FA)
- **Entrada**: HOME ou AWAY
- **L/P**: Positivo ou Negativo
- **ODD CASA**: Range de odds (mínimo e máximo)
- **ODD VISIT**: Range de odds (mínimo e máximo)

## 📈 Estatísticas

O sistema calcula automaticamente:
- **Rodada Atual**: Número da rodada processada
- **Total de Entradas**: Quantidade de value bets identificados
- **Win Rate**: Percentual de acertos
- **ROI**: Retorno sobre investimento
- **Lucro Total**: Lucro/prejuízo acumulado
- **Acertos**: Quantidade de bets vencedores
- **Erros**: Quantidade de bets perdedores

## 🛠️ Scripts Auxiliares

### preparar_ligas.py
Prepara os arquivos de treino para todas as ligas:
```bash
python preparar_ligas.py
```

### copiar_originais.py
Copia os arquivos originais para a pasta backtest:
```bash
python copiar_originais.py
```

## 💡 Funcionamento da Estratégia

### Value Bet
Identifica quando a odd da Bet365 é maior que a odd calculada + 10% de margem:
```
Value Bet = B365_Odd > (Calculated_Odd × 1.1)
```

### Cálculo de xG (Expected Goals)
- Usa média dos últimos 10 jogos
- `xG = (Goals Scored + Opponent Goals Conceded) / 2`

### DxG (Difference in Expected Goals)
Categorias:
- **FH** (Favorite Home): xGH - xGA ≥ 0.75
- **LH** (Light Home): xGH - xGA ≥ 0.35
- **EQ** (Equal): -0.35 ≤ xGH - xGA ≤ 0.35
- **LA** (Light Away): xGH - xGA > -0.75
- **FA** (Favorite Away): xGH - xGA < -0.75

## ⚙️ Configuração Técnica

- **Backend**: Python 3.12.6 com Flask e CORS
- **Frontend**: HTML5, CSS3, JavaScript vanilla
- **Dados**: Pandas, NumPy, SciPy (Poisson distribution)
- **Porta API**: 5001
- **Porta HTTP**: 8001

## 🔗 Endpoints da API

- `GET /api/backtest/ligas` - Lista ligas disponíveis
- `POST /api/backtest/selecionar-liga` - Seleciona uma liga
- `GET /api/backtest/status` - Status atual
- `POST /api/backtest/processar` - Processa próxima rodada
- `GET /api/backtest/entradas` - Lista entradas/resultados
- `POST /api/backtest/resetar` - Reseta o backtest

## 📝 Notas Importantes

1. **Dados de Treino**: Apenas dados até 2023/2024 são usados para calcular xG
2. **Temporada de Teste**: 2024/2025 é usada para testar a estratégia
3. **Cada Liga tem seu Backtest**: Os resultados são salvos separadamente por liga
4. **Filtros Dinâmicos**: As estatísticas se atualizam quando filtros são aplicados

## 🐛 Troubleshooting

### API não inicia
```bash
# Verificar se porta 5001 está em uso
netstat -ano | findstr :5001
```

### Dados não carregam
- Verificar se os arquivos CSV estão na pasta correta
- Executar `preparar_ligas.py` e `copiar_originais.py`

### Erro ao processar rodada
- Verificar logs do Flask
- Garantir que a API está rodando
- Conferir se os dados estão formatados corretamente

## 📞 Suporte

Para reportar problemas ou sugerir melhorias, verifique:
1. Se a API está rodando (`python api_backtest.py`)
2. Se os dados estão carregados corretamente
3. Se a porta 5001 está disponível
