import secrets
from mysql.connector import Error


class AdminSession:
    def __init__(self, mysql_connection, ttl_seconds=3600):
        self.connection = mysql_connection
        self.ttl = ttl_seconds

    def create_session(self, user_id):
        session_id = secrets.token_urlsafe(32)
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO admin_sessions (id, user_id, expires_at) "
                "VALUES (%s, %s, DATE_ADD(NOW(), INTERVAL %s SECOND))",
                (session_id, user_id, self.ttl)
            )
            self.connection.commit()
        except Error:
            return None
        finally:
            cursor.close()

        return session_id

    def get_session(self, session_id):
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT user_id FROM admin_sessions "
                "WHERE id = %s AND expires_at > NOW()",
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
                (self.ttl, session_id)
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

    def cleanup_expired(self):
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
