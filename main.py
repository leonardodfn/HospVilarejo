# -*- coding: utf-8 -*-

import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import db_manager
from config import TELEGRAM_TOKEN
from bot_handlers import admin_commands, guest_commands, message_handler

# --- Configuração de Logging ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

def main() -> None:
    """Inicia o bot do Telegram com a estrutura modular."""
    
    # Prepara o banco de dados
    db_manager.setup_database()

    # Cria a aplicação do bot
    application = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .connect_timeout(10)
        .read_timeout(10)
        .build()
    )

    # --- Registra os Handlers ---
    # Comandos para todos
    application.add_handler(CommandHandler("start", guest_commands.start))
    application.add_handler(CommandHandler("ajuda", guest_commands.help_command))
    application.add_handler(CommandHandler("checkin", guest_commands.checkin_command))
    
    # Comandos de Admin
    application.add_handler(CommandHandler("gerar_codigo", admin_commands.gerar_codigo_command))
    application.add_handler(CommandHandler("bloquear", admin_commands.bloquear_command))
    
    # Handler para mensagens de texto
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler.handle_any_message))

    # Inicia o bot
    logger.info("Bot com estrutura modular iniciado. Pressione Ctrl+C para parar.")
    application.run_polling(allowed_updates="ALL")

if __name__ == "__main__":
    main()

