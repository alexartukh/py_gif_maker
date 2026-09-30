import os
import json
import hashlib

from werkzeug.wrappers import Response

import anno_auth

# generators
import gen_life_test
import gen_life_my
import gen_f
import gen_ant

# project root : one level above the "src" folder
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# web service endpoints : /login and /g
# it is a mixin for the Anno class, so "self" is the Anno object
# and self.mysql is available here
class AnnoWebService:
    
    # a new generator should be added here
    def _create_generator(self, template, settings):
        generator = None
        if template >= 1 and template <= 5:
            generator = gen_f.FGenerator(template, settings)
        elif template == 100:
            generator = gen_life_test.LifeSimpleGenerator(settings)        
        elif template == 200:
            generator = gen_life_my.LifeMyGenerator(settings)
        elif template == 300:
            generator = gen_ant.AntGenerator(settings)
        return generator

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
        ignore_cache = data.get("ignore_cache") or None

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

        all_db_settings = self.mysql.get_settings(u)

        if all_db_settings is None:
            all_db_settings = {}
        settings = all_db_settings.get(template) or ""

        generator = self._create_generator(template, settings)
        if generator is None:
            return Response(
                response=json.dumps({ "error": 1, "message": "unknown template value " + str(template)}),
                mimetype="application/json"
            )

        # cache in action or run a new task
        if ignore_cache is None:
            task = self.mysql.search_for_task(u, template, md5_value_hex)
        else:
            task = None

        if task is None:
            result = generator.make_gif(md5_value, u)
            self.mysql.create_task_record(u, template, md5_value_hex, result)

            print('Run a new task for a template ' + str(template))    
            cache_in_action = False
        else:
            result = task
            
            print('Cache in action : ' + result)
            cache_in_action = True

        # POST result : send JSON with a URL inside as a response
        if json_response:  
            result_data = {
                "result": "http://" + request.host + result,
                "t": t,
                "template": template,
                "description": generator.get_description(),
                "md5_value": md5_value_hex,
                "cache_in_action": cache_in_action, 
            }
            return Response(response=json.dumps(result_data), mimetype="application/json")

        # GET result : send a file as a response
        with open(PROJECT_DIR + result, "rb") as f:
            gif_data = f.read()
        return Response(
            response=gif_data,
            mimetype="image/gif"
        )
