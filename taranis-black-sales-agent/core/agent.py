import os
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

SYSTEM_PROMPT = """
# SYSTEM PROMPT: TARANIS BLACK — AI SALES & B2B COPILOT AGENT

## 1. IDENTIDADE E PAPEL
Você é o **Taranis Sales Copilot**, um agente inteligente especializado em Engenharia de Vendas B2B, Inteligência Comercial e Simulação Negocial para a Taranis Black.
Sua missão é atuar em dois modos operacionais principais:
1. **MODO COPILOTO (Apoio ao Vendedor):** Auxiliar SDRs e Closers com argumentos estratégicos em tempo real, cálculos de ROI, qualificação de leads e contorno de objeções complexas.
2. **MODO SIMULADOR / ROLEPLAY (Treinador C-Level):** Atuar como Dr. Roberto Mendes, Diretor Comercial (C-Level) cético, exigente quanto a custos e intransigente em relação à conformidade com a LGPD e GDPR.

## 2. GOVERNANÇA, SEGURANÇA E PROTEÇÃO INTERNACIONAL DE DADOS
- **Anonimização Ativa:** Substitua automaticamente qualquer Dado Pessoal Identificável (PII), como Documentos de Identificação Nacional (BI, NIF, SSN, Passaporte), e-mails pessoais ou dados bancários por tags de anonimização (ex: `[DOCUMENTO_PESSOAL_ANONIMIZADO]`).
- **Arquitetura Zero Data Retention & RAG:** Todos os dados corporativos são processados sob isolamento estrito via RAG, sem retenção para treino de modelos públicos globais.
- **Limitação de Escopo:** Recuse responder a perguntas fora do contexto corporativo.
- **Human-in-the-Loop (HITL):** Nenhuma proposta ou e-mail pode ser despachado sem revisão e aprovação final do executivo humano.

## 3. MATRIZ DE 5 OBJEÇÕES B2B
- **Preço ("Acima do orçamento"):** Reenquadre para Custo de Inação e ROI comprovado.
- **Prazo ("Sem tempo/equipe"):** Apresente Onboarding Guiado e Time-to-Value em 14 dias úteis.
- **Segurança ("Receio com LGPD/GDPR"):** Demonstre a arquitetura RAG isolada e Zero Data Retention.
- **Concorrência ("Já usamos outra solução"):** Destaque o menor TCO (Custo Total de Propriedade) e diferenciação técnica.
- **Maturidade ("Não estamos prontos"):** Proponha adoção modular por fases.

## 4. FORMATO DE SAÍDA
Responda com tom executivo, direto, persuasivo e fundamentado em métricas de produtividade. Estruture o texto com marcadores e encerre com uma chamada de avanço negocial.
"""

class TaranisSalesAgent:
    def __init__(self, mode: str = "copilot", provider: str = "Google Gemini", api_key: str = None, custom_model: str = None):
        self.mode = mode
        self.provider = provider
        clean_key = (api_key or "").strip()
        
        if not clean_key:
            raise ValueError(f"Insira uma API Key válida para o provedor {provider}.")

        self.api_key = clean_key
        temp = 0.3 if mode == "copilot" else 0.7

        # Configuração flexível por Provedor com fallback de modelo padrão
        if provider == "Google Gemini":
            from langchain_google_genai import ChatGoogleGenerativeAI
            # 'gemini-1.5-flash' ou 'gemini-2.0-flash'
            model = custom_model.strip() if custom_model and custom_model.strip() else "gemini-1.5-flash"
            self.llm = ChatGoogleGenerativeAI(
                model=model,
                google_api_key=self.api_key,
                temperature=temp
            )

        elif provider == "Groq (Gratuito/Rápido)":
            from langchain_groq import ChatGroq
            if not self.api_key.startswith("gsk_"):
                raise ValueError("Para o Groq, a chave deve começar com 'gsk_'.")
            # Modelo padrão atualizado do Groq
            model = custom_model.strip() if custom_model and custom_model.strip() else "llama-3.3-70b-versatile"
            self.llm = ChatGroq(
                model=model,
                api_key=self.api_key,
                temperature=temp
            )

        elif provider == "OpenAI":
            from langchain_openai import ChatOpenAI
            if not self.api_key.startswith("sk-"):
                raise ValueError("Para a OpenAI, a chave deve começar com 'sk-'.")
            model = custom_model.strip() if custom_model and custom_model.strip() else "gpt-4o-mini"
            self.llm = ChatOpenAI(
                model=model,
                api_key=self.api_key,
                temperature=temp
            )

        elif provider == "DeepSeek":
            from langchain_openai import ChatOpenAI
            model = custom_model.strip() if custom_model and custom_model.strip() else "deepseek-chat"
            self.llm = ChatOpenAI(
                model=model,
                api_key=self.api_key,
                base_url="https://api.deepseek.com",
                temperature=temp
            )
        else:
            raise ValueError(f"Provedor {provider} não suportado.")

        self.chat_history = []

    def chat(self, user_input: str) -> str:
        mode_instruction = f"\n\n[MODO OPERACIONAL ATIVO: {self.mode.upper()}]"
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT + mode_instruction),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "history": self.chat_history,
            "input": user_input
        })

        self.chat_history.append(HumanMessage(content=user_input))
        self.chat_history.append(AIMessage(content=response.content))
        return response.content

    def clear_history(self):
        self.chat_history = []
