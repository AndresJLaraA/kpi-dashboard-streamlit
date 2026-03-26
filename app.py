import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from io import BytesIO
from datetime import datetime

# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────

SHAREPOINT_URL = (
    "https://fonturcolombia-my.sharepoint.com/:x:/g/personal/"
    "alara_fontur_com_co/IQAHr1G56IHiQ7ulXGBvBNP8AVhnUF5G9p_Mh0EO_oSuN50"
    "?e=6Mftls&download=1"
)

HOJA = "Datos"

CURVA_START = 120
CURVA_END = 131

IG_START = 4
IG_END = 114
IG_STEP = 11

IR_START = 135
IR_END = 179
IR_STEP = 11

PERIODOS = [
    "Oct-25","Nov-25","Dic-25","Ene-26","Feb-26",
    "Mar-26","Abr-26","May-26","Jun-26","Jul-26","Ago-26"
]

# ─────────────────────────────────────────────
# CARGA DE DATOS
# ─────────────────────────────────────────────

@st.cache_data(ttl=300)
def cargar_excel() -> pd.DataFrame:

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/octet-stream",
    }

    resp = requests.get(
        SHAREPOINT_URL,
        headers=headers,
        timeout=30,
        allow_redirects=True
    )

    resp.raise_for_status()

    content_type = resp.headers.get("Content-Type", "")

    if "html" in content_type:
        raise ValueError(
            "SharePoint devolvió HTML en vez del archivo. "
            "Verifica que el enlace esté compartido como público."
        )

    return pd.read_excel(
        BytesIO(resp.content),
        sheet_name=HOJA,
        header=None
    )


# ─────────────────────────────────────────────
# PARSEO DEL EXCEL
# ─────────────────────────────────────────────

def extraer_datos(df: pd.DataFrame) -> dict:

    # ── CURVA S ─────────────────────────────

    prog, real_s, desv, estados, montos = [], [], [], [], []

    for i in range(CURVA_START, CURVA_END):

        row = df.iloc[i]

        prog.append(float(row[2]) * 100 if pd.notna(row[2]) else None)
        real_s.append(float(row[3]) * 100 if pd.notna(row[3]) else None)
        desv.append(float(row[4]) if pd.notna(row[4]) else None)
        montos.append(float(row[5]) if pd.notna(row[5]) else None)

        estados.append(
            str(row[6]).strip() if pd.notna(row[6]) else "—"
        )

    presupuesto = (
        float(df.iloc[118][2])
        if pd.notna(df.iloc[118][2])
        else 0
    )

    curva = pd.DataFrame({
        "Período": PERIODOS,
        "Programado": prog,
        "Real": real_s,
        "Desviación (pp)": desv,
        "Estado": estados,
        "Monto Ejec. COP": montos
    })

    # ── IGs ─────────────────────────────

    ig_rows = []

    for i in range(IG_START, IG_END, IG_STEP):

        row = df.iloc[i]

        ig_rows.append({
            "Cód.": str(row[0]).strip(),
            "Indicador": str(row[1]).strip(),
            "Unidad": str(row[3]).strip(),
            "Meta Total": float(row[4]) if pd.notna(row[4]) else 1,
            "Meta Acum.": float(row[5]) if pd.notna(row[5]) else 0,
            "Período": str(row[6]).strip() if pd.notna(row[6]) else "—",
            "Valor Real": float(row[8]) if pd.notna(row[8]) else 0,
            "Últ. Acum.": float(row[9]) if pd.notna(row[9]) else 0,
            "% Desempeño": float(row[10]) if pd.notna(row[10]) else 0,
            "Semáforo": int(row[11]) if pd.notna(row[11]) else 1
        })

    igs = pd.DataFrame(ig_rows)

    # ── IRs ─────────────────────────────

    ir_rows = []

    for i in range(IR_START, IR_END, IR_STEP):

        row = df.iloc[i]

        ir_rows.append({
            "Cód.": str(row[1]).strip(),
            "Indicador": str(row[2]).strip(),
            "Unidad": str(row[4]).strip(),
            "Meta": row[5] if pd.notna(row[5]) else "—",
            "Valor": float(row[8]) if pd.notna(row[8]) else 0,
            "Últ. Acum.": float(row[9]) if pd.notna(row[9]) else 0,
            "Fuente": str(row[11]).strip() if pd.notna(row[11]) else "—"
        })

    irs = pd.DataFrame(ir_rows)

    return {
        "curva": curva,
        "igs": igs,
        "irs": irs,
        "presupuesto": presupuesto
    }


