from bin.handler.base import BaseHandler


class Ping(BaseHandler):
    def GET(self):
        return "ok"
