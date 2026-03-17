import streamlit as st
import pandas as pd

# =========================
# Configuração da página
# =========================
st.set_page_config(
    page_title="Calculadora de Apostas Elegíveis",
    layout="wide"
)

# =========================
# Jogos elegíveis
# =========================
JOGOS_ELEGIVEIS = [
    "Fortune Tiger", "Fortune Ox", "Fortune Mouse", "Fortune Rabbit",
    "Tigre Sortudo", "Tigre Sortudo 1000", "Macaco Sortudo",
    "Ratinho Sortudo", "Touro Sortudo", "Cachorro Sortudo",
    "Wild Bounty Showdown", "Dragon Hatch", "Dragon Hatch 2",
    "Midas Fortune", "The Great Icescape", "Wild Bandito",
    "Lucky Neko", "Piggy Gold", "Dragon Tiger Luck", "Lucky Piggy",
    "Caishen Wins", "Bikini Paradise", "Double Fortune",
    "Ways Of The Qilin", "Ganesha Gold", "Ganesha Fortune",
    "Mahjong Ways", "Mahjong Ways 2", "Speed Winner",
    "Treasures Of Aztec", "Legend Of Perseus", "Shaolin Soccer",
    "Asgardian Rising", "Diner Delights", "Cash Mania",
    "Pinata Wins", "Wild Ape", "Futebol Fever", "Ultimate Striker",
    "Jungle Delight", "Zombie Outbreak", "Mafia Mayhem",
    "Yakuza Honor", "Mystic Potion", "Wings Of Iguazu",
    "Three Crazy Piggies", "Rio Fantasia", "Chocolate Deluxe",
    "Graffiti Rush", "Dreams Of Macau", "Sweet Bonanza",
    "Sweet Bonanza Xmas", "Gates of Olympus",
    "Gates of Olympus 1000", "Gates of Olympus Xmas 1000",
    "Big Bass Bonanza", "Big Bass Splash", "Big Bass Christmas Bash",
    "Fortune Dragon"
]

JOGOS_ELEGIVEIS_NORMALIZADOS = [j.lower().strip() for j in JOGOS_ELEGIVEIS]

# =========================
# Título
# =========================
st.markdown(
    "<h1 style='text-align:center;'>🎰 Calculadora de Apostas Elegíveis</h1>",
    unsafe_allow_html=True
)

# =========================
# Upload
# =========================
arquivo = st.file_uploader("📂 Envie o CSV", type=["csv"])

