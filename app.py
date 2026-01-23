import streamlit as st
import pandas as pd

st.set_page_config(page_title="Calculadora de Apostas Elegíveis", layout="wide")

st.title("🎰 Calculadora de Valor Apostado - Jogos Elegíveis")

# ---------------------------
# Lista de jogos elegíveis
# ---------------------------
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

# ---------------------------
# Upload do CSV
# ---------------------------
uploaded_file = st.file_uploader("📤 Faça upload do CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Padronização
    df["Creation Date"] = pd.to_datetime(df["Creation Date"], errors="coerce")
    df["Bet"] = pd.to_numeric(df["Bet"], errors="coerce").fillna(0)

    # ---------------------------
    # Filtro de Data e Hora
    # ---------------------------
    st.subheader("⏰ Filtro de Data e Hora")

    col1, col2 = st.columns(2)

    with col1:
        start_datetime = st.date_input("Data inicial")
        start_time = st.time_input("Hora inicial")

    with col2:
        end_datetime = st.date_input("Data final")
        end_time = st.time_input("Hora final")

    start_dt = pd.to_datetime(f"{start_datetime} {start_time}")
    end_dt = pd.to_datetime(f"{end_datetime} {end_time}")

    df_filtered = df[
        (df["Creation Date"] >= start_dt) &
        (df["Creation Date"] <= end_dt)
    ]

    # ---------------------------
    # Separação elegíveis / não elegíveis
    # ---------------------------
    df_elegiveis = df_filtered[df_filtered["Game Name"].isin(JOGOS_ELEGIVEIS)]
    df_nao_elegiveis = df_filtered[~df_filtered["Game Name"].isin(JOGOS_ELEGIVEIS)]

    # ---------------------------
    # Exibição do Cliente
    # ---------------------------
    st.subheader("👤 Cliente(s)")
    st.write(df_filtered["Client"].unique())

    # ---------------------------
    # Total Apostado (Elegíveis)
    # ---------------------------
    total_apostado = df_elegiveis["Bet"].sum()
    st.metric("💰 Total Apostado em Jogos Elegíveis", f"R$ {total_apostado:,.2f}")

    # ---------------------------
    # Valor por jogo elegível
    # ---------------------------
    st.subheader("🎮 Valor Apostado por Jogo Elegível")
    jogos_grouped = (
        df_elegiveis
        .groupby("Game Name")["Bet"]
        .sum()
        .reset_index()
        .sort_values(by="Bet", ascending=False)
    )
    st.dataframe(jogos_grouped, use_container_width=True)

    # ---------------------------
    # Jogos não elegíveis
    # ---------------------------
    st.subheader("🚫 Jogos NÃO Elegíveis")

    nao_elegiveis_grouped = (
        df_nao_elegiveis
        .groupby("Game Name")["Bet"]
        .sum()
        .reset_index()
        .sort_values(by="Bet", ascending=False)
    )

    total_nao_elegiveis = df_nao_elegiveis["Bet"].sum()

    st.write(f"**Total apostado em jogos não elegíveis:** R$ {total_nao_elegiveis:,.2f}")
    st.dataframe(nao_elegiveis_grouped, use_container_width=True)

    # ---------------------------
    # Exportar CSV
    # ---------------------------
    st.subheader("📥 Exportar CSV")

    csv_export = df_filtered.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Baixar CSV Filtrado",
        data=csv_export,
        file_name="apostas_filtradas.csv",
        mime="text/csv"
    )
