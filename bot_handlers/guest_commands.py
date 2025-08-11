# -*- coding: utf-8 -*-

import logging
from telegram import Update
from telegram.ext import ContextTypes
import db_manager

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mensagem de boas-vindas que verifica o estado de check-in."""
    chat_id = update.effective_chat.id
    checkin_info = db_manager.get_checkin_status(chat_id)
    if checkin_info:
        guest_identifier, guest_name = checkin_info
        await update.message.reply_html(f"Olá novamente, {guest_name}! Você já está conectado como o quarto/reserva <b>{guest_identifier}</b>.\n\nComo posso ajudar? Se precisar de ajuda, digite /ajuda.")
    else:
        await update.message.reply_html("Olá! Bem-vindo(a) ao assistente virtual do Hotel Vilarejo.\n\nPara ativar o serviço, por favor, insira o código de acesso fornecido pela recepção usando o comando /checkin. Por exemplo:\n<code>/checkin SEUCODIGO</code>")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Exibe uma mensagem de ajuda."""
    help_text = """
Olá! Eu sou o assistente virtual do Hotel Vilarejo.

Você pode me usar para:
✅ *Reportar problemas no seu quarto:*
   - "O ar condicionado não está gelando."
   - "O chuveiro está com pouca pressão."

✅ *Solicitar itens ou serviços:*
   - "Preciso de mais toalhas."
   - "Poderiam trazer um travesseiro extra?"

Basta me enviar uma mensagem com o que você precisa!
    """
    await update.message.reply_html(help_text)

async def checkin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Realiza o check-in usando um código de acesso único."""
    chat_id = update.effective_chat.id
    user = update.effective_user
    if db_manager.get_checkin_status(chat_id):
        await update.message.reply_text("Você já está com um check-in ativo.")
        return
    if not context.args:
        await update.message.reply_text("Uso: /checkin <codigo_de_acesso>")
        return
    code = context.args[0].upper()
    guest_identifier = db_manager.validate_and_use_code(code, chat_id, user.full_name)
    if guest_identifier:
        await update.message.reply_html(f"✅ Check-in realizado com sucesso para o quarto/reserva <b>{guest_identifier}</b>!")
        await help_command(update, context)
        logger.info(f"Hóspede {user.full_name} ({chat_id}) usou o código {code} para fazer check-in no quarto {guest_identifier}.")
    else:
        await update.message.reply_text("Código de acesso inválido ou expirado. Por favor, solicite um novo código na recepção.")
        logger.warning(f"Tentativa de check-in falhou para o chat {chat_id} com o código {code}.")

