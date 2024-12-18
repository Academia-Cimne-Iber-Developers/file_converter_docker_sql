import mysql.connector
from datetime import datetime
from typing import List, Optional, Dict


class DatabaseService:
    def __init__(self, host: str, user: str, password: str, database: str):
        self.config = {
            "host": host,
            "user": user,
            "password": password,
            "database": database,
        }
        self._create_database()
        self._create_table()

    def _get_connection(self):
        return mysql.connector.connect(**self.config)

    def _create_database(self):
        conn = mysql.connector.connect(
            host=self.config["host"],
            user=self.config["user"],
            password=self.config["password"],
        )

        cursor = conn.cursor()

        try:
            cursor.execute(
                "CREATE DATABASE IF NOT EXISTS {}".format(
                    self.config["database"]
                )
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    def _create_table(self):
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS conversion_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    ip VARCHAR(50) NOT NULL,
                    source_format VARCHAR(10) NOT NULL,
                    target_format VARCHAR(10) NOT NULL,
                    file_size FLOAT NOT NULL,
                    processing_time FLOAT NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    error_message VARCHAR(500),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()

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