if arquivo:
    df = pd.read_csv(arquivo)

    # =========================
    # Validação
    # =========================
    colunas = {"Game Name", "Bet", "Creation Date", "Client"}
    if not colunas.issubset(df.columns):
        st.error("❌ CSV inválido")
        st.stop()

    # =========================
    # Tratamento
    # =========================
    df["Creation Date"] = pd.to_datetime(df["Creation Date"], dayfirst=True, errors="coerce")
    df["Bet"] = pd.to_numeric(df["Bet"], errors="coerce").fillna(0)
    df = df.dropna(subset=["Creation Date"])

    df["Game Name Normalizado"] = df["Game Name"].str.lower().str.strip()

    # =========================
    # Filtro
    # =========================
    st.subheader("⏰ Filtro")

    col1, col2 = st.columns(2)

    with col1:
        data_inicio = st.date_input("Data inicial")
        hora_inicio = st.time_input("Hora inicial")

    with col2:
        data_fim = st.date_input("Data final")
        hora_fim = st.time_input("Hora final")

    inicio = pd.to_datetime(f"{data_inicio} {hora_inicio}")
    fim = pd.to_datetime(f"{data_fim} {hora_fim}")

    df = df[(df["Creation Date"] >= inicio) & (df["Creation Date"] <= fim)]

    if df.empty:
        st.warning("⚠️ Nenhum dado encontrado.")
        st.stop()

    # =========================
    # Cliente
    # =========================
    clientes = df["Client"].unique()

    if len(clientes) == 1:
        st.markdown(f"### 👤 Cliente: **{clientes[0]}**")
    else:
        st.write(clientes)

    # =========================
    # Elegibilidade
    # =========================
    df["Elegivel"] = df["Game Name Normalizado"].isin(JOGOS_ELEGIVEIS_NORMALIZADOS)

    df_elegiveis = df[df["Elegivel"]]
    df_nao_elegiveis = df[~df["Elegivel"]]

    # =========================
    # Totais
    # =========================
    total_geral = df["Bet"].sum()
    total_elegiveis = df_elegiveis["Bet"].sum()
    total_nao_elegiveis = df_nao_elegiveis["Bet"].sum()

    percentual_elegivel = (total_elegiveis / total_geral * 100) if total_geral > 0 else 0

    # =========================
    # Função formatar
    # =========================
    def formatar_brl(valor):
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # =========================
    # Cards
    # =========================
    st.subheader("💵 Resumo")

    colA, colB, colC, colD = st.columns(4)

    def card(titulo, valor, cor):
        st.markdown(f"""
        <div style="padding:20px; border-radius:12px; background:{cor}; text-align:center;">
            <h4 style="color:white;">{titulo}</h4>
            <h2 style="color:white;">{formatar_brl(valor)}</h2>
        </div>
        """, unsafe_allow_html=True)

    with colA:
        card("Total Geral", total_geral, "#1565c0")

    with colB:
        card("Elegíveis", total_elegiveis, "#2e7d32")

    with colC:
        card("Não Elegíveis", total_nao_elegiveis, "#c62828")

    with colD:
        st.markdown(f"""
        <div style="padding:20px; border-radius:12px; background:#6a1b9a; text-align:center;">
            <h4 style="color:white;">% Elegível</h4>
            <h2 style="color:white;">{percentual_elegivel:.2f}%</h2>
        </div>
        """, unsafe_allow_html=True)

    # =========================
    # Tabela
    # =========================
    def gerar_tabela(df_base):
        tabela = (
            df_base
            .groupby("Game Name")
            .agg(
                Quantidade_Rodadas=("Bet", "count"),
                Total_Apostado=("Bet", "sum"),
                Primeira_Aposta=("Creation Date", "min"),
                Ultima_Aposta=("Creation Date", "max")
            )
            .reset_index()
            .sort_values(by="Total_Apostado", ascending=False)
        )

        tabela["Primeira_Aposta"] = tabela["Primeira_Aposta"].dt.strftime("%d/%m/%Y %H:%M")
        tabela["Ultima_Aposta"] = tabela["Ultima_Aposta"].dt.strftime("%d/%m/%Y %H:%M")

        tabela["Resumo"] = tabela.apply(
            lambda row: f"{formatar_brl(row['Total_Apostado'])} ({row['Quantidade_Rodadas']} rodadas)",
            axis=1
        )

        return tabela[["Game Name", "Resumo", "Primeira_Aposta", "Ultima_Aposta"]]

    # =========================
    # Exibição
    # =========================
    st.subheader("🟢 Jogos Elegíveis")
    st.dataframe(gerar_tabela(df_elegiveis), use_container_width=True)

    st.subheader("🔴 Jogos Não Elegíveis")
    st.dataframe(gerar_tabela(df_nao_elegiveis), use_container_width=True)

    # =========================
    # RELATÓRIO FINAL
    # =========================
    st.subheader("📋 Relatório Final")

    valor_necessario = st.number_input(
        "💰 Valor necessário para cumprir missão",
        min_value=0.0,
        step=10.0
    )

    if valor_necessario > 0:

        cliente_nome = clientes[0] if len(clientes) == 1 else "Jogador"

        jogos_lista = (
            df_elegiveis
            .groupby("Game Name")["Bet"]
            .sum()
            .sort_values(ascending=False)
        )

        if jogos_lista.empty:
    jogos_texto = "Nenhum jogo elegível apostado"
else:
    jogos_texto = "\n".join(
        [f"{jogo}: {formatar_brl(valor)}" for jogo, valor in jogos_lista.items()]
    )

        faltante = max(0, valor_necessario - total_elegiveis)

        if total_elegiveis >= valor_necessario:
            mensagem = f"""Jogador {cliente_nome} apostou o valor necessário para cumprir missão

Jogos apostados e valor:
{jogos_texto}
"""
        else:
            mensagem = f"""Jogador {cliente_nome} não apostou valor necessário para cumprir missão

Faltante: {formatar_brl(faltante)}

Jogos apostados e valor:
{jogos_texto}
"""

        st.text_area("📄 Mensagem pronta", mensagem, height=300)
