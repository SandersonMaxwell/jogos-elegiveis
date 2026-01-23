import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Calculadora de Apostas Elegíveis",
    layout="wide"
)

# =========================
# Título
# =========================
st.markdown(
    """
    <h1 style='text-align:center;'>🎰 Calculadora de Apostas Elegíveis</h1>
    <p style='text-align:center;color:gray;'>
    Visualização clara de valores apostados por período
    </p>
    """,
    unsafe_allow_html=True
)

st.divider()

# =========================
# Jogos elegíveis
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
uploaded_file = st.file_uploader(
    "📤 Faça upload do arquivo CSV",
    type=["csv"]
)

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    df["Creation Date"] = pd.to_datetime(df["Creation Date"], errors="coerce")
    df["Bet"] = pd.to_numeric(df["Bet"], errors="coerce").fillna(0)

    st.divider()

    # =========================
    # Filtro de Data e Hora
    # =========================
    st.subheader("⏰ Filtro de Data e Hora")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        start_date = st.date_input("📅 Data inicial")

    with col2:
        start_time = st.text_input("⌨️ Hora inicial (HH:MM)", value="00:00")

    with col3:
        end_date = st.date_input("📅 Data final")

    with col4:
        end_time = st.text_input("⌨️ Hora final (HH:MM)", value="23:59")

    try:
        start_dt = datetime.strptime(
            f"{start_date} {start_time}", "%Y-%m-%d %H:%M"
        )
        end_dt = datetime.strptime(
            f"{end_date} {end_time}", "%Y-%m-%d %H:%M"
        )

        df_filtered = df[
            (df["Creation Date"] >= start_dt) &
            (df["Creation Date"] <= end_dt)
        ]

    except ValueError:
        st.error("⚠️ Horário inválido. Use HH:MM (ex: 09:30)")
        st.stop()

    st.divider()

    # =========================
    # Cliente
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
    # Cards de valores
    # =========================
    st.subheader("💵 Resumo Financeiro")

    colA, colB, colC = st.columns(3)

    with colA:
        st.metric(
            "🟢 Total Geral Apostado",
            f"R$ {total_geral:,.2f}"
        )

    with colB:
        st.metric(
            "🔵 Total Jogos Elegíveis",
            f"R$ {total_elegiveis:,.2f}"
        )

    with colC:
        st.metric(
            "🔴 Total Jogos Não Elegíveis",
            f"R$ {total_nao_elegiveis:,.2f}"
        )

    st.divider()

    # =========================
    # Jogos Elegíveis
    # =========================
    st.subheader("🎮 Valor Apostado por Jogo Elegível")

    tabela_elegiveis = (
        df_elegiveis
        .groupby("Game Name")["Bet"]
        .sum()
        .reset_index()
        .sort_values(by="Bet", ascending=False)
    )

    st.dataframe(tabela_elegiveis, use_container_width=True)

    st.divider()

    # =========================
    # Jogos Não Elegíveis
    # =========================
    st.subheader("🚫 Jogos Não Elegíveis")

    tabela_nao_elegiveis = (
        df_nao_elegiveis
        .groupby("Game Name")["Bet"]
        .sum()
        .reset_index()
        .sort_values(by="Bet", ascending=False)
    )

    st.dataframe(tabela_nao_elegiveis, use_container_width=True)
