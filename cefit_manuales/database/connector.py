import mysql.connector
from mysql.connector import Error
import logging
class DatabaseConnector:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            logging.info("Conexión a la base de datos establecida")
        except Error as e:
            logging.error(f"Error al conectar a la base de datos: {e}")
            raise

    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logging.info("Conexión a la base de datos cerrada")

    def execute_query(self, query, params=None):
        try:
            with self.connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, params)
                if cursor.description:
                    result = cursor.fetchall()
                else:
                    result = cursor.rowcount
                self.connection.commit()
                return result
        except mysql.connector.Error as e:
            logging.error(f"Error al ejecutar la consulta: {e}")
            self.connection.rollback()
            return

    def call_procedure(self, proc_name, params=None):
        try:
            with self.connection.cursor(dictionary=True) as cursor:
                cursor.callproc(proc_name, params)
                self.connection.commit()
                results = []
                for result in cursor.stored_results():
                    results.extend(result.fetchall())
                return results
        except Error as e:
            logging.error(f"Error al llamar al procedimiento almacenado: {e}")
            self.connection.rollback()
            return None