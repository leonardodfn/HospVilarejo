# -*- coding: utf-8 -*-

import logging
import secrets
import string
from telegram import Update
from telegram.ext import ContextTypes
import db_manager
from config import ADMIN_CHAT_IDS

logger = logging.getLogger(__name__)

async def gerar_codigo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """(Admin) Gera um código de acesso único para um quarto/reserva."""
    admin_id = update.effective_chat.id
    if admin_id not in ADMIN_CHAT_IDS: return
    if not context.args:
        await update.message.reply_text("Uso: /gerar_codigo <quarto_reserva>")
        return
    guest_identifier = context.args[0]
    code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(6))
    db_manager.generate_and_store_code(guest_identifier, code)
    await update.message.reply_html(f"✅ Código de acesso para o quarto/reserva <b>{guest_identifier}</b>:\n\n<code>{code}</code>\n\nEste código é de uso único.")
    logger.info(f"Admin {admin_id} gerou o código {code} para o identificador {guest_identifier}.")

async def bloquear_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """(Admin) Bloqueia o acesso de um hóspede."""
    admin_id = update.effective_chat.id
    if admin_id not in ADMIN_CHAT_IDS: return
    if not context.args:
        await update.message.reply_text("Uso: /bloquear <quarto_reserva>")
        return
    guest_identifier = context.args[0]
    guest_chat_id = db_manager.perform_checkout_by_identifier(guest_identifier)
    if guest_chat_id:
        await update.message.reply_html(f"✅ Acesso para o quarto/reserva <b>{guest_identifier}</b> foi bloqueado com sucesso.")
        try:
            await context.bot.send_message(chat_id=guest_chat_id, text="Seu acesso ao assistente virtual foi finalizado. Agradecemos a sua estadia no Hotel Vilarejo! 👋")
        except Exception as e:
            await update.message.reply_text(f"Não foi possível notificar o hóspede (Chat ID: {guest_chat_id}). Erro: {e}")
        logger.info(f"Admin {admin_id} bloqueou o acesso para o identificador '{guest_identifier}'.")
    else:
        await update.message.reply_text(f"Nenhum check-in ativo encontrado para o quarto/reserva {guest_identifier}.")

