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
    "Tigre Sortudo", "Tigrinho Sortudo 1000", "Macaco Sortudo",
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
    "Sweet Bonanza Xmas", "Gates Of Olympus",
    "Gates Of Olympus 1000", "Gates Of Olympus Xmas 1000",
    "Big Bass Bonanza", "Big Bass Splash", "Big Bass Christmas Bash"
]

# =========================
# Título e descrição
# =========================
st.title("🎰 Calculadora de Valor Apostado - Jogos Elegíveis")

st.markdown(
    """
    **Importante:**  
    Para confirmar se um jogo está elegível e garantir que o código não foi alterado,
    consulte sempre a lista oficial no link abaixo:

    👉 https://start.bet.br/promotions/1976
    """
)

# =========================
# Upload do arquivo
# =========================
arquivo = st.file_uploader("📂 Envie o arquivo CSV", type=["csv"])

if arquivo:
    df = pd.read_csv(arquivo)

    # =========================
    # Tratamento dos dados
    # =========================
    df["Creation Date"] = pd.to_datetime(df["Creation Date"], errors="coerce")
    df["Bet"] = pd.to_numeric(df["Bet"], errors="coerce").fillna(0)

    # =========================
    # Filtro por data e hora
    # =========================
    st.subheader("⏰ Filtro de Data e Hora")

    col1, col2 = st.columns(2)

    with col1:
        data_inicio = st.date_input("Data inicial")
        hora_inicio = st.text_input("Hora inicial (HH:MM)", value="00:00")

    with col2:
        data_fim = st.date_input("Data final")
        hora_fim = st.text_input("Hora final (HH:MM)", value="23:59")

    try:
        inicio = pd.to_datetime(f"{data_inicio} {hora_inicio}")
        fim = pd.to_datetime(f"{data_fim} {hora_fim}")

        df = df[(df["Creation Date"] >= inicio) & (df["Creation Date"] <= fim)]
    except:
        st.error("❌ Formato de hora inválido. Use HH:MM")

    # =========================
    # Cliente
    # =========================
    cliente = df["Client"].iloc[0]
    st.markdown(f"### 👤 Cliente: **{cliente}**")

    # =========================
    # Separação elegíveis / não elegíveis
    # =========================
    df["Elegivel"] = df["Game Name"].isin(JOGOS_ELEGIVEIS)

    df_elegiveis = df[df["Elegivel"]]
    df_nao_elegiveis = df[~df["Elegivel"]]

    # =========================
    # Totais
    # =========================
    total_geral = df["Bet"].sum()
    total_elegiveis = df_elegiveis["Bet"].sum()
    total_nao_elegiveis = df_nao_elegiveis["Bet"].sum()

    # =========================
    # Cards (dark/light safe)
    # =========================
    st.subheader("💵 Resumo Financeiro")

    colA, colB, colC = st.columns(3)

    with colA:
        st.markdown(
            f"""
            <div style="padding:20px; border-radius:12px; background:#1565c0; text-align:center;">
                <h4 style="color:white;">Total Geral Apostado</h4>
                <h2 style="color:white;">R$ {total_geral:,.2f}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    with colB:
        st.markdown(
            f"""
            <div style="padding:20px; border-radius:12px; background:#2e7d32; text-align:center;">
                <h4 style="color:white;">Jogos Elegíveis</h4>
                <h2 style="color:white;">R$ {total_elegiveis:,.2f}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    with colC:
        st.markdown(
            f"""
            <div style="padding:20px; border-radius:12px; background:#c62828; text-align:center;">
                <h4 style="color:white;">Jogos Não Elegíveis</h4>
                <h2 style="color:white;">R$ {total_nao_elegiveis:,.2f}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    # =========================
    # Função de tabela
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
    # Tabelas
    # =========================
    st.subheader("🟢 Jogos Elegíveis")
    st.dataframe(gerar_tabela(df_elegiveis), use_container_width=True)

    st.subheader("🔴 Jogos Não Elegíveis")
    st.dataframe(gerar_tabela(df_nao_elegiveis), use_container_width=True)
