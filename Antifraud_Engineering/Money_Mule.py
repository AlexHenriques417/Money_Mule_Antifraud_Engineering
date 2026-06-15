import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import numpy as np
from collections import defaultdict

# =============================================================================
# 1. CRIAÇÃO DOS GRAFOS
# =============================================================================

def criar_grafo_normal():
    """
    Grafo 1: Fluxo normal — transações legítimas sem padrão suspeito.
    Pares independentes e pequenos clusters sem hub central.
    """
    G = nx.DiGraph()
    transacoes = [
        # Cluster 1: pequenas compras cotidianas
        ("João",    "Mercado",   320),
        ("Maria",   "Mercado",   450),
        ("Carlos",  "Mercado",   280),
        # Cluster 2: pagamentos entre amigos
        ("Ana",     "Pedro",     750),
        ("Pedro",   "Bia",       200),
        # Cluster 3: negócios independentes
        ("Loja_A",  "Fornec_1",  3200),
        ("Loja_B",  "Fornec_2",  1800),
        # Cluster 4: transferências pontuais
        ("Tiago",   "Renata",    500),
        ("Paulo",   "Lucas",     900),
        ("Fernanda","Marcos",    650),
    ]
    for o, d, v in transacoes:
        G.add_edge(o, d, weight=v, amount=v)
    return G


def criar_grafo_fraude():
    """
    Grafo 2: Fluxo com money mules — vítimas → mules → hub → destino final.
    """
    G = nx.DiGraph()

    # Transações legítimas coexistindo com a fraude
    transacoes_legitimas = [
        ("Conta_A", "Conta_B", 500),
        ("Conta_B", "Conta_C", 300),
        ("Conta_D", "Conta_E", 1200),
    ]

    # Camada 0: vítimas → money mules (contas comprometidas)
    transacoes_roubo = [
        ("Vítima_1", "Mule_1",  18000),   # dispositivo clonado
        ("Vítima_2", "Mule_1",  15000),   # phishing bancário
        ("Vítima_3", "Mule_2",  22000),   # SIM swap
        ("Vítima_4", "Mule_2",  19500),   # acesso remoto
        ("Vítima_5", "Mule_3",  52500),   # engenharia social
    ]

    # Camada 1: money mules → hub de escalonamento
    transacoes_mule = [
        ("Mule_1", "Hub_Escal", 32500),
        ("Mule_2", "Hub_Escal", 41000),
        ("Mule_3", "Hub_Escal", 52000),
    ]

    # Camada 2: hub → destino final (saída do sistema)
    transacoes_saida = [
        ("Hub_Escal", "Dest_Final", 125000),
    ]

    todas = (transacoes_legitimas + transacoes_roubo
             + transacoes_mule + transacoes_saida)
    for o, d, v in todas:
        G.add_edge(o, d, weight=v, amount=v)
    return G

# =============================================================================
# 2. DETECÇÃO DE MONEY MULES — BETWEENNESS CENTRALITY
# =============================================================================

def detectar_money_mules(G, threshold=0.02):
    """
    Betweenness Centrality: CB(v) = Σ [σ(s,t,v) / σ(s,t)]
      σ(s,t)   = total de caminhos mínimos de s → t
      σ(s,t,v) = caminhos que passam por v

    Algoritmo de Brandes: O(VE + V²logV) para grafos ponderados.
    """
    centralidade = nx.betweenness_centrality(
        G, normalized=True, weight='weight'
    )
    mules = [n for n, c in centralidade.items() if c >= threshold]
    return mules, centralidade


# =============================================================================
# 3. MÉTRICAS ADICIONAIS
# =============================================================================

def calcular_metricas(G, mules):
    print("\n=== MÉTRICAS DOS SUSPEITOS ===")
    for mule in mules:
        vol_rec = sum(d['amount'] for _, _, d in G.in_edges(mule, data=True))
        vol_env = sum(d['amount'] for _, _, d in G.out_edges(mule, data=True))
        taxa = (vol_env / vol_rec * 100) if vol_rec > 0 else 0
        print(f"\n  {mule}")
        print(f"    Recebeu de {G.in_degree(mule)} conta(s)  → R${vol_rec:,.0f}")
        print(f"    Enviou p/ {G.out_degree(mule)} conta(s)  → R${vol_env:,.0f}")
        print(f"    Taxa de repasse: {taxa:.1f}%")

# =============================================================================
# 4. VISUALIZAÇÃO — DOIS GRAFOS LADO A LADO
# =============================================================================

def cor_no(no, mules, centralidade, threshold=0.02):
    c = centralidade.get(no, 0)
    if no in mules and ('Mule' in no):
        return '#E53935'          # vermelho — money mule
    elif 'Vitima' in no or 'Vítima' in no:
        return '#FF8F00'          # âmbar — vítima
    elif 'Dest_Final' in no or 'Destino' in no:
        return '#6A1B9A'          # roxo escuro — destino suspeito
    elif 'Hub' in no or 'Escal' in no:
        return '#C62828'          # vermelho escuro — hub
    elif c > 0.01:
        return '#F57F17'          # amarelo — moderadamente suspeito
    else:
        return '#1565C0'          # azul — conta normal


