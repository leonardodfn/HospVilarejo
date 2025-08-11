# -*- coding: utf-8 -*-

import sqlite3
import logging
import os
import pandas as pd
from config import DB_FILE

logger = logging.getLogger(__name__)

def setup_database():
    """Cria e verifica as tabelas necessárias no banco de dados."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedbacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT, guest_chat_id INTEGER NOT NULL,
            guest_identifier TEXT NOT NULL, guest_name TEXT, original_message TEXT NOT NULL,
            sentiment TEXT, suggested_reply TEXT, intention TEXT, category TEXT,
            status TEXT DEFAULT 'Aberto', timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS checkins (
            chat_id INTEGER PRIMARY KEY, guest_identifier TEXT NOT NULL UNIQUE,
            guest_name TEXT, checkin_time DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS access_codes (
            code TEXT PRIMARY KEY, guest_identifier TEXT NOT NULL,
            creation_time DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    logger.info(f"Banco de dados '{DB_FILE}' verificado e pronto.")

def get_checkin_status(chat_id: int) -> tuple | None:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT guest_identifier, guest_name FROM checkins WHERE chat_id = ?", (chat_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def perform_checkout_by_identifier(guest_identifier: str) -> int | None:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id FROM checkins WHERE guest_identifier = ?", (guest_identifier,))
    result = cursor.fetchone()
    if result:
        chat_id = result[0]
        cursor.execute("DELETE FROM checkins WHERE guest_identifier = ?", (guest_identifier,))
        conn.commit()
    conn.close()
    return result[0] if result else None

def generate_and_store_code(guest_identifier: str, code: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO access_codes (code, guest_identifier) VALUES (?, ?)", (code, guest_identifier))
    conn.commit()
    conn.close()

def validate_and_use_code(code: str, user_id: int, user_name: str) -> str | None:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT guest_identifier FROM access_codes WHERE code = ?", (code,))
    result = cursor.fetchone()
    if result:
        guest_identifier = result[0]
        cursor.execute("INSERT OR REPLACE INTO checkins (chat_id, guest_identifier, guest_name) VALUES (?, ?, ?)", (user_id, guest_identifier, user_name))
        cursor.execute("DELETE FROM access_codes WHERE code = ?", (code,))
        conn.commit()
    conn.close()
    return result[0] if result else None

def save_feedback(chat_id, guest_identifier, guest_name, message, analysis):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO feedbacks (guest_chat_id, guest_identifier, guest_name, original_message, sentiment, suggested_reply, intention, category) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (chat_id, guest_identifier, guest_name, message, analysis.get('sentimento'), analysis.get('resposta_sugerida'), analysis.get('intencao'), analysis.get('categoria'))
        )
        conn.commit()
        conn.close()
        logger.info(f"Interação do identificador '{guest_identifier}' salva no banco de dados.")
    except sqlite3.Error as e:
        logger.error(f"Erro ao salvar interação no banco de dados: {e}")

def load_data_for_dashboard():
    """Carrega os dados da tabela de feedbacks para o dashboard."""
    if not os.path.exists(DB_FILE):
        return pd.DataFrame(columns=[
            'id', 'guest_chat_id', 'guest_identifier', 'guest_name', 
            'original_message', 'sentiment', 'suggested_reply', 
            'intention', 'category', 'status', 'timestamp'
        ])
    
    conn = sqlite3.connect(DB_FILE)
    try:
        df = pd.read_sql_query("SELECT * FROM feedbacks", conn)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    finally:
        conn.close()
