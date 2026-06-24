import sqlite3
from datetime import datetime

def get_connection(db_path="currency_converter.db"):
    """Устанавливает соединение с базой данных."""
    return sqlite3.connect(db_path)

def init_db(db_path="currency_converter.db"):
    """Создает таблицы, если они еще не созданы."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rates (
                from_currency TEXT NOT NULL,
                to_currency TEXT NOT NULL,
                rate REAL NOT NULL,
                PRIMARY KEY (from_currency, to_currency)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                from_currency TEXT NOT NULL,
                to_currency TEXT NOT NULL,
                amount_from REAL NOT NULL,
                amount_to REAL NOT NULL,
                rate REAL NOT NULL
            )
        """)
        conn.commit()

def save_or_update_rate(from_curr, to_curr, rate, db_path="currency_converter.db"):
    """Добавляет новый курс или обновляет существующий."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO rates (from_currency, to_currency, rate)
            VALUES (?, ?, ?)
            ON CONFLICT(from_currency, to_currency) 
            DO UPDATE SET rate = excluded.rate
        """, (from_curr.upper(), to_curr.upper(), float(rate)))
        conn.commit()

def get_rate(from_curr, to_curr, db_path="currency_converter.db"):
    """Возвращает курс для пары валют или None, если курс не найден."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT rate FROM rates 
            WHERE from_currency = ? AND to_currency = ?
        """, (from_curr.upper(), to_curr.upper()))
        result = cursor.fetchone()
        return result[0] if result else None

def add_history_record(from_curr, to_curr, amount_from, amount_to, rate, db_path="currency_converter.db"):
    """Записывает операцию конвертации в историю."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO history (timestamp, from_currency, to_currency, amount_from, amount_to, rate)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (timestamp, from_curr.upper(), to_curr.upper(), float(amount_from), float(amount_to), float(rate)))
        conn.commit()

def get_all_history(db_path="currency_converter.db"):
    """Возвращает все записи из истории операций."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp, from_currency, to_currency, amount_from, amount_to, rate FROM history ORDER BY id DESC")
        return cursor.fetchall()