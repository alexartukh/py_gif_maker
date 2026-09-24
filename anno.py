import os
import json
import time
import threading
import hashlib
import shutil

from jinja2 import Environment
from jinja2 import FileSystemLoader

from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import NotFound
from werkzeug.middleware.shared_data import SharedDataMiddleware
from werkzeug.routing import Map
from werkzeug.routing import Rule
from werkzeug.wrappers import Request
from werkzeug.wrappers import Response
from werkzeug.utils import redirect

# other modules
import anno_db
import anno_auth
import anno_admin_session

# generators
import gen_life_test
import gen_life_my
import gen_f

APP_VERSION = "0.0.1"
TTL_ADMIN_SESSION = 3600
ADMIN_SESSION_CLEANUP_INTERVAL_SECONDS = 300

# def run_periodic_admin_session_cleanup(admin_sessions, interval_seconds):
#     while True:
#         time.sleep(interval_seconds)
#         admin_sessions.cleanup_expired()


class Anno:
    def __init__(self, config):

        # mysql access
        self.mysql = anno_db.AnnoDB()

        # admin sessions (MySQL-backed, table: admin_sessions)
        self.admin_sessions = anno_admin_session.AdminSession(
            self.mysql.connection, ttl_seconds=TTL_ADMIN_SESSION
        )

        # background thread that purges expired sessions periodically;
        # always on, including under the dev reloader
        # self.cleanup_thread = threading.Thread(
        #     target=run_periodic_admin_session_cleanup,
        #     args=(self.admin_sessions, ADMIN_SESSION_CLEANUP_INTERVAL_SECONDS),
        #     daemon=True
        # )
        # self.cleanup_thread.start()

        # template toolkit 
        self.jinja_env = Environment(
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")),
            autoescape=True
        )

        self.url_map = Map(
            [
                # Pages for testing
                Rule("/testing_post", endpoint="testing_post"), # show tester for POST requests
                Rule("/testing_get", endpoint="testing_get"), # show tester for GET requests

                # Admin
                Rule("/", endpoint="admin_login"),
                Rule("/admin", endpoint="admin_login"),
                Rule("/admin_submit_password", endpoint="admin_submit_password"),
                Rule("/admin_logout", endpoint="admin_logout"),
                Rule("/admin_clear_cache", endpoint="admin_clear_cache"),
                Rule("/admin_main", endpoint="admin_main"),

                # Web Service
                Rule("/g", endpoint="generate"),
                Rule("/login", endpoint="login"),
            ]
        )

# ---------------------------------------------------------------------

    def on_login(self, request):
        if request.method != "POST":
            return Response(
                response=json.dumps({"error": 1, "message": "POST required"}),
                mimetype="application/json",
                status=405
            )

        data = request.json
        login = data.get("login") or None
        password = data.get("password") or None

        if not login or not password:
            return Response(
                response=json.dumps({"error": 1, "message": "no login or password"}),
                mimetype="application/json"
            )

        u = self.mysql.get_user_by_login_and_password(login, password)
        if not u:
            return Response(
                response=json.dumps({"error": 1, "message": "wrong login or password"}),
                mimetype="application/json"
            )

        token = anno_auth.make_token(u["id"])
        return Response(
            response=json.dumps({"error": 0, "token": token}),
            mimetype="application/json"
        )

# ---------------------------------------------------------------------

    def on_generate(self, request):

        # 2 request me
        data = None
        if request.method == "GET":
            # in = normal args, out = GIF file
            json_response = False
            data = request.args  
        elif request.method == "POST":
            # in = JSON, out = JSON
            json_response = True
            data = request.json
        else:
            return Response(
                response=json.dumps({"error": 1, "message": "unsupported request method", "value": request.method}),
                mimetype="application/json"
            )

        t = data.get("t") or "" # empty seed is correct seed as well 
        token = data.get("token") or None

        # get template ID
        template = None
        try:
            template = int(data.get("template"))
        except (TypeError, ValueError):
            return Response(
                response=json.dumps({"error": 1, "message": "template must be an integer", "value": template}),
                mimetype="application/json"
            )

        u = anno_auth.verify_token(token);
        if not u:   
            return Response(
                response=json.dumps({ "error": 1, "message": "wrong auth token"}),
                mimetype="application/json"
            )

        result = None
        md5_value = hashlib.md5(t.encode('utf-8')).digest()
        md5_value_hex = md5_value.hex()

        # create a generator in any case
        generator = None
        if template >= 1 and template <= 5:
            generator = gen_f.FGenerator(template)
        elif template == 100:
            generator = gen_life_test.LifeSimpleGenerator()        
        elif template == 200:
            generator = gen_life_my.LifeMyGenerator()
        else:
            return Response(
                response=json.dumps({ "error": 1, "message": "unknown template value " + str(template)}),
                mimetype="application/json"
            )

        # cache in action or run a new task
        task = self.mysql.search_for_task(u, template, md5_value_hex)
        # TODO
        # remove this later    
        task = None # disable cache for testing

        if task is None:
            print('Run a new task for a template ' + str(template))    
            result = generator.make_gif(md5_value, u)

            # save task record in the DB
            self.mysql.create_task_record(u, template, md5_value_hex, result)
        else:
            # cache in action
            result = task
            print('Cache in action : ' + result)

        # POST result : send JSON with a URL inside as a response
        if json_response:  
            result_data = {
                "result": "http://" + request.host + result,
                "t": t,
                "template": template,
                "description": generator.get_description(),
                "md5_value": md5_value_hex,
            }
            return Response(response=json.dumps(result_data), mimetype="application/json")

        # GET result : send a file as a response
        with open('.' + result, "rb") as f:
            gif_data = f.read()
        return Response(
            response=gif_data,
            mimetype="image/gif"
        )

