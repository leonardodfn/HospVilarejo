# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do ficheiro .env
load_dotenv()

# --- Configurações de API e IDs ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
STAFF_CHAT_ID = os.getenv("STAFF_CHAT_ID")

# --- CONTROLE DE ACESSO ---
# Lê os IDs de admin, os separa por vírgula e os converte para inteiros
admin_ids_str = os.getenv("ADMIN_CHAT_IDS", "")
ADMIN_CHAT_IDS = [int(admin_id.strip()) for admin_id in admin_ids_str.split(',') if admin_id.strip()]

# --- Gerenciamento de Banco de Dados ---
DB_FILE = "smartnps_persistent.db"
