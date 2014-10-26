#! /Users/Antoine/.virtualenvs/RpiSpeaker/bin/python

import sys
import signal
import os

from gevent.wsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

from pimusic.web_interface import pimusic_server
from pimusic.player import MPlayerControl
from conf import CONF

player = MPlayerControl(CONF)
app = pimusic_server(CONF, player)

def handler(signum, frame):
    player.kill()
    sys.exit()
    return

signal.signal(signal.SIGTERM, handler)
player.start()
app.debug = True
http_server = WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
http_server.serve_forever()
