import os
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from motor_transcricao import arquivo_final, MotorTranscricao
from analise_dossie import gerar_dossie

st.set_page_config(page_title="Wil É Foda - Transcritor", page_icon="🎙️", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@400;600&display=swap');

* { font-family: 'Inter', sans-serif; }
.stApp {
    background: #020510;
    background-image:
        radial-gradient(ellipse at 20% 20%, rgba(0,196,204,0.08) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 80%, rgba(108,92,231,0.08) 0%, transparent 50%);
}
h1, h2, h3, p, label, .stMarkdown, .stCaption { color: #e8edf2 !important; }
#particles-canvas { position: fixed; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:0; }
.header-3d { text-align:center; padding:2rem 0 1rem; }
.header-3d h1 {
    font-family:'Orbitron',monospace !important;
    font-size:2.4rem !important; font-weight:900 !important;
    background:linear-gradient(135deg,#00c4cc 0%,#ffffff 40%,#a29bfe 70%,#00c4cc 100%);
    -webkit-background-clip:text !important; -webkit-text-fill-color:transparent !important;
    background-clip:text !important;
    filter:drop-shadow(0 0 20px rgba(0,196,204,0.5));
    letter-spacing:2px; animation:glow-pulse 3s ease-in-out infinite;
}
@keyframes glow-pulse {
    0%,100%{filter:drop-shadow(0 0 20px rgba(0,196,204,0.5))}
    50%{filter:drop-shadow(0 0 40px rgba(0,196,204,0.9)) drop-shadow(0 0 80px rgba(162,155,254,0.4))}
}
.header-subtitle { font-family:'Orbitron',monospace; font-size:0.7rem; letter-spacing:4px; color:rgba(0,196,204,0.6) !important; text-transform:uppercase; margin-top:8px; }
.divider-3d { height:1px; background:linear-gradient(90deg,transparent,#00c4cc,#a29bfe,#00c4cc,transparent); margin:1.5rem 0; box-shadow:0 0 10px rgba(0,196,204,0.5); }
.step-label { font-family:'Orbitron',monospace; color:#00c4cc !important; font-size:10px; font-weight:700; letter-spacing:3px; text-transform:uppercase; margin-bottom:8px; display:flex; align-items:center; gap:8px; }
.step-label::before { content:''; display:inline-block; width:6px; height:6px; background:#00c4cc; border-radius:50%; box-shadow:0 0 8px #00c4cc; animation:blink 2s infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }
.stButton button {
    background:linear-gradient(135deg,rgba(0,196,204,0.15),rgba(0,196,204,0.05)) !important;
    color:#00c4cc !important; font-family:'Orbitron',monospace !important;
    font-weight:700 !important; font-size:12px !important; letter-spacing:2px !important;
    border:1px solid rgba(0,196,204,0.5) !important; border-radius:4px !important;
    box-shadow:0 0 10px rgba(0,196,204,0.2),0 4px 15px rgba(0,0,0,0.5),inset 0 1px 0 rgba(255,255,255,0.1) !important;
    transition:all 0.3s ease !important;
}
.stButton button:hover {
    background:linear-gradient(135deg,rgba(0,196,204,0.3),rgba(0,196,204,0.1)) !important;
    border-color:#00c4cc !important;
    box-shadow:0 0 25px rgba(0,196,204,0.6),0 0 50px rgba(0,196,204,0.3),0 0 100px rgba(0,196,204,0.1),inset 0 1px 0 rgba(255,255,255,0.2) !important;
    transform:perspective(500px) translateZ(10px) translateY(-3px) !important;
    color:#ffffff !important;
}
div[data-baseweb="textarea"] textarea { background:rgba(2,5,16,0.8) !important; color:#00c4cc !important; border:1px solid rgba(0,196,204,0.2) !important; border-radius:4px !important; }
div[data-baseweb="textarea"] textarea:focus { border-color:rgba(0,196,204,0.7) !important; box-shadow:0 0 20px rgba(0,196,204,0.2) !important; }
div[data-baseweb="textarea"] textarea::placeholder { color:rgba(0,196,204,0.3) !important; }
div[data-baseweb="input"] input { background:rgba(2,5,16,0.8) !important; color:#00c4cc !important; border:1px solid rgba(0,196,204,0.2) !important; border-radius:4px !important; font-family:'Orbitron',monospace !important; }
div[data-baseweb="input"] input:focus { border-color:rgba(0,196,204,0.7) !important; }
.stRadio label { color:#a0aab4 !important; }
div[role="progressbar"] > div { background:linear-gradient(90deg,#00c4cc,#a29bfe,#00c4cc) !important; box-shadow:0 0 10px rgba(0,196,204,0.5) !important; }
div[data-testid="stDownloadButton"] button { background:transparent !important; color:#a29bfe !important; border:1px solid rgba(162,155,254,0.4) !important; font-family:'Orbitron',monospace !important; font-size:11px !important; }
div[data-testid="stDownloadButton"] button:hover { box-shadow:0 0 25px rgba(162,155,254,0.5) !important; border-color:#a29bfe !important; color:#ffffff !important; transform:translateY(-2px) !important; }
div[data-testid="stAlert"] { background:rgba(0,196,204,0.05) !important; border:1px solid rgba(0,196,204,0.3) !important; border-radius:4px !important; }
hr { border-color:rgba(0,196,204,0.1) !important; }
</style>

<canvas id="particles-canvas"></canvas>
<script>
const canvas = document.getElementById('particles-canvas');
const ctx = canvas.getContext('2d');
canvas.width = window.innerWidth; canvas.height = window.innerHeight;
const particles = [];
for(let i=0;i<80;i++) particles.push({x:Math.random()*canvas.width,y:Math.random()*canvas.height,size:Math.random()*1.5+0.3,speedX:(Math.random()-0.5)*0.3,speedY:(Math.random()-0.5)*0.3,opacity:Math.random()*0.5+0.1,color:Math.random()>0.5?'0,196,204':'162,155,254'});
function animate(){
    ctx.clearRect(0,0,canvas.width,canvas.height);
    particles.forEach(p=>{
        p.x+=p.speedX; p.y+=p.speedY;
        if(p.x<0)p.x=canvas.width; if(p.x>canvas.width)p.x=0;
        if(p.y<0)p.y=canvas.height; if(p.y>canvas.height)p.y=0;
        ctx.beginPath(); ctx.arc(p.x,p.y,p.size,0,Math.PI*2);
        ctx.fillStyle=`rgba(${p.color},${p.opacity})`; ctx.fill();
    });
    requestAnimationFrame(animate);
}
animate();
window.addEventListener('resize',()=>{canvas.width=window.innerWidth;canvas.height=window.innerHeight;});
</script>
""", unsafe_allow_html=True)

if "rodando" not in st.session_state:
    st.session_state.rodando = False
if "logs" not in st.session_state:
    st.session_state.logs = []
if "motor" not in st.session_state:
    st.session_state.motor = None
if "transcricao_atual" not in st.session_state:
    st.session_state.transcricao_atual = ""

st.markdown("""
<div class="header-3d">
    <h1>🎙 WIL É FODA<br>TRANSCRITOR</h1>
    <div class="header-subtitle">[ SISTEMA DE TRANSCRIÇÃO COM IA · V2.0 ]</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="divider-3d"></div>', unsafe_allow_html=True)

# ===================== CONFIGURAÇÃO DO MOTOR =====================
chave_groq_env = os.getenv("GROQ_API_KEY", "").strip()

st.markdown('<div class="step-label">00 · CONFIGURAÇÃO</div>', unsafe_allow_html=True)

if chave_groq_env:
    # Chave já salva no .env — só mostra o seletor de motor
    motor_escolhido = st.radio("Motor", options=["⚡ Groq (rápido)", "🖥 Whisper (local)"], label_visibility="collapsed")
    chave_groq = chave_groq_env
else:
    # Sem chave salva — mostra campo para digitar
    col_motor, col_chave = st.columns([1, 2])
    with col_motor:
        motor_escolhido = st.radio("Motor", options=["⚡ Groq (rápido)", "🖥 Whisper (local)"], label_visibility="collapsed")
    with col_chave:
        chave_groq = st.text_input("Chave API Groq", type="password", placeholder="Cole sua chave Groq aqui (gsk_...)", label_visibility="collapsed")

usar_groq = "Groq" in motor_escolhido

st.markdown('<div class="divider-3d"></div>', unsafe_allow_html=True)
st.markdown('<div class="step-label">01 · SELECIONAR ORIGEM</div>', unsafe_allow_html=True)
plataforma_label = st.radio("Origem", options=["TikTok", "Instagram", "YouTube"], horizontal=True, label_visibility="collapsed")
plataforma_map = {"TikTok": "tiktok", "Instagram": "instagram", "YouTube": "youtube"}
plataforma = plataforma_map[plataforma_label]

st.markdown('<div class="divider-3d"></div>', unsafe_allow_html=True)
st.markdown('<div class="step-label">02 · INSERIR LINKS · UM POR LINHA</div>', unsafe_allow_html=True)
texto_links = st.text_area("Links", height=180, placeholder="https://vt.tiktok.com/exemplo1/\nhttps://vt.tiktok.com/exemplo2/", label_visibility="collapsed")

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    iniciar = st.button("▶ INICIAR", type="primary", use_container_width=True, disabled=st.session_state.rodando)
with col2:
    juntar = st.button("⊕ JUNTAR", use_container_width=True)
with col3:
    limpar_log = st.button("✕ LIMPAR", use_container_width=True)

barra_progresso = st.empty()
status_texto = st.empty()
st.markdown('<div class="divider-3d"></div>', unsafe_allow_html=True)
st.markdown('<div class="step-label">03 · REGISTRO DE PROCESSO</div>', unsafe_allow_html=True)
area_log = st.empty()

def renderizar_log():
    texto = "\n".join(st.session_state.logs[-300:])
    area_log.code(texto if texto else "[ SISTEMA AGUARDANDO COMANDO... ]", language=None)

def callback_log(texto, tipo="info"):
    st.session_state.logs.append(texto)
    renderizar_log()

def callback_progresso(atual, total):
    barra_progresso.progress(atual / total if total else 0)
    status_texto.markdown(f"`[ PROCESSANDO {atual}/{total} · {int((atual/total)*100)}% CONCLUÍDO ]`")

if limpar_log:
    st.session_state.logs = []

renderizar_log()

if iniciar:
    links = [linha.strip() for linha in texto_links.splitlines() if linha.strip()]
    if not links:
        st.warning("Cole pelo menos um link antes de iniciar.")
    elif usar_groq and not chave_groq.strip():
        st.error("Cole sua chave da Groq no campo de configuração antes de iniciar.")
    else:
        st.session_state.rodando = True
        st.session_state.logs = []
        st.session_state.transcricao_atual = ""

        motor = MotorTranscricao(
            callback_log,
            callback_progresso,
            motor_ia="groq" if usar_groq else "whisper",
            chave_groq=chave_groq.strip() if usar_groq else None,
        )
        st.session_state.motor = motor

        with st.spinner("[ PROCESSANDO... NÃO FECHE ESTA ABA ]"):
            try:
                sucesso, falhas, caminhos_rodada = motor.processar_links(links, plataforma)
                st.success(f"✅ CONCLUÍDO · Sucesso: {sucesso} · Falhas: {falhas}")
                if caminhos_rodada:
                    caminho = motor.juntar_arquivos_especificos(caminhos_rodada)
                    if caminho:
                        with open(caminho, "r", encoding="utf-8") as f:
                            conteudo = f.read()
                        st.session_state.transcricao_atual = conteudo
                        st.download_button("⬇ BAIXAR TRANSCRIÇÕES (.TXT)", data=conteudo, file_name=os.path.basename(caminho), mime="text/plain", type="primary")
            except Exception as e:
                st.error(f"ERRO: {e}")
            finally:
                st.session_state.rodando = False

if juntar:
    motor_temp = st.session_state.motor or MotorTranscricao(callback_log, callback_progresso)
    quantidade, caminho = motor_temp.juntar_resultados(plataforma)
    if quantidade == 0:
        st.info(f"Nenhum resultado para {plataforma_label}. Transcreva primeiro.")
    else:
        st.success(f"{quantidade} transcrições juntadas.")
        with open(caminho, "r", encoding="utf-8") as f:
            conteudo = f.read()
        st.session_state.transcricao_atual = conteudo
        st.download_button("⬇ BAIXAR ARQUIVO JUNTADO (.TXT)", data=conteudo, file_name=os.path.basename(caminho), mime="text/plain")

st.markdown('<div class="divider-3d"></div>', unsafe_allow_html=True)
st.markdown('<div class="step-label">04 · DOSSIÊ COM IA</div>', unsafe_allow_html=True)

if st.session_state.transcricao_atual:
    st.caption("[ TRANSCRIÇÃO CARREGADA · PRONTA PARA ANÁLISE ]")
    observacao = st.text_area(
        "OBSERVAÇÕES",
        height=100,
        placeholder=(
            "Direcione o formato do dossiê. Exemplos:\n"
            "· Foque nos ganchos de copywriting\n"
            "· Gere 10 títulos virais baseados no conteúdo\n"
            "· Quero em formato de roteiro pronto para gravar\n"
            "· Extraia só as objeções e como contorná-las\n"
            "· Resuma em bullet points para gestor de tráfego"
        ),
        label_visibility="collapsed"
    )
    if st.button("⚡ GERAR DOSSIÊ COM IA", type="primary", use_container_width=True):
        with st.spinner("[ WIL ESTÁ GERANDO O DOSSIÊ... ]"):
            try:
                dossie = gerar_dossie(st.session_state.transcricao_atual, observacao)
                st.markdown('<div class="divider-3d"></div>', unsafe_allow_html=True)
                st.markdown('<div class="step-label">DOSSIÊ GERADO</div>', unsafe_allow_html=True)
                st.markdown(dossie)
                st.download_button("⬇ BAIXAR DOSSIÊ (.TXT)", data=dossie, file_name="dossie.txt", mime="text/plain")
            except Exception as e:
                st.error(f"ERRO: {e}")
else:
    st.caption("[ AGUARDANDO TRANSCRIÇÃO PARA LIBERAR DOSSIÊ ]")
