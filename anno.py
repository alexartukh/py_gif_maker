import os
import json
import time

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

app_version = "0.0.1"

class Anno:
    def __init__(self, config):

        # mysql access
        self.mysql = anno_db.AnnoDB()

        # admin sessions (MySQL-backed, table: admin_sessions)
        self.admin_sessions = anno_admin_session.AdminSession(
            self.mysql.connection, ttl_seconds=3600
        )

        # template toolkit 
        self.jinja_env = Environment(
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")),
            autoescape=True
        )

        self.url_map = Map(
            [
                # HTML Pages
                Rule("/testing_post", endpoint="testing_post"), # show tester for POST requests
                Rule("/testing_get", endpoint="testing_get"), # show tester for GET requests
                Rule("/", endpoint="admin"),
                Rule("/admin", endpoint="admin"),
                Rule("/admin_submit_password", endpoint="admin_submit_password"),
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

        u = self.mysql.get_user(login, password)
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

        t = data.get("t") or "NO_SEED" 
        token = data.get("token") or None

        result = None
        template = None

        # get template ID
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

        # create a generator
        generator = None
        if template >= 1 and template <= 5:
            generator = gen_f.FGenerator(template)
        elif template == 100:
            generator = gen_life_test.LifeSimpleGenerator()        
        elif template == 200:
            generator = gen_life_my.LifeMyGenerator()
        else:
            return Response(
                response=json.dumps({ "error": 1, "message": "unknown template value " + template}),
                mimetype="application/json"
            )

        # use generator
        if generator is not None:    
            result = generator.make_gif(t, u)

        # POST result : send JSON with a URL inside as a response
        if json_response:  
            result_data = {
                "result": "http://" + request.host + result,
                "t": t,
                "template": template,
                "description": generator.get_description(),
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

        u = self.mysql.get_user(login, password)
        if u is None:
            return self.render_template("admin_login.html", version=app_version, timestamp=time.time(), message="Wrong login or password")

        session_id = self.admin_sessions.create_session(u['id'])
        if session_id is None:
            return self.render_template("admin_login.html", version=app_version, timestamp=time.time(), message="Login failed, try again")

        response = redirect("/admin_main")
        response.set_cookie(
            "session_id",
            session_id,
            max_age=3600,
            httponly=True,
            samesite="Lax"
        )
        return response

    def on_admin(self, request):
        return self.render_template("admin_login.html", version=app_version, timestamp=time.time(), message="Enter login and password")

    def on_admin_main(self, request):

        # check session first
        session_id = request.cookies.get("session_id")
        user_id = self.admin_sessions.get_session(session_id) if session_id else None

        if user_id is None:
            return redirect("/admin")

        return self.render_template("admin_main.html", version=app_version, timestamp=time.time())


    def on_testing_post(self, request):
        return self.render_template("testing_post.html", version=app_version, timestamp=time.time())

    def on_testing_get(self, request):
        return self.render_template("testing_get.html", version=app_version, timestamp=time.time())
    
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


def create_app(redis_host="localhost", redis_port=6379, with_static=True):
    app = Anno({"redis_host": redis_host, "redis_port": redis_port})
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

