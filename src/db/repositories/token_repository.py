import psycopg2
import logging

from typing import List
from models.token import UserToken

from db.redis.main import client as redis

from config_reader import config

def insert_token(user_id: str, token: str, worksnaps_user_id: str) -> None:
    connection = psycopg2.connect(config.database.connection_string)
    
    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO api_tokens (api_token) VALUES (%s) RETURNING token_id",
            (token,)
        )
        token_id = cursor.fetchone()[0]

        cursor.execute(
            "INSERT INTO user_tokens (user_id, token_id, worksnaps_user_id) VALUES (%s, %s, %s)",
            (user_id, token_id, worksnaps_user_id)
        )

        connection.commit()
    except Exception as e:
        logging.error(f"Error inserting token: {e}")
        connection.rollback()
        return None
    finally:
        cursor.close()
        connection.close()

def get_tokens(user_id: int) -> List[UserToken]:
    try:
        connection = psycopg2.connect(config.database.connection_string)
        cursor = connection.cursor()

        cursor.execute("""
                    SELECT t.token_id, t.api_token, ut.worksnaps_user_id, t.rate, t.currency, ut.user_id
                    FROM api_tokens t
                    JOIN user_tokens ut ON t.token_id = ut.token_id
                    WHERE ut.user_id = %s
                """, (user_id,))
        
        rows = cursor.fetchall()

        tokens = []

        for row in rows:
            tokens.append(UserToken(token_id=row[0],api_token=row[1], worksnaps_user_id=row[2], rate=row[3], currency=row[4], user_id=row[5]))

        return tokens
    except Exception as e:
        logging.error(f"Error getting token: {e}")
        return None
    finally:
        cursor.close()
        connection.close()

def get_all_tokens() -> List[UserToken]:
    try:
        connection = psycopg2.connect(config.database.connection_string)
        cursor = connection.cursor()

        cursor.execute("""
                    SELECT t.token_id, t.api_token, ut.worksnaps_user_id, t.rate, t.currency, ut.user_id
                    FROM api_tokens t
                    JOIN user_tokens ut ON t.token_id = ut.token_id
                """)
        
        rows = cursor.fetchall()

        tokens = []

        for row in rows:
            tokens.append(UserToken(token_id=row[0],api_token=row[1], worksnaps_user_id=row[2], rate=row[3], currency=row[4], user_id=row[5]))

        return tokens
    except Exception as e:
        logging.error(f"Error getting token: {e}")
        return None
    finally:
        cursor.close()
        connection.close()

def is_token_exists(user_id: int) -> bool:
    try:
        connection = psycopg2.connect(config.database.connection_string)
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM user_tokens WHERE user_id = %s", (user_id,))
        rows = cursor.fetchall()

        return len(rows) > 0
    except Exception as e:
        logging.error(f"Error checking if token exists: {e}")
        return False

def add_rate(token_id: int, rate: float, currency: str) -> None:
    try:
        connection = psycopg2.connect(config.database.connection_string)

        cursor = connection.cursor()
        cursor.execute("""
                    UPDATE api_tokens
                    SET rate = %s, currency = %s
                    WHERE token_id = %s
                """, (rate, currency, token_id))

        connection.commit()
    except Exception as e:
        logging.error(f"Error adding rate: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

def delete_token(token_id: int) -> None:
    try:
        connection = psycopg2.connect(config.database.connection_string)
        cursor = connection.cursor()
        
        clear_cache(token_id, cursor)

        cursor.execute("""
                    DELETE FROM api_tokens
                    WHERE token_id = %s
                """, (token_id,))

        connection.commit()

    except Exception as e:
        logging.error(f"Error deleting token: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

def clear_cache(token_id: int, cursor) -> None:
    cursor.execute("""
                        SELECT at.api_token, ut.worksnaps_user_id
                        FROM user_tokens ut
                        JOIN api_tokens at ON ut.token_id = at.token_id
                        WHERE at.token_id = %s
                    """, (token_id,))

    token_data = cursor.fetchone()

    api_token = token_data[0]
    worksnaps_user_id = token_data[1]
    
    redis.delete(f"user:{api_token}")
    redis.delete(f"summary:{worksnaps_user_id}")