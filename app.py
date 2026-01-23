import streamlit as st
import pandas as pd
from datetime import datetime, time

# =========================
# Configuração da página
# =========================
st.set_page_config(
    page_title="Calculadora de Apostas Elegíveis",
    layout="wide"
)

# =========================
# Título + Descrição
# =========================
st.markdown(
    """
    <h1 style="text-align:center;">🎰 Calculadora de Apostas Elegíveis</h1>

    <p style="text-align:center; font-size:16px; color:#b0b0b0;">
    Para garantir que o jogo está elegível e que o código não foi alterado ou quebrado,
    valide sempre na aba oficial de promoções:
    <br><br>
    <a href="https://start.bet.br/promotions/1976" target="_blank"
       style="color:#4da3ff; font-weight:bold;">
       👉 Promoções – Jogos Elegíveis (StartBet)
    </a>
    </p>
    """,
    unsafe_allow_html=True
)

st.divider()

# =========================
# Lista de jogos elegíveis
# =========================
JOGOS_ELEGIVEIS = [
    "Fortune Tiger","Fortune Ox","Fortune Mouse","Fortune Rabbit","Tigre Sortudo",
    "Tigrinho Sortudo 1000","Macaco Sortudo","Ratinho Sortudo","Touro Sortudo",
    "Cachorro Sortudo","Wild Bounty Showdown","Dragon Hatch","Dragon Hatch 2",
    "Midas Fortune","The Great Icescape","Wild Bandito","Lucky Neko","Piggy Gold",
    "Dragon Tiger Luck","Lucky Piggy","Caishen Wins","Bikini Paradise",
    "Double Fortune","Ways Of The Qilin","Ganesha Gold","Ganesha Fortune",
    "Mahjong Ways","Mahjong Ways 2","Speed Winner","Treasures Of Aztec",
    "Legend Of Perseus","Shaolin Soccer","Asgardian Rising","Diner Delights",
    "Cash Mania","Pinata Wins","Wild Ape","Futebol Fever","Ultimate Striker",
    "Jungle Delight","Zombie Outbreak","Mafia Mayhem","Yakuza Honor",
    "Mystic Potion","Wings Of Iguazu","Three Crazy Piggies","Rio Fantasia",
    "Chocolate Deluxe","Graffiti Rush","Dreams Of Macau","Sweet Bonanza",
    "Sweet Bonanza Xmas","Gates Of Olympus","Gates Of Olympus 1000",
    "Gates Of Olympus Xmas 1000","Big Bass Bonanza","Big Bass Splash",
    "Big Bass Christmas Bash"
]

# =========================
# Upload CSV
# =========================
uploaded_file = st.file_uploader("📤 Faça upload do arquivo CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    df["Creation Date"] = pd.to_datetime(df["Creation Date"], errors="coerce")
    df["Bet"] = pd.to_numeric(df["Bet"], errors="coerce").fillna(0)

    st.divider()

    # =========================
    # Filtro de Data e Hora (FIXO)
    # =========================
    st.subheader("⏰ Filtro de Data e Hora")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        start_date = st.date_input("📅 Data inicial")

    with col2:
        start_time = st.time_input("⏱️ Hora inicial", value=time(0, 0))

    with col3:
        end_date = st.date_input("📅 Data final")

    with col4:
        end_time = st.time_input("⏱️ Hora final", value=time(23, 59))

    start_dt = datetime.combine(start_date, start_time)
    end_dt = datetime.combine(end_date, end_time)

    df_filtered = df[
        (df["Creation Date"] >= start_dt) &
        (df["Creation Date"] <= end_dt)
    ]

    st.divider()

    # =========================
    # Cliente(s)
    # =========================
    st.subheader("👤 Cliente(s)")
    st.info(", ".join(df_filtered["Client"].astype(str).unique()))

    # =========================
    # Separação
    # =========================
    df_elegiveis = df_filtered[df_filtered["Game Name"].isin(JOGOS_ELEGIVEIS)]
    df_nao_elegiveis = df_filtered[~df_filtered["Game Name"].isin(JOGOS_ELEGIVEIS)]

    total_elegiveis = df_elegiveis["Bet"].sum()
    total_nao_elegiveis = df_nao_elegiveis["Bet"].sum()
    total_geral = total_elegiveis + total_nao_elegiveis

    # =========================
    # Cards resumo
    # =========================
    st.subheader("💵 Resumo Financeiro")

    colA, colB, colC = st.columns(3)

    with colA:
        st.markdown(
            f"""
            <div style="padding:22px; border-radius:14px; background:#1565c0; text-align:center;">
                <h4 style="color:white;">Total Geral Apostado</h4>
                <h2 style="color:white;">R$ {total_geral:,.2f}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    with colB:
        st.markdown(
            f"""
            <div style="padding:22px; border-radius:14px; background:#2e7d32; text-align:center;">
                <h4 style="color:white;">Jogos Elegíveis</h4>
                <h2 style="color:white;">R$ {total_elegiveis:,.2f}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    with colC:
        st.markdown(
            f"""
            <div style="padding:22px; border-radius:14px; background:#c62828; text-align:center;">
                <h4 style="color:white;">Jogos Não Elegíveis</h4>
                <h2 style="color:white;">R$ {total_nao_elegiveis:,.2f}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    # =========================
    # Função tabela com horários
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

    return tabela


    # =========================
    # Jogos Elegíveis
    # =========================
    st.subheader("🎮 Jogos Elegíveis")
    st.dataframe(gerar_tabela(df_elegiveis), use_container_width=True)

    st.divider()

    # =========================
    # Jogos Não Elegíveis
    # =========================
    st.subheader("🚫 Jogos Não Elegíveis")
    st.dataframe(gerar_tabela(df_nao_elegiveis), use_container_width=True)
