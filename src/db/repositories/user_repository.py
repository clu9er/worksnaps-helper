import psycopg2
import logging as logger

from utils.aes_cipher import AESCipher

from config_reader import config

def insert_user(user_id: str, username: str, first_name: str, last_name: str, token: str, worksnaps_user_id: int):
    connection = None
    try:
        connection = psycopg2.connect(config.database.connection_string)
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO users (user_id, username, first_name, last_name)
            VALUES (%s, %s, %s, %s)
        """, (user_id, username, first_name, last_name))

        cipher = AESCipher(config.encryption.key)

        token = cipher.encrypt(token)

        cursor.execute("""
            INSERT INTO api_tokens (api_token)
            VALUES (%s) RETURNING token_id
        """, (token,))

        token_id = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO user_tokens (user_id, token_id, worksnaps_user_id)
            VALUES (%s, %s, %s)
        """, (user_id, token_id, worksnaps_user_id))

        connection.commit()
    except Exception as e:
        logger.error(f"Error inserting user: {e}")
        if connection:
            connection.rollback()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def is_user_exists(user_id: str) -> bool:
    connection = None
    try:
        connection = psycopg2.connect(config.database.connection_string)
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        rows = cursor.fetchall()

        return len(rows) > 0
    except Exception as e:
        logger.error(f"Error checking if user exists: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