def tamanho_no(no, mules, centralidade):
    c = centralidade.get(no, 0)
    if no in mules or 'Hub' in no:
        return 750                # Reduzido de 900 para desaglomerar
    elif c > 0.01:
        return 550                # Reduzido de 650
    return 300                    # Reduzido de 400


def desenhar_grafo(ax, G, mules, centralidade, titulo, seed=42):
    # ALTERAÇÃO CRÍTICA: Aumentado 'k' de 2.2 para 4.5 e definidas 100 iterações 
    # para forçar os nós densos (como mulas e vítimas) a se espalharem bem na tela.
    pos = nx.spring_layout(G, k=4.5, iterations=100, seed=seed)

    cores    = [cor_no(n, mules, centralidade)   for n in G.nodes()]
    tamanhos = [tamanho_no(n, mules, centralidade) for n in G.nodes()]
    pesos    = [G[u][v].get('weight', 100) / 7000 for u, v in G.edges()]
    pesos    = [max(0.6, min(p, 4.0)) for p in pesos]   # clamp sutil nos pesos das arestas

    nx.draw_networkx(
        G, pos, ax=ax,
        node_color=cores,
        node_size=tamanhos,
        edge_color='#4A5A6A',
        width=pesos,
        arrows=True,
        arrowsize=14,             # Reduzido de 18 para limpar visual de setas emboladas
        font_size=7.0,            # Ajuste fino na fonte
        font_color='white',
        font_weight='bold',
        connectionstyle='arc3,rad=0.12', # Curvatura levemente maior para evitar sobreposição de idas/voltas
    )

    ax.set_title(titulo, fontsize=13, fontweight='bold', pad=12, color='#1a1a2e')
    ax.axis('off')


def visualizar(G_normal, mules_n, cent_n, G_fraude, mules_f, cent_f):
    # ── Paleta e estilo ───────────────────────────────────────────────────────
    BG      = '#0d1117'   # fundo geral — quase preto
    PANEL   = '#161b22'   # fundo dos painéis
    TITULO  = '#e6edf3'
    SUBTTL  = '#8b949e'

    fig = plt.figure(figsize=(22, 10), facecolor=BG) # Aumentado levemente o tamanho da figura externa
    fig.suptitle(
        "NUBANK  .  ANTIFRAUD ENGINE  --  Detecção de Money Mule via Betweenness Centrality",
        fontsize=15, fontweight='bold', color=TITULO, y=0.97
    )

    gs = gridspec.GridSpec(1, 2, figure=fig, wspace=0.08,
                            left=0.03, right=0.97, top=0.88, bottom=0.12)

    # ── Painel esquerdo: fluxo normal ────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor(PANEL)
    desenhar_grafo(ax1, G_normal, mules_n, cent_n,
                   "Fluxo Normal -- Transacoes Legitimas", seed=7)

    ax1.text(0.5, -0.05, "Sem concentracao de caminhos . Nenhum alerta disparado",
             transform=ax1.transAxes, ha='center', fontsize=9,
             color=SUBTTL, style='italic')

    # ── Painel direito: fraude ───────────────────────────────────────────────
    ax2 = fig.add_subplot(gs[1])
    ax2.set_facecolor(PANEL)
    # Alterada a seed do layout de fraude para 15 (calcula um espalhamento mais limpo para essa estrutura)
    desenhar_grafo(ax2, G_fraude, mules_f, cent_f,
                   "Fraude Detectada -- Padrao Money Mule", seed=15)

    ax2.text(0.5, -0.05,
             f"Contas suspeitas: {', '.join(mules_f)}  |  R$ 125.000 em risco",
             transform=ax2.transAxes, ha='center', fontsize=9,
             color='#E57373', style='italic')

    # ── Legenda global ───────────────────────────────────────────────────────
    legenda = [
        mpatches.Patch(color='#1565C0', label='Conta normal'),
        mpatches.Patch(color='#FF8F00', label='Vítima (Pix forçado)'),
        mpatches.Patch(color='#E53935', label='Money Mule (alta centralidade)'),
        mpatches.Patch(color='#C62828', label='Hub de escalonamento'),
        mpatches.Patch(color='#6A1B9A', label='Destino final suspeito'),
    ]
    fig.legend(
        handles=legenda,
        loc='lower center',
        ncol=5,
        fontsize=9,
        frameon=True,
        framealpha=0.15,
        facecolor=PANEL,
        edgecolor='#30363d',
        labelcolor=TITULO,
        bbox_to_anchor=(0.5, 0.02),
    )

    # Linha divisória entre painéis
    fig.add_artist(plt.Line2D([0.5, 0.5], [0.10, 0.92],
                               color='#30363d', lw=1.2,
                               transform=fig.transFigure))

    # Salvando localmente
    plt.savefig('rede_antifraude_nubank.png',
                dpi=160, bbox_inches='tight', facecolor=BG)
    print("  Salvo com sucesso localmente: rede_antifraude_nubank.png")