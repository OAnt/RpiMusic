#! /Users/Antoine/.virtualenvs/RpiSpeaker/bin/python

from gevent.wsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

from pimusic.web_interface import pimusic_server
from pimusic.player import MPlayerControl
from conf import CONF

player = MPlayerControl(CONF)
player.start()
app = pimusic_server(CONF, player)
app.debug = True
http_server = WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
http_server.serve_forever()
