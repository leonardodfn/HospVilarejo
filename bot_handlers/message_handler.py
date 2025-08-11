# -*- coding: utf-8 -*-

import logging
from telegram import Update
from telegram.ext import ContextTypes
import db_manager
import ai_analyzer
from config import STAFF_CHAT_ID
from .guest_commands import help_command

logger = logging.getLogger(__name__)

async def handle_any_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Processa qualquer mensagem, verificando o check-in no banco de dados."""
    chat_id = update.effective_chat.id
    checkin_info = db_manager.get_checkin_status(chat_id)
    if not checkin_info:
        await update.message.reply_text("Seu acesso ainda não foi liberado. Use /checkin <codigo> para começar.")
        return
    guest_identifier, guest_name = checkin_info
    guest_message = update.message.text
    logger.info(f"Recebida mensagem do identificador '{guest_identifier}': '{guest_message}'")
    
    analise = ai_analyzer.analisar_mensagem_com_gemini(guest_message)
    
    if not analise:
        await update.message.reply_text("Desculpe, estou com dificuldades para processar sua mensagem. Já notifiquei a recepção para que entrem em contato.")
        alerta_falha = f"""
⚠️ ALERTA DE FALHA NA IA ⚠️
- Hóspede (Quarto/Reserva): <b>{guest_identifier}</b>
- Mensagem original: "{guest_message}"
Por favor, entre em contato com o hóspede manualmente.
"""
        try:
            await context.bot.send_message(chat_id=STAFF_CHAT_ID, text=alerta_falha, parse_mode='HTML')
            logger.info(f"Alerta de FALHA NA IA enviado para a equipe sobre o identificador '{guest_identifier}'.")
        except Exception as e:
            logger.error(f"Falha ao enviar o ALERTA DE FALHA para a equipe: {e}")
        return

    await update.message.reply_text(analise.get('resposta_sugerida', 'Obrigado!'))
    
    db_manager.save_feedback(chat_id, guest_identifier, guest_name, guest_message, analise)

    intencao = analise.get('intencao')
    sentiment = analise.get('sentimento') # Pega o sentimento para o log
    category = analise.get('categoria')

    # --- LINHA CORRIGIDA ---
    # Adicionado o 'sentiment' de volta à mensagem de log.
    logger.info(f"Análise -> Intenção: {intencao}, Sentimento: {sentiment}, Categoria: {category}")

    if intencao == 'Reclamacao/Pedido':
        alerta = f"""
🚨 NOVO PEDIDO / RECLAMAÇÃO 🚨
- Hóspede (Quarto/Reserva): <b>{guest_identifier}</b>
- Categoria: <b>{category or 'Não especificada'}</b>
- Mensagem: "{guest_message}"
"""
        try:
            await context.bot.send_message(chat_id=STAFF_CHAT_ID, text=alerta, parse_mode='HTML')
            logger.info(f"Alerta enviado para a equipe sobre o identificador '{guest_identifier}'.")
        except Exception as e:
            logger.error(f"Falha ao enviar alerta para a equipe: {e}")
    elif intencao == 'Fora_De_Escopo':
        await help_command(update, context)
