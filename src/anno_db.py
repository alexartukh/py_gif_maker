import os
import secrets

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# project root : one level above the "src" folder
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class AnnoDB:
    def __init__(self, session_ttl_seconds=3600):
        # read DB access settings from .env in the project root
        load_dotenv(os.path.join(PROJECT_DIR, ".env"))

        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "3306")
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD", "")
        database = os.getenv("DB_NAME")

        if not user or not database:
            raise RuntimeError("DB_USER and DB_NAME must be set in .env (see .env.example)")

        self.connection = mysql.connector.connect(
            host=host,
            port=int(port),
            user=user,
            password=password,
            database=database
        )

        # lifetime of admin sessions (table: admin_sessions)
        self.session_ttl = session_ttl_seconds

    def get_user_by_login_and_password(self, login, password):
        try:
            cursor = self.connection.cursor(dictionary=True, buffered=True)
            cursor.execute(
                "SELECT * FROM anno_users "
                "WHERE username = %s AND password = %s AND status = 'active' ",
                (login, password, )
            )
            user = cursor.fetchone()
            return user
        except Error as e:
            print("!! MySQL error !! " + str(e))
            return None
        finally:
            cursor.close()

    def get_user_by_id(self, uid):
        try:
            cursor = self.connection.cursor(dictionary=True, buffered=True)
            cursor.execute(
                "SELECT * FROM anno_users "
                "WHERE id = %s AND status = 'active' ",
                (uid, )
            )
            user = cursor.fetchone()
            return user
        except Error as e:
            print("!! MySQL error !! " + str(e))
            return None
        finally:
            cursor.close()

    def create_task_record(self, user_id, template, md5_hash, gif_filename):
        try:
            cursor = self.connection.cursor(dictionary=True, buffered=True)
            cursor.execute(
                "REPLACE INTO anno_tasks (user_id, template, md5_hash, gif_filename) "
                "VALUES (%s, %s, %s, %s) ",
                (user_id, template, md5_hash, gif_filename)
            )
            self.connection.commit()
        except Error as e:
            print("!! MySQL error !! " + str(e))
            return None
        finally:
            cursor.close()

    def search_for_task(self, user_id, template, md5_hash):
        try:
            cursor = self.connection.cursor(dictionary=True, buffered=True)
            cursor.execute(
                "SELECT gif_filename FROM anno_tasks "
                "WHERE user_id = %s AND template = %s AND md5_hash = %s ",
                (user_id, template, md5_hash)
            )
            task = cursor.fetchone()
            if not task:
                return None
            
            return task.get("gif_filename")
        except Error as e:
            print("!! MySQL error !! " + str(e))
            return None
        finally:
            cursor.close()

    def clear_cache_for_user(self, user_id):
        try:
            cursor = self.connection.cursor(dictionary=True, buffered=True)
            cursor.execute(
                "DELETE FROM anno_tasks "
                "WHERE user_id = %s ",
                (user_id, )
            )
            self.connection.commit()
        except Error as e:
            print("!! MySQL error !! " + str(e))
            return None
        finally:
            cursor.close()

    def get_task_count_for_user(self, user_id):
        try:
            cursor = self.connection.cursor(dictionary=True, buffered=True)
            cursor.execute(
                "SELECT COUNT(*) AS ctr "
                "FROM anno_tasks "
                "WHERE user_id = %s ",
                (user_id, )
            )
            row = cursor.fetchone()
            return row["ctr"]
        except Error as e:
            print("!! MySQL error !! " + str(e))
            return None
        finally:
            cursor.close()

    def save_settings(self, user_id, template, settings):
        try:
            cursor = self.connection.cursor(dictionary=True, buffered=True)
            cursor.execute(
                "REPLACE INTO anno_settings (user_id, template, settings) "
                "VALUES (%s, %s, %s) ",
                (user_id, template, settings)
            )
            self.connection.commit()
        except Error as e:
            print("!! MySQL error !! " + str(e))
            return None
        finally:
            cursor.close()

    def get_settings(self, user_id):
        try:
            cursor = self.connection.cursor(dictionary=True, buffered=True)
            cursor.execute(
                "SELECT template, settings FROM anno_settings "
                "WHERE user_id = %s ",
                (user_id, )
            )
            rows = cursor.fetchall()
            result = {}
            for row in rows:
                template = row["template"]
                settings = row["settings"]
                result[template] = settings
            return result
        except Error as e:
            print("!! MySQL error !! " + str(e))
            return None
        finally:
            cursor.close()

# ---------------------------------------------------------------------
# admin sessions (table: admin_sessions)

    def create_session(self, user_id):
        session_id = secrets.token_urlsafe(32)
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO admin_sessions (id, user_id, expires_at) "
                "VALUES (%s, %s, DATE_ADD(NOW(), INTERVAL %s SECOND))",
                (session_id, user_id, self.session_ttl)
            )
            self.connection.commit()
        except Error:
            return None
        finally:
            cursor.close()

        return session_id

    def get_session(self, session_id):
        try:
            cursor = self.connection.cursor(dictionary=True, buffered=True)
            cursor.execute(
                "SELECT user_id FROM admin_sessions "
                "WHERE id = %s AND expires_at > NOW() "
                "LIMIT 1",
                (session_id,)
            )
            row = cursor.fetchone()
        except Error:
            return None
        finally:
            cursor.close()

        if row is None:
            return None  # нет такой сессии или уже истекла

        # скользящий TTL: продлеваем срок жизни при активности
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "UPDATE admin_sessions SET expires_at = DATE_ADD(NOW(), INTERVAL %s SECOND) "
                "WHERE id = %s",
                (self.session_ttl, session_id)
            )
            self.connection.commit()
        except Error:
            pass
        finally:
            cursor.close()

        return row["user_id"]

    def destroy_session(self, session_id):
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM admin_sessions WHERE id = %s", (session_id,))
            self.connection.commit()
        except Error:
            pass
        finally:
            cursor.close()

    def cleanup_expired_sessions(self):
        """Optional housekeeping: purge rows past their TTL instead of relying
        purely on lazy expiry checks in get_session(). Safe to call
        periodically (e.g. on a schedule) or just skip entirely."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM admin_sessions WHERE expires_at <= NOW()")
            self.connection.commit()
        except Error:
            pass
        finally:
            cursor.close()
