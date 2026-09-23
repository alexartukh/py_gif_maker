import mysql.connector
from mysql.connector import Error

class AnnoDB:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="anno"
        )

    def get_user_by_login_and_password(self, login, password):
        try:
            cursor = self.connection.cursor(dictionary=True)
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
            cursor = self.connection.cursor(dictionary=True)
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
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO anno_tasks (user_id, template, md5_hash, gif_filename) "
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
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT gif_filename FROM anno_tasks "
                "WHERE user_id = %s AND template = %s AND md5_hash = %s "
                "LIMIT 1 ",
                (user_id, template, md5_hash)
            )
            task = cursor.fetchone()
            return task
        except Error as e:
            print("!! MySQL error !! " + str(e))
            return None
        finally:
            cursor.close()

    def clear_cache_for_user(self, user_id):
        try:
            cursor = self.connection.cursor()
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
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT COUNT(id) AS ctr "
                "FROM anno_tasks "
                "WHERE user_id = %s ",
                (user_id, )
            )
            row = cursor.fetchone()
            return row
        except Error as e:
            print("!! MySQL error !! " + str(e))
            return None
        finally:
            cursor.close()
