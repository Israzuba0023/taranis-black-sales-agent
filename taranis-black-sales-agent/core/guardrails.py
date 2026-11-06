import re

class SafetyGuardrails:
    """
    Filtros de governança, anonimização de PII internacional (GDPR / LGPD)
    e validação de escopo corporativo.
    """
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """
        Anonimiza documentos de identificação pessoal/fiscal internacionais (BI, NIF, SSN, Passaporte),
        números de telefone globais e e-mails de forma padronizada.
        """
        # 1. Anonimização de E-mails
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_ANONIMIZADO]', text)
        
        # 2. Anonimização de Números de Identificação Pessoal / Fiscal (BI, NIF, CPF, SSN, Passaporte)
        text = re.sub(r'\b\d{3}[\s.-]?\d{3}[\s.-]?\d{3}[\s.-]?\d{2,3}\b', '[DOCUMENTO_PESSOAL_ANONIMIZADO]', text)
        text = re.sub(r'\b[A-Z0-9]{8,14}\b', '[DOCUMENTO_PESSOAL_ANONIMIZADO]', text)
        
        # 3. Anonimização de Telefones Internacionais (+244..., +351..., +1..., etc.)
        text = re.sub(r'\+?\d{1,4}?[\s.-]?\(?\d{1,4}?\)?[\s.-]?\d{3,4}[\s.-]?\d{3,4}', '[TELEFONE_ANONIMIZADO]', text)
        
        return text

    @staticmethod
    def validate_scope(text: str) -> bool:
        """
        Bloqueia requisições fora do escopo corporativo e comercial da Taranis Black.
        """
        forbidden_keywords = [
            "receita de bolo", "resultado do jogo", "futebol", "piada", 
            "horóscopo", "política partidária", "criptomoeda"
        ]
        text_lower = text.lower()
        if any(keyword in text_lower for keyword in forbidden_keywords):
            return False
        return True
