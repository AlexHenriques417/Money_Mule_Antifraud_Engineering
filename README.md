#### Project de Antifraud Engineering

Tema: Identificação de Money Mule em Transações Financeiras — aplicação prática de métricas
de centralidade em grafos direcionados no contexto do Nubank/Pix.

Objetivo acadêmico: Demonstrar como Betweenness Centrality e análise de grafos podem
detectar contas intermediárias em cadeias de lavagem de dinheiro.

Aplicação prática: Código Python com NetworkX que modela transações Pix como grafo
direcionado e ponderado, identifica money mules por centralidade, e visualiza a rede antifraud.

#### Situação/ Dor/ Solução

Um money mule é uma conta bancária usada como intermediária para receber e repassar dinheiro
de origem ilícita, dificultando o rastreio. No contexto do Pix, essa cadeia acontece em segundos —
a janela para bloqueio é de aproximadamente 40 minutos. O grafo de transações é a única forma
eficaz de enxergar o padrão.

Somos o time de engenharia antifraud do Nubank. São 14h de uma sexta-feira. O sistema
processa 2 milhões de transações Pix por hora.

Identificamos R$4,2M movimentados em cadeia em 40 minutos. Nossas regras baseadas
em valor e frequência não detectaram — o dinheiro saiu antes do bloqueio.

Modelamos as transações como um grafo direcionado. Usamos Betweenness Centrality
para identificar contas que atuam como hub de repasse — os money mules

...
