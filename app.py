import streamlit as st
import pandas as pd

# =========================
# Configuração
# =========================
st.set_page_config(page_title="Calculadora de Apostas", layout="wide")

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
# Funções auxiliares
# =========================
def formatar_brl(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# =========================
# Título
# =========================
st.title("🎰 Calculadora de Apostas Elegíveis")

# =========================
# Upload
# =========================
arquivo = st.file_uploader("📂 Envie o CSV", type=["csv"])

if arquivo:
    df = pd.read_csv(arquivo)

    # Validação
    if not {"Game Name", "Bet", "Creation Date", "Client"}.issubset(df.columns):
        st.error("CSV inválido")
        st.stop()

    # Tratamento
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
        st.warning("Nenhum dado encontrado")
        st.stop()

    # =========================
    # Cliente
    # =========================
    clientes = df["Client"].unique()
    cliente_nome = clientes[0] if len(clientes) == 1 else "Jogador"
    st.markdown(f"### 👤 Cliente: **{cliente_nome}**")

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

    # =========================
    # Cards
    # =========================
    st.subheader("💵 Resumo")

    colA, colB, colC = st.columns(3)

    with colA:
        st.metric("Total Geral", formatar_brl(total_geral))

    with colB:
        st.metric("Elegíveis", formatar_brl(total_elegiveis))

    with colC:
        st.metric("Não Elegíveis", formatar_brl(total_nao_elegiveis))

    # =========================
    # Tabela com datas corrigida
    # =========================
    def gerar_tabela(df_base):
        tabela = (
            df_base
            .groupby("Game Name")
            .agg(
                Rodadas=("Bet", "count"),
                Total=("Bet", "sum"),
                Primeira_Aposta=("Creation Date", "min"),
                Ultima_Aposta=("Creation Date", "max")
            )
            .reset_index()
            .sort_values(by="Total", ascending=False)
        )

        tabela["Primeira_Aposta"] = tabela["Primeira_Aposta"].dt.strftime("%d/%m/%Y %H:%M")
        tabela["Ultima_Aposta"] = tabela["Ultima_Aposta"].dt.strftime("%d/%m/%Y %H:%M")

        tabela["Resumo"] = tabela.apply(
            lambda row: f"{formatar_brl(row['Total'])} ({row['Rodadas']} rodadas)",
            axis=1
        )

        return tabela[[
            "Game Name",
            "Resumo",
            "Primeira_Aposta",
            "Ultima_Aposta"
        ]]

    # =========================
    # Exibição tabelas
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

        faltante = max(0, valor_necessario - total_elegiveis)

        jogos_lista = (
            df
            .groupby(["Game Name", "Elegivel"])["Bet"]
            .sum()
            .reset_index()
            .sort_values(by="Bet", ascending=False)
        )

        if jogos_lista.empty:
            jogos_texto = "Nenhum jogo apostado"
        else:
            jogos_texto = "\n".join(
                [
                    f"{row['Game Name']} ({'🟢 Elegível' if row['Elegivel'] else '🔴 Não elegível'}): {formatar_brl(row['Bet'])}"
                    for _, row in jogos_lista.iterrows()
                ]
            )

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
