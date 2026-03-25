import streamlit as st
from pdf2image import convert_from_bytes
from PIL import Image
import io
import os

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PDF Compressor",
    page_icon="🗜️",
    layout="centered"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background-color: #0f0f0f;
    color: #f0f0f0;
}

h1, h2, h3 {
    font-family: 'DM Mono', monospace !important;
    letter-spacing: -0.02em;
}

.hero {
    text-align: center;
    padding: 3rem 0 2rem 0;
}

.hero h1 {
    font-size: 2.8rem;
    font-weight: 500;
    color: #f0f0f0;
    margin-bottom: 0.5rem;
}

.hero p {
    color: #888;
    font-size: 1.05rem;
    font-weight: 300;
}

.accent { color: #a8ff78; }

.card {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
}

.result-card {
    background: #0d1f0d;
    border: 1px solid #2a4a2a;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
    text-align: center;
}

.size-display {
    font-family: 'DM Mono', monospace;
    font-size: 2rem;
    color: #a8ff78;
    font-weight: 500;
}

.size-label {
    color: #666;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.3rem;
}

.arrow {
    color: #444;
    font-size: 1.5rem;
    margin: 0 1rem;
}

.sizes-row {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    flex-wrap: wrap;
}

.size-block { text-align: center; }

.reduction-badge {
    display: inline-block;
    background: #a8ff7820;
    border: 1px solid #a8ff7840;
    color: #a8ff78;
    font-family: 'DM Mono', monospace;
    font-size: 0.9rem;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    margin-top: 1rem;
}

div[data-testid="stFileUploader"] {
    background: #1a1a1a;
    border: 1px dashed #333;
    border-radius: 12px;
    padding: 0.5rem;
}

div[data-testid="stFileUploader"]:hover {
    border-color: #a8ff78;
}

div[data-testid="stSelectbox"] label,
div[data-testid="stSlider"] label {
    color: #aaa !important;
    font-size: 0.9rem !important;
}

.stButton > button {
    background: #a8ff78;
    color: #0f0f0f;
    font-family: 'DM Mono', monospace;
    font-weight: 500;
    font-size: 1rem;
    border: none;
    border-radius: 8px;
    padding: 0.75rem 2rem;
    width: 100%;
    cursor: pointer;
    transition: all 0.2s;
}

.stButton > button:hover {
    background: #c8ff98;
    transform: translateY(-1px);
}

.stDownloadButton > button {
    background: transparent;
    color: #a8ff78;
    font-family: 'DM Mono', monospace;
    border: 1px solid #a8ff78;
    border-radius: 8px;
    padding: 0.75rem 2rem;
    width: 100%;
}

.stDownloadButton > button:hover {
    background: #a8ff7815;
}

.tip {
    color: #666;
    font-size: 0.82rem;
    font-family: 'DM Mono', monospace;
    padding: 0.8rem;
    background: #151515;
    border-left: 2px solid #333;
    border-radius: 0 6px 6px 0;
    margin-top: 0.5rem;
}

footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def compress_pdf(file_bytes: bytes, dpi: int, quality: int, color: bool) -> bytes:
    pages = convert_from_bytes(file_bytes, dpi=dpi)
    mode = 'RGB' if color else 'L'
    output_pages = [p.convert(mode) for p in pages]

    buf = io.BytesIO()
    output_pages[0].save(
        buf,
        save_all=True,
        append_images=output_pages[1:],
        format='PDF',
        quality=quality
    )
    return buf.getvalue()


def fmt_size(size_bytes: int) -> str:
    mb = size_bytes / 1024 / 1024
    if mb >= 1:
        return f"{mb:.2f} MB"
    return f"{size_bytes / 1024:.0f} KB"


# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🗜️ PDF <span class="accent">Compressor</span></h1>
    <p>Comprime tus PDFs escaneados sin complicaciones</p>
</div>
""", unsafe_allow_html=True)

# Upload
uploaded_file = st.file_uploader(
    "Arrastra tu PDF aquí",
    type=["pdf"],
    label_visibility="collapsed"
)

if uploaded_file:
    original_bytes = uploaded_file.read()
    original_size = len(original_bytes)

    st.markdown(f"""
    <div class="card">
        <div class="size-label">Archivo cargado</div>
        <b>{uploaded_file.name}</b>
        <span style="color:#666; margin-left:1rem; font-family:'DM Mono',monospace; font-size:0.9rem;">{fmt_size(original_size)}</span>
    </div>
    """, unsafe_allow_html=True)

    # Settings
    st.markdown("#### Ajustes")

    preset = st.selectbox(
        "Nivel de compresión",
        options=["Balanceado (recomendado)", "Agresivo", "Personalizado"],
    )

    if preset == "Balanceado (recomendado)":
        dpi, quality = 96, 30
    elif preset == "Agresivo":
        dpi, quality = 72, 20
    else:
        col1, col2 = st.columns(2)
        with col1:
            dpi = st.slider("DPI", min_value=30, max_value=150, value=72, step=10)
        with col2:
            quality = st.slider("Calidad JPEG", min_value=5, max_value=80, value=20, step=5)

    color = st.toggle("Mantener color", value=True)

    st.markdown(f"""
    <div class="tip">
        DPI: {dpi} · Calidad: {quality} · {'Color' if color else 'Escala de grises'}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Compress button
    if st.button("Comprimir PDF"):
        with st.spinner("Comprimiendo..."):
            compressed = compress_pdf(original_bytes, dpi, quality, color)
            compressed_size = len(compressed)
            reduction = (1 - compressed_size / original_size) * 100

        # Result
        st.markdown(f"""
        <div class="result-card">
            <div class="sizes-row">
                <div class="size-block">
                    <div class="size-label">Original</div>
                    <div class="size-display" style="color:#888">{fmt_size(original_size)}</div>
                </div>
                <div class="arrow">→</div>
                <div class="size-block">
                    <div class="size-label">Comprimido</div>
                    <div class="size-display">{fmt_size(compressed_size)}</div>
                </div>
            </div>
            <div class="reduction-badge">↓ {reduction:.1f}% reducción</div>
        </div>
        """, unsafe_allow_html=True)

        output_name = uploaded_file.name.replace(".pdf", "_comprimido.pdf")
        st.download_button(
            label="⬇ Descargar PDF comprimido",
            data=compressed,
            file_name=output_name,
            mime="application/pdf"
        )

else:
    st.markdown("""
    <div class="tip" style="text-align:center; border-left:none; border: 1px solid #222; border-radius:8px;">
        Sube un PDF escaneado desde tu iPhone o cualquier escáner
    </div>
    """, unsafe_allow_html=True)
