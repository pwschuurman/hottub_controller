import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
from hottubapi import HotTubAPI
from datetime import timedelta
import json
from rx.scheduler.eventloop import AsyncIOScheduler
import asyncio

ioloop = tornado.ioloop.IOLoop.current()

class FancySocketHandler(tornado.websocket.WebSocketHandler):
    def initialize(self):
        self.callbacks = {} # use this for bind

    def bind(self, method_name, callback):
        """Binds a callback to method_name.

        Args:
          method_nane: The javascript method_name
          callback: The function to pass through
        """
        if not method_name in self.callbacks:
            self.callbacks[method_name] = []
        self.callbacks[method_name].append(callback)

    def send(self, method_name, data):
        """Sends a messge to the client.

        Args:
          method_name: The javascript method name
          data: A dictionary of data to pass to the client
        """

        j_msg = dict(event=method_name, data=data)
        message = json.dumps(j_msg)

        ioloop.add_callback(lambda: self.write_message(message))
        
    def _dispatch(self, event_name, **kwargs):
        if not event_name in self.callbacks:
            return
        for callback in self.callbacks[event_name]:
            callback(**kwargs)
        
    def on_message(self, message):
        """Callback for a message received from a WS client.

        Args:
          message: A JSON message. If not formatted appropriately, it is
              discarded.
        """
        j_msg = json.loads(message)
        if 'event' in j_msg:
            if not 'data' in j_msg or not type(j_msg['data']) is dict:
                j_msg['data'] = dict()
            self._dispatch(j_msg['event'], **j_msg['data'])
        
    def on_close(self):
        self._dispatch('close', **dict())

class WebSocketHandler(FancySocketHandler):
    def initialize(self, api):
        super(WebSocketHandler, self).initialize()
        self.api = api
        self.bind('close', self.close)
        
        # Bind the incoming events
        self.bind('pressLightButton', self.api.press_light_button)
        self.bind('pressPumpButton', self.api.press_pump_button)
        self.bind('pressTempUpButton', self.api.press_temp_up_button)
        self.bind('pressTempDownButton', self.api.press_temp_down_button)

    def send_transmission(self, transmission):
        print("Updating leds")
        self.send('updateLeds', transmission._asdict())

    def open(self):
        print('Connection opened')
        loop = asyncio.get_event_loop()
        aio_scheduler = AsyncIOScheduler(loop=loop)
        self.api.transmissions().subscribe(self.send_transmission, scheduler=aio_scheduler)
        
    def close(self):
        print('Connected closed')

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")
        
class HeatHandler(tornado.web.RequestHandler):
    def initialize(self, api):
        super(HeatHandler, self).initialize()
        self.api = api
    
    def post(self):
        self.api.heat_up()
        self.write("OK")

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
                (r"/ws", WebSocketHandler, dict(api=api)),
                (r"/hottubapi/heat", HeatHandler, dict(api=api))
            ]
        )
        server = tornado.httpserver.HTTPServer(app)
        port = 9999
        server.listen(port,address="0.0.0.0")
        print("Tornado listening on port: %s" % port)

        set_ping(ioloop, timedelta(seconds=2))
        ioloop.start()
    except KeyboardInterrupt:
        print('^C received, shutting down server')
        #api.close()
        server.stop();

if __name__ == '__main__':
    main()
