import mysql.connector
from datetime import datetime
from typing import List, Optional, Dict


class DatabaseService:
    def __init__(self, host: str, user: str, password: str, database: str, port: str):
        self.config = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database,
            "port": port,
        }

    def _get_connection(self):
        return mysql.connector.connect(**self.config)

    def log_conversion(
        self,
        ip: str,
        source_format: str,
        target_format: str,
        file_size: float,
        processing_time: float,
        status: str,
        error_message: Optional[str] = None,
    ) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO conversion_logs 
                (ip, source_format, target_format, file_size, processing_time, status, error_message)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    ip,
                    source_format,
                    target_format,
                    file_size,
                    processing_time,
                    status,
                    error_message,
                ),
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    def get_conversion_history(self, limit: int = 100) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT * FROM conversion_logs 
                ORDER BY created_at DESC 
                LIMIT %s
            """,
                (limit,),
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
