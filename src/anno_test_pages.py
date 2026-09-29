import time


# pages for manual testing of the web service : /testing_post and /testing_get
# it is a mixin for the Anno class, so "self" is the Anno object
# and self.mysql, self.render_template are available here
#
# a tesing page will be displayed in any case,
# but if a user has a logged in session, his login and password will be used
class AnnoTestPages:
    def on_testing_post(self, request):
        session_id = request.cookies.get("session_id")
        user_id = self.mysql.get_session(session_id) if session_id else None

        # this is a default service user for testing
        login = "test"
        password = "123"

        if user_id is not None:
            user = self.mysql.get_user_by_id(user_id)
            login = user["username"]
            password = user["password"]
        
        return self.render_template(
            "testing_post.html",
            timestamp=time.time(),
            test_login=login,
            test_password=password,
        )

    def on_testing_get(self, request):
        session_id = request.cookies.get("session_id")
        user_id = self.mysql.get_session(session_id) if session_id else None

        # this is a default service user for testing
        login = "test"
        password = "123"

        if user_id is not None:
            user = self.mysql.get_user_by_id(user_id)
            login = user["username"]
            password = user["password"]
            
        return self.render_template(
            "testing_get.html",
            timestamp=time.time(),
            test_login=login,
            test_password=password,
        )
