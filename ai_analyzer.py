# -*- coding: utf-8 -*-

import requests
import json
import time
import logging
from config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

GEMINI_MODEL_NAME = "gemini-1.5-flash-latest"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL_NAME}:generateContent?key={GEMINI_API_KEY}"

def analisar_mensagem_com_gemini(texto_mensagem: str) -> dict | None:
    """Analisa a mensagem com a IA, incluindo lógica de retentativa."""
    headers = {"Content-Type": "application/json"}
    prompt = f"""
    Analise a seguinte mensagem de um hóspede de hotel. Sua tarefa é quádrupla:
    1.  Determine a INTENÇÃO: 'Reclamacao/Pedido', 'Conversa/Casual', ou 'Fora_De_Escopo'.
    2.  Classifique o SENTIMENTO: 'Positivo', 'Neutro' ou 'Negativo'.
    3.  Se a intenção for 'Reclamacao/Pedido', categorize o tópico em uma das seguintes opções: "Problema no Banheiro", "Solicitação de Itens", "Eletrônicos (TV/Ar)", "Barulho ou Incômodo", "Limpeza", "Internet/Wi-Fi", "Outros". Se não for uma reclamação, retorne null para a categoria.
    4.  Gere uma RESPOSTA apropriada em português. Para pedidos, confirme o recebimento sem estimar tempo.

    Retorne sua análise estritamente no seguinte formato JSON:
    {{
      "intencao": "...",
      "sentimento": "...",
      "categoria": "...",
      "resposta_sugerida": "..."
    }}
    Mensagem do hóspede: "{texto_mensagem}"
    """
    payload = {"contents": [{"parts": [{"text": prompt}]}],"generationConfig": {"response_mime_type": "application/json"}}
    
    max_retries = 3
    delay = 1

    for attempt in range(max_retries):
        try:
            response = requests.post(GEMINI_API_URL, headers=headers, data=json.dumps(payload), timeout=20)
            if response.status_code == 429:
                logger.warning(f"Rate limit atingido. Tentando novamente em {delay} segundos...")
                time.sleep(delay)
                delay *= 2
                continue
            response.raise_for_status()
            api_response_text = response.json()['candidates'][0]['content']['parts'][0]['text']
            return json.loads(api_response_text)
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na chamada da API na tentativa {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)
                delay *= 2
            else:
                logger.error("Máximo de retentativas atingido.")
                return None
    return None

