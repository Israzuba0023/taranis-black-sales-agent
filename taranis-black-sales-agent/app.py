import os
import streamlit as st
from PIL import Image
from core.agent import TaranisSalesAgent
from core.guardrails import SafetyGuardrails

# 1. Configuração da Página
st.set_page_config(
    page_title="Taranis Black — AI Sales Suite B2B",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Estilo Visual (Dark Executive)
st.markdown("""
<style>
    .stApp { background-color: #0A0E14; color: #E6EDF3; }
    .main-title {
        font-size: 2.3rem; font-weight: 800;
        background: linear-gradient(90deg, #00D2FF 0%, #3B82F6 50%, #90EAFF 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-title { font-size: 1rem; color: #8B949E; margin-bottom: 2rem; }
    [data-testid="stSidebar"] { background-color: #11161D; border-right: 1px solid #1F2937; }
    .stButton>button {
        background: linear-gradient(90deg, #0052CC 0%, #00D2FF 100%);
        color: #FFFFFF; font-weight: 600; border: none; border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)

# 3. Logo
LOGO_PATH = os.path.join("assets", "taranis_logo.png")
if os.path.exists(LOGO_PATH):
    st.sidebar.image(Image.open(LOGO_PATH), use_container_width=True)
else:
    st.sidebar.title("🛡️ TARANIS BLACK")

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Provedor & API Key")

provider = st.sidebar.selectbox(
    "Escolha o Provedor de IA:",
    ("Google Gemini", "Groq (Gratuito/Rápido)", "OpenAI", "DeepSeek")
)

# Modelos padrão sugeridos para cada API
DEFAULT_MODELS = {
    "Google Gemini": "gemini-1.5-flash",
    "Groq (Gratuito/Rápido)": "llama-3.3-70b-versatile",
    "OpenAI": "gpt-4o-mini",
    "DeepSeek": "deepseek-chat"
}

# Permite ao utilizador usar o modelo padrão ou escrever o nome de um modelo novo
model_name = st.sidebar.text_input("ID do Modelo:", value=DEFAULT_MODELS[provider])

key_hints = {
    "Google Gemini": "Obtenha a chave em: aistudio.google.com",
    "Groq (Gratuito/Rápido)": "Obtenha a chave em: console.groq.com",
    "OpenAI": "Obtenha a chave em: platform.openai.com",
    "DeepSeek": "Obtenha a chave em: platform.deepseek.com"
}
st.sidebar.caption(f"💡 {key_hints[provider]}")

raw_api_key = st.sidebar.text_input(f"API Key ({provider}):", type="password")
api_key = raw_api_key.strip()

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Modo do Agente")

mode_selection = st.sidebar.radio(
    "Modo de Operação:",
    ("Copiloto Comercial (SDR/Closer)", "Simulador C-Level (Roleplay B2B)")
)
mode_key = "copilot" if "Copiloto" in mode_selection else "simulator"

if st.sidebar.button("🧹 Limpar Conversa"):
    st.session_state.messages = []
    if "agent" in st.session_state and st.session_state.agent:
        st.session_state.agent.clear_history()
    st.rerun()

# 4. Área Principal
st.markdown('<div class="main-title">Taranis Black — AI Sales Suite B2B</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-title">Provedor: <b>{provider}</b> ({model_name}) | Modo: <b>{mode_selection}</b></div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Detetor de alterações dinâmicas
key_changed = st.session_state.get("previous_api_key") != api_key
provider_changed = st.session_state.get("previous_provider") != provider
model_changed = st.session_state.get("previous_model") != model_name
mode_changed = st.session_state.get("current_mode") != mode_key

if "agent" not in st.session_state or key_changed or provider_changed or model_changed or mode_changed:
    if api_key:
        try:
            st.session_state.agent = TaranisSalesAgent(
                mode=mode_key,
                provider=provider,
                api_key=api_key,
                custom_model=model_name
            )
            st.session_state.current_mode = mode_key
            st.session_state.previous_api_key = api_key
            st.session_state.previous_provider = provider
            st.session_state.previous_model = model_name
        except Exception as e:
            st.session_state.agent = None
            st.sidebar.error(f"Erro ao ligar ao provedor: {str(e)}")
    else:
        st.session_state.agent = None

if not st.session_state.get("agent"):
    st.info(f"👋 **Bem-vindo à Taranis Black!** Insira a sua API Key do **{provider}** no menu lateral. Para testar sem custos, selecione **Groq** ou **Google Gemini**!")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_prompt := st.chat_input("Digite sua mensagem para o agente comercial..."):
    if not st.session_state.get("agent"):
        st.error(f"Insira uma API Key válida do {provider} no menu lateral.")
        st.stop()

    sanitized_prompt = SafetyGuardrails.sanitize_input(user_prompt)
    
    if not SafetyGuardrails.validate_scope(sanitized_prompt):
        st.error("⚠️ **Bloqueio de Governança:** Solicitação fora do escopo corporativo.")
    else:
        st.session_state.messages.append({"role": "user", "content": sanitized_prompt})
        with st.chat_message("user"):
            st.markdown(sanitized_prompt)

        with st.chat_message("assistant"):
            with st.spinner(f"Processando estratégia via {provider}..."):
                try:
                    bot_response = st.session_state.agent.chat(sanitized_prompt)
                    st.markdown(bot_response)
                    st.session_state.messages.append({"role": "assistant", "content": bot_response})
                except Exception as err:
                    st.error(f"Erro na resposta do modelo ({model_name}): {str(err)}")
