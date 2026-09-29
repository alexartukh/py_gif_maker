import os
import json
import time
import shutil

from werkzeug.wrappers import Response
from werkzeug.utils import redirect

# generators
import gen_base

# project root : one level above the "src" folder
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# admin pages : login, logout, main page, settings, cache cleanup
# it is a mixin for the Anno class, so "self" is the Anno object
# and self.mysql, self.admin_sessions, self.render_template are available here
class AnnoAdminPages:
    def on_admin_submit_password(self, request):
        if request.method != "POST":
            return Response(
                response=json.dumps({"error": 1, "message": "POST required"}),
                mimetype="application/json",
                status=405
            )

        data = request.form
        login = data.get("username")
        password = data.get("password")

        u = self.mysql.get_user_by_login_and_password(login, password)
        if u is None:
            return self.render_template(
                "admin_login.html",
                timestamp=time.time(),
                message="Wrong login or password"
            )

        session_id = self.admin_sessions.create_session(u['id'])
        if session_id is None:
            return self.render_template(
                "admin_login.html",
                timestamp=time.time(),
                message="Unable to create a session record"
            )

        response = redirect("/admin_main")
        response.set_cookie(
            "session_id",
            session_id,
            max_age=self.admin_sessions.ttl,
            httponly=True,
            samesite="Strict"
        )
        return response

    def on_admin_logout(self, request):
        session_id = request.cookies.get("session_id")
        self.admin_sessions.destroy_session(session_id)
        return redirect("/admin")

    def on_admin_login(self, request):
        return self.render_template("admin_login.html", timestamp=time.time(), message="Enter login and password")

    def on_admin_clear_cache(self, request):
        # check session first
        session_id = request.cookies.get("session_id")
        user_id = self.admin_sessions.get_session(session_id) if session_id else None

        if user_id is None:
            return redirect("/admin")

        self.mysql.clear_cache_for_user(user_id)
        shutil.rmtree(
            os.path.join(PROJECT_DIR, "static", str(user_id)),
            ignore_errors=True
        )
        
        return redirect("/admin_main")

    def on_admin_main(self, request):
        # check session first
        session_id = request.cookies.get("session_id")
        user_id = self.admin_sessions.get_session(session_id) if session_id else None

        if user_id is None:
            return redirect("/admin")

        user = self.mysql.get_user_by_id(user_id)
        task_count = self.mysql.get_task_count_for_user(user_id)
        all_settings = self.mysql.get_settings(user_id)

        if all_settings is None:
            all_settings = {}

        return self.render_template(
            "admin_main.html",
            timestamp=time.time(),
            welcome_message="Welcome " + user["username"] + " (" + user["email"] + ")",
            show_logout_link=True,
            tasks_for_this_user=task_count,
            hint_for_settings=gen_base.GifGeneratorBase.get_hint_for_settings(),
            all_settings=all_settings, # attach the whole dictionary
        )

    def on_admin_change_settings(self, request):
        # check session first
        session_id = request.cookies.get("session_id")
        user_id = self.admin_sessions.get_session(session_id) if session_id else None

        if user_id is None:
            return redirect("/admin")

        data = request.form
        template = data.get("template")
        settings = data.get("settings")

        self.mysql.save_settings(user_id, template, settings)

        return redirect("/admin_main")
