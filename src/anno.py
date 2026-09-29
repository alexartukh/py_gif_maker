import os
import time
import threading

from jinja2 import Environment
from jinja2 import FileSystemLoader

from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import NotFound
from werkzeug.middleware.shared_data import SharedDataMiddleware
from werkzeug.routing import Map
from werkzeug.routing import Rule
from werkzeug.wrappers import Request
from werkzeug.wrappers import Response

# other modules
import anno_db
import anno_admin_session
import anno_test_pages
import anno_admin_pages
import anno_web_service

TTL_ADMIN_SESSION = 3600
ADMIN_SESSION_CLEANUP_INTERVAL_SECONDS = 300

# project root : one level above the "src" folder
# get dir from dir
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run_periodic_admin_session_cleanup(admin_sessions, interval_seconds):
    while True:
        time.sleep(interval_seconds)
        admin_sessions.cleanup_expired()

class Anno(
    anno_test_pages.AnnoTestPages,
    anno_admin_pages.AnnoAdminPages,
    anno_web_service.AnnoWebService,
):
    def __init__(self):

        # mysql access
        self.mysql = anno_db.AnnoDB()

        # admin sessions (MySQL-backed, table: admin_sessions)
        self.admin_sessions = anno_admin_session.AdminSession(
            self.mysql.connection, ttl_seconds=TTL_ADMIN_SESSION
        )

        # background thread that purges expired sessions periodically;
        # always on, including under the dev reloader
        self.cleanup_thread = threading.Thread(
            target=run_periodic_admin_session_cleanup,
            args=(self.admin_sessions, ADMIN_SESSION_CLEANUP_INTERVAL_SECONDS),
            daemon=True
        )
        self.cleanup_thread.start()

        # template toolkit 
        self.jinja_env = Environment(
            loader=FileSystemLoader(os.path.join(PROJECT_DIR, "templates")),
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
                Rule("/admin_change_settings", endpoint="admin_change_settings"),

                # Web Service
                Rule("/g", endpoint="generate"),
                Rule("/login", endpoint="login"),
            ]
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


def create_app():
    app = Anno()
    app.wsgi_app = SharedDataMiddleware(
        app.wsgi_app,
        {
            "/static": os.path.join(PROJECT_DIR, "static"),
        }
    )
    return app


if __name__ == "__main__":
    from werkzeug.serving import run_simple
    app = create_app()
    # run_simple("127.0.0.1", 5555, app, use_debugger=True, use_reloader=True)
    run_simple("0.0.0.0", 5555, app, use_debugger=True, use_reloader=True)

