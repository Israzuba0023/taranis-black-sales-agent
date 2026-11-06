import os
import streamlit as st
from PIL import Image
from core.agent import TaranisSalesAgent
from core.guardrails import SafetyGuardrails

# 1. Configuração de Página
st.set_page_config(
    page_title="Taranis Black — AI Sales Suite B2B",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Estilização Visual (Dark Executive / Cyberspace)
st.markdown("""
<style>
    .stApp {
        background-color: #0A0E14;
        color: #E6EDF3;
    }
    
    .main-title {
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #00D2FF 0%, #3B82F6 50%, #90EAFF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    
    .sub-title {
        font-size: 1rem;
        color: #8B949E;
        margin-bottom: 2rem;
    }

    [data-testid="stSidebar"] {
        background-color: #11161D;
        border-right: 1px solid #1F2937;
    }

    .stButton>button {
        background: linear-gradient(90deg, #0052CC 0%, #00D2FF 100%);
        color: #FFFFFF;
        font-weight: 600;
        border: none;
        border-radius: 6px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #00D2FF 0%, #0052CC 100%);
        box-shadow: 0 0 10px rgba(0, 210, 255, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# 3. Carregamento da Logo
LOGO_PATH = os.path.join("assets", "taranis_logo.png")

if os.path.exists(LOGO_PATH):
    logo_img = Image.open(LOGO_PATH)
    st.sidebar.image(logo_img, use_container_width=True)
else:
    st.sidebar.title("🛡️ TARANIS BLACK")

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Provedor & Modelo de IA")

# Seleção de Provedor de IA
provider = st.sidebar.selectbox(
    "Escolha o Provedor de IA:",
    ("Google Gemini", "Groq (Gratuito/Rápido)", "OpenAI", "DeepSeek")
)

# Sugestões de Modelos por Provedor
model_options = {
    "Google Gemini": ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp"],
    "Groq (Gratuito/Rápido)": ["llama-3.3-70b-versatile", "mixtral-8x7b-32768", "llama3-8b-8192"],
    "OpenAI": ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
    "DeepSeek": ["deepseek-chat", "deepseek-coder"]
}

selected_model = st.sidebar.selectbox("Modelo:", model_options[provider])

# Dica sobre onde obter chaves gratuitas
key_hints = {
    "Google Gemini": "Obtenha uma chave gratuita no Google AI Studio (aistudio.google.com)",
    "Groq (Gratuito/Rápido)": "Obtenha uma chave gratuita no Groq Cloud (console.groq.com)",
    "OpenAI": "Obtenha sua chave no painel da OpenAI (platform.openai.com)",
    "DeepSeek": "Obtenha sua chave no painel da DeepSeek (platform.deepseek.com)"
}
st.sidebar.caption(f"💡 {key_hints[provider]}")

# Captura de API Key e limpeza de espaços
raw_api_key = st.sidebar.text_input(f"API Key ({provider}):", type="password")
api_key = raw_api_key.strip()

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Modo do Agente")

# Seleção de Modo
mode_selection = st.sidebar.radio(
    "Modo de Operação:",
    ("Copiloto Comercial (SDR/Closer)", "Simulador C-Level (Roleplay B2B)")
)

mode_key = "copilot" if "Copiloto" in mode_selection else "simulator"

# Limpeza de Conversa
if st.sidebar.button("🧹 Limpar Conversa"):
    st.session_state.messages = []
    if "agent" in st.session_state and st.session_state.agent:
        st.session_state.agent.clear_history()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='font-size: 0.8rem; color: #8B949E;'>
<b>Taranis Black AI Suite</b><br>
Challenge ONE G11 — AI for Business<br>
<i>Arquitetura Multi-LLM & Governança Global</i>
</div>
""", unsafe_allow_html=True)

# 4. Área Principal
st.markdown('<div class="main-title">Taranis Black — AI Sales Suite B2B</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-title">Provedor: <b>{provider} ({selected_model})</b> | Modo: <b>{mode_selection}</b></div>', unsafe_allow_html=True)

# Inicialização de mensagens na sessão
if "messages" not in st.session_state:
    st.session_state.messages = []

# Deteção dinâmica de alteração de Chave, Provedor ou Modo
key_changed = st.session_state.get("previous_api_key") != api_key
provider_changed = st.session_state.get("previous_provider") != provider
model_changed = st.session_state.get("previous_model") != selected_model
mode_changed = st.session_state.get("current_mode") != mode_key

if "agent" not in st.session_state or key_changed or provider_changed or model_changed or mode_changed:
    if api_key:
        try:
            st.session_state.agent = TaranisSalesAgent(
                mode=mode_key,
                provider=provider,
                api_key=api_key,
                model_name=selected_model
            )
            st.session_state.current_mode = mode_key
            st.session_state.previous_api_key = api_key
            st.session_state.previous_provider = provider
            st.session_state.previous_model = selected_model
        except Exception as e:
            st.session_state.agent = None
            st.sidebar.error(f"Erro no provedor: {str(e)}")
    else:
        st.session_state.agent = None

if not st.session_state.get("agent"):
    st.info(f"👋 **Bem-vindo à Taranis Black!** Insira sua API Key do **{provider}** no painel lateral para ativar o agente. Se não tem saldo na OpenAI, selecione **Google Gemini** ou **Groq** para utilizar gratuitamente!")

# Renderização do histórico de mensagens
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Prompt de entrada do utilizador
if user_prompt := st.chat_input("Digite sua mensagem para o agente comercial..."):
    if not st.session_state.get("agent"):
        st.error(f"Insira uma API Key válida do {provider} no painel lateral antes de enviar mensagens.")
        st.stop()

    # Validação de Governança
    sanitized_prompt = SafetyGuardrails.sanitize_input(user_prompt)
    
    if not SafetyGuardrails.validate_scope(sanitized_prompt):
        st.error("⚠️ **Bloqueio de Governança Taranis Black:** Esta solicitação está fora do escopo corporativo.")
    else:
        st.session_state.messages.append({"role": "user", "content": sanitized_prompt})
        with st.chat_message("user"):
            st.markdown(sanitized_prompt)

        with st.chat_message("assistant"):
            with st.spinner(f"Analisando dados estratégicos via {provider}..."):
                try:
                    bot_response = st.session_state.agent.chat(sanitized_prompt)
                    st.markdown(bot_response)
                    st.session_state.messages.append({"role": "assistant", "content": bot_response})
                except Exception as err:
                    st.error(f"Erro na resposta do modelo: {str(err)}")