# ---------------------------------------------------------------------

    def on_admin_submit_password(self, request):
        if request.method != "POST":
            return Response(
                response=json.dumps({"error": 1, "message": "POST required"}),
                mimetype="application/json",
                status=405
            )

        data = request.form
        login = data.get("username") or None
        password = data.get("password") or None

        u = self.mysql.get_user_by_login_and_password(login, password)
        if u is None:
            return self.render_template("admin_login.html", version=APP_VERSION, timestamp=time.time(), message="Wrong login or password")

        session_id = self.admin_sessions.create_session(u['id'])
        if session_id is None:
            return self.render_template("admin_login.html", version=APP_VERSION, timestamp=time.time(), message="Unable to create a session record")

        response = redirect("/admin_main")
        response.set_cookie(
            "session_id",
            session_id,
            max_age=TTL_ADMIN_SESSION,
            httponly=True,
            samesite="Strict"
        )
        return response

    def on_admin_logout(self, request):
        session_id = request.cookies.get("session_id")
        self.admin_sessions.destroy_session(session_id)
        return redirect("/admin")

    def on_admin_login(self, request):
        return self.render_template("admin_login.html", version=APP_VERSION, timestamp=time.time(), message="Enter login and password")

    def on_admin_clear_cache(self, request):
        # check session first
        session_id = request.cookies.get("session_id")
        user_id = self.admin_sessions.get_session(session_id) if session_id else None

        if user_id is None:
            return redirect("/admin")

        self.mysql.clear_cache_for_user(user_id)
        shutil.rmtree(
            os.path.join(os.path.dirname(__file__), "static", str(user_id)),
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

        return self.render_template(
            "admin_main.html",
            version=APP_VERSION,
            timestamp=time.time(),
            welcome_message="Welcome " + user["username"] + " (" + user["email"] + ")",
            show_logout_link=True,
            tasks_for_this_user=task_count,
        )

# ---------------------------------------------------------------------
    # a tesing page will be displayed in any case, 
    # but if a user has a logged in session, his login and password will be used 

    def on_testing_post(self, request):
        session_id = request.cookies.get("session_id")
        user_id = self.admin_sessions.get_session(session_id) if session_id else None

        # this is a default service user for testing
        login = "test"
        password = "123"

        if user_id is not None:
            user = self.mysql.get_user_by_id(user_id)
            login = user["username"]
            password = user["password"]
        
        return self.render_template(
            "testing_post.html",
            version=APP_VERSION,
            timestamp=time.time(),
            test_login=login,
            test_password=password,
        )

    def on_testing_get(self, request):
        session_id = request.cookies.get("session_id")
        user_id = self.admin_sessions.get_session(session_id) if session_id else None

        # this is a default service user for testing
        login = "test"
        password = "123"

        if user_id is not None:
            user = self.mysql.get_user_by_id(user_id)
            login = user["username"]
            password = user["password"]
            
        return self.render_template(
            "testing_get.html",
            version=APP_VERSION,
            timestamp=time.time(),
            test_login=login,
            test_password=password,
        )

# ---------------------------------------------------------------------

    def error_404(self):
        response = self.render_template("404.html") 
        response.status_code = 404
        return response

    def render_template(self, template_name, **context):
        t = self.jinja_env.get_template(template_name)
        return Response(t.render(context), mimetype="text/html")

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            return getattr(self, f"on_{endpoint}")(request, **values)
        except NotFound:
            return self.error_404()
        except HTTPException as e:
            return e

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)


def create_app(with_static=True):
    app = Anno({})
    if with_static:
        app.wsgi_app = SharedDataMiddleware(
            app.wsgi_app,
            {
                "/static": os.path.join(os.path.dirname(__file__), "static"),
            }
        )
    return app


if __name__ == "__main__":
    from werkzeug.serving import run_simple
    app = create_app()
    # run_simple("127.0.0.1", 5555, app, use_debugger=True, use_reloader=True)
    run_simple("0.0.0.0", 5555, app, use_debugger=True, use_reloader=True)

