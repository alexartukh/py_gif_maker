from email import generator
import os
import json
import redis
import re
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

import anno_db
import anno_life_generator

class Anno:
    def __init__(self, config):

        # mysql access
        self.mysql = anno_db.AnnoDB()
        self.mysql.get_all_users()

        # cache service 
        self.redis = redis.Redis(
            config["redis_host"], config["redis_port"], decode_responses=True
        )

        # template toolkit 
        self.jinja_env = Environment(
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")),
            autoescape=True
        )

        # map
        self.url_map = Map(
            [
                # HTML Pages
                Rule("/", endpoint="home"),
                Rule("/admin", endpoint="admin"),
                Rule("/account", endpoint="account"),

                # Web Service
                Rule("/anno", endpoint="annotate"),
            ]
        )        

    def on_annotate(self, request):

        # check method
        if request.method != "POST":
            return Response(
                response=json.dumps({ "error": 1, "message": "wrong method"}),
                mimetype="application/json"
            )

        # get strings from 'application/json' data
        data = request.json; 
        t = data["t"]
        user = data["user"]
        template = data["template"]
        result = None

        # check form data
        if not t:
            return Response(
                response=json.dumps({ "error": 1, "message": "no text"}),
                mimetype="application/json"
            )
        if not user:   
            return Response(
                response=json.dumps({ "error": 1, "message": "no user"}),
                mimetype="application/json"
            )
        u = self.mysql.get_user_by_id(user)
        if not u:   
            return Response(
                response=json.dumps({ "error": 1, "message": "can't find a user by id"}),
                mimetype="application/json"
            )

        # create a pattern or a generator
        pattern = None
        generator = None
            
        if template == "1":
            pattern = re.compile(r'\b(\d+)\b')
        elif template == "2":
            pattern = re.compile(r'\b([A-Z]\w+)\b')
        elif template == "3":
            pattern = re.compile(r'\b(xxx|yyy|zzz)\b')
        elif template == "4":
            generator = anno_life_generator.LifeGenerator()            
        else:
            return Response(
                response=json.dumps({ "error": 1, "message": "unknown pattern " + template}),
                mimetype="application/json"
            )

        # main processing = use template or generator

        if pattern is not None:
            result = re.sub(pattern, r'<span style="color:cyan;">\1</span>', t)
            result_type = 1
        if generator is not None:    
            result = generator.make_gif(t)
            result = "http://" + request.host + result
            result_type = 2

        result_data = {
            "result": result,
            "result_type": result_type,
            "t": t,
            "user": user,
            "template": template,
        }

        return Response(response=json.dumps(result_data), mimetype="application/json")
                

    def on_home(self, request):
        return self.render_template("tester.html", version="0.1", timestamp=time.time())
    
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
    run_simple("127.0.0.1", 5555, app, use_debugger=True, use_reloader=True)

