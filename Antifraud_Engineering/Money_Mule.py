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