# ─────────────────────────────────────────────
# UTILIDADES
# ─────────────────────────────────────────────

def semaforo_color(val: int) -> str:
    return {3: "🟢", 2: "🟡", 1: "🔴"}.get(val, "⚪")


def estado_color(estado: str) -> str:

    if "Rezagado" in estado:
        return "🔴"

    if "Adelantado" in estado:
        return "🟢"

    if "En rango" in estado:
        return "🟡"

    return "⚪"


# ─────────────────────────────────────────────
# LAYOUT
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="Dashboard FONTUR · FNTP-2025-264",
    layout="wide",
    page_icon="📊"
)

st.title("📊 Seguimiento Proyecto FNTP-2025-264")
st.caption("Campaña Colombia el País de la Belleza · FONTUR")

# ─────────────────────────────────────────────
# CARGA
# ─────────────────────────────────────────────

with st.spinner("Cargando datos desde SharePoint..."):

    try:

        df_raw = cargar_excel()

        datos = extraer_datos(df_raw)

        curva = datos["curva"]
        igs = datos["igs"]
        irs = datos["irs"]
        presupuesto = datos["presupuesto"]

        st.success(
            f"Datos actualizados · {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        )

    except Exception as e:

        st.error(f"Error al cargar el archivo: {e}")
        st.stop()

# ─────────────────────────────────────────────
# CORTE AUTOMÁTICO
# ─────────────────────────────────────────────

curva_real = curva.dropna(subset=["Real"])

if curva_real.empty:

    st.warning("No hay datos de ejecución aún")
    st.stop()

corte = curva_real.iloc[-1]

periodo_corte = corte["Período"]
mes_corte = curva_real.index[-1] + 1

# ─────────────────────────────────────────────
# KPIs
# ─────────────────────────────────────────────

ejecucion_real = corte["Real"]
meta_mes = corte["Programado"]
desviacion = ejecucion_real - meta_mes
monto_ejec = corte["Monto Ejec. COP"] or 0
igs_con_avance = int((igs["Valor Real"] > 0).sum())

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Ejecución real acum.",
    f"{ejecucion_real:.1f}%",
    f"{desviacion:+.1f} pp vs programado"
)

col2.metric(
    "Presupuesto total",
    f"${presupuesto/1e9:.1f}MM COP",
    f"Ejecutado: ${monto_ejec/1e9:.1f}MM"
)

col3.metric(
    "IGs con avance",
    f"{igs_con_avance} / {len(igs)}"
)

col4.metric(
    "Estado general",
    corte["Estado"],
    f"Corte: {periodo_corte}"
)

st.divider()

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────

tab1, tab2, tab3 = st.tabs(
    [
        "📈 Curva-S",
        "📋 Indicadores de Gestión",
        "🎯 Indicadores de Resultado"
    ]
)

# ─────────────────────────────────────────────
# TAB CURVA S
# ─────────────────────────────────────────────

with tab1:

    curva_real = curva.dropna(subset=["Real"])

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=curva["Período"],
        y=curva["Programado"],
        name="Programado",
        mode="lines+markers",
        line=dict(color="#185FA5", dash="dot")
    ))

    fig.add_trace(go.Scatter(
        x=curva_real["Período"],
        y=curva_real["Real"],
        name="Real ejecutado",
        mode="lines+markers",
        line=dict(color="#A32D2D")
    ))

    fig.update_layout(
        yaxis_title="% acumulado",
        yaxis=dict(ticksuffix="%"),
        height=380
    )

    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# TAB IG
# ─────────────────────────────────────────────

with tab2:

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=igs["Cód."],
        x=igs["Meta Acum."] * 100,
        orientation="h",
        name="Meta"
    ))

    fig.add_trace(go.Bar(
        y=igs["Cód."],
        x=igs["Valor Real"] * 100,
        orientation="h",
        name="Real"
    ))

    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# TAB IR
# ─────────────────────────────────────────────

with tab3:

    st.dataframe(irs, use_container_width=True)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:

    st.header("⚙️ Configuración")

    st.markdown(f"""
    **Proyecto:** FNTP-2025-264  
    **Contrato:** FNTC-161-2026  
    **Horizonte:** Oct-25 – Ago-26  

    **Corte actual:** {periodo_corte} (Mes {mes_corte})  

    **Presupuesto:** ${presupuesto/1e9:.2f}MM COP
    """)

    st.divider()

    if st.button("🔄 Forzar actualización"):

        st.cache_data.clear()
        st.rerun()

    st.caption("Datos refrescados cada 5 minutos.")