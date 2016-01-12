import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
from hottubapi import HotTubAPI
from datetime import timedelta
import json

class FancySocketHandler(tornado.websocket.WebSocketHandler):
    def initialize(self):
        self.callbacks = {} # use this for bind
        
    def bind(self, method_name, callback):
        if not method_name in self.callbacks:
            self.callbacks[method_name] = []
        self.callbacks[method_name].append(callback)
        
    # data is a dict
    def send(self, method_name, data):
        j_msg = dict(event=method_name, data=data)
        message = json.dumps(j_msg)
        self.write_message(message)
        
    def dispatch(self, event_name, **kwargs):
        if not event_name in self.callbacks:
            return
        for callback in self.callbacks[event_name]:
            callback(**kwargs)
        
    def on_message(self, message):
        j_msg = json.loads(message)
        if 'event' in j_msg:
            if not 'data' in j_msg or not type(j_msg['data']) is dict:
                j_msg['data'] = dict()
            self.dispatch(j_msg['event'], **j_msg['data'])
        
    def on_close(self):
        self.dispatch('close', **dict())

class WebSocketHandler(FancySocketHandler):
    def initialize(self, api):
        super(WebSocketHandler, self).initialize()
        self.api = api
        self.bind('close', self.close)
        
        # Bind the incoming events
        self.bind('pressLightButton', self.api.pressLightButton)
        self.bind('pressPumpButton', self.api.pressPumpButton)
        self.bind('pressTempUpButton', self.api.pressTempUpButton)
        self.bind('pressTempDownButton', self.api.pressTempDownButton)
        self.bind('refresh', self.api.doRefresh)
        # Bind the outgoing events
        self.api.registerClient(self, self.send)
        
    def open(self):
        print 'Connection opened'
        
    def close(self):
        print 'Connected closed'
        self.api.deregisterClient(self)

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html");
        
class TwilioHandler(tornado.web.RequestHandler):
    def initialize(self, api):
        super(TwilioHandler, self).initialize()
        self.api = api
    
    def get(self):
        # Get the message body
        body = self.get_argument('Body')
        if body.lower() == "temp":
            message = "The Current Temperature is %d" % self.api.getCurTemp()
        elif body.lower() == "setp" or body.lower() == "set point" or body.lower() == "setpoint":
            message = "The Current Set Point is %d" % self.api.getSetPoint()
        elif body.lower() == "heat":
            self.api.heatUp()
            message = "Hot Tub On! It will take %d minutes to heat from %d to %d" % (self.api.estimateDelay(), self.api.getCurTemp(), self.api.getSetPoint())
        elif body.lower() == "off" or body.lower() == "cool" or body.lower() == "cold":
            self.api.coolDown()
            message = "Hot Tub Set to %d" % (self.api.getSetPoint())
        else:
            message = "Options are 'TEMP', 'SET POINT', 'HEAT' or 'COOL'"
        self.set_header('Content-type', 'application/xml')
        self.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<Response>\n   <Sms>%s</Sms>\n</Response>" % message)

def set_ping(ioloop, timeout):
    ioloop.add_timeout(timeout, lambda: set_ping(ioloop, timeout))
        
def main():
    try:
        # create an api for the webserver
        api = HotTubAPI();
        app = tornado.web.Application(
            handlers=[
                (r"/images/(.*)", tornado.web.StaticFileHandler, {"path":"./images"}),
                (r"/css/(.*)", tornado.web.StaticFileHandler, {"path":"./css"}),
                (r"/js/(.*)", tornado.web.StaticFileHandler, {"path":"./js"}),
                (r"/*", IndexHandler),
                (r"/twilio.api", TwilioHandler, dict(api=api)),
                (r"/ws", WebSocketHandler, dict(api=api))
            ]
        )
        server = tornado.httpserver.HTTPServer(app)
        port = 9999
        server.listen(port,address="0.0.0.0")
        print "Tornado listening on port: %s" % port

        ioloop = tornado.ioloop.IOLoop.instance()
        set_ping(ioloop, timedelta(seconds=2))
        ioloop.start()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        api.close()
        server.stop();

if __name__ == '__main__':
    main()

