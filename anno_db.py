import mysql.connector
from mysql.connector import Error
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DB.log")

class AnnoDB:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="anno"
        )

        if self.connection.is_connected():
            logger.info("DB connection OK")
        else:
            logger.error("DB connection error")

    def get_user_by_login_and_password(self, login, password):
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM anno_users WHERE username = %s AND password = %s AND status = 'active' ", (login, password, ))
            user = cursor.fetchone()
            return user
        except Error as err:
            logger.error("DB Error")
        finally:
            cursor.close()

        return None

    def get_user_by_id(self, uid):
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM anno_users WHERE id = %s AND status = 'active' ", (uid, ))
            user = cursor.fetchone()
            return user
        except Error as err:
            logger.error("DB Error")
        finally:
            cursor.close()

        return None
