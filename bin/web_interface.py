import threading
import sqlite3
import flask
import json
import os

import gevent
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

import pimusic.player

DATABASE = '/Users/Antoine/Documents/Pn/projects/databases/RpiPlayer.db'
DEBUG = True
Player = pimusic.player.MPlayerControl()
Player.start()

app = flask.Flask(__name__)
app.config.from_object(__name__)

def local_db():
    mydata = threading.local()
    if not hasattr(mydata, 'Database'):
        mydata.Database = sqlite3.connect(DATABASE)
        mydata.Cursor = mydata.Database.cursor()
    return mydata

def sql_execute(cursor, statement, values):
    cursor.execute(statement, values)
    result = cursor.fetchall()
    return result

@app.route('/')
def index():
    index = open('templates/index.html')
    response = index.read()
    index.close()
    return flask.make_response(response)

@app.route('/api')
def api():
    if flask.request.environ.get('wsgi.websocket'):
        ws = flask.request.environ['wsgi.websocket']
        Player.listeners.append(ws)
        Player.get_metadata()
        while True:
            if ws.socket is None:
                return "Bye"
            gevent.sleep(1)
    return "OK"

@app.route('/player/pause', methods=['GET'])
def pause_unpause():
    Player.pause_unpause()
    return 'done'

@app.route('/player/next', methods=['GET'])
def next_song():
    Player.next_song()
    return 'done'

@app.route('/player/previous', methods=['GET'])
def previous_song():
    Player.previous_song()
    return 'done'

@app.route('/music')
def get_music():
    mydata = local_db()
    statement = 'SELECT id, name FROM artists'
    result = sql_execute(mydata.Cursor, statement, [])
    return json.dumps(result)

@app.route('/music/<artist>', methods = ['GET'])
def artist_req(artist):
    mydata = local_db()
    if flask.request.method == 'GET':
        statement = 'SELECT albums.id, album, albums.artist_id FROM albums, artists WHERE artists.id=? and albums.artist_id = artists.id'
        result = sql_execute(mydata.Cursor, statement, [artist])
        return json.dumps(result)

@app.route('/music/<artist>/<album>', methods = ['GET'])
def album_req(artist, album):
    mydata = local_db()
    if flask.request.method == 'GET':
        statement = 'SELECT Songs.id, Song, albums.id, albums.artist_id FROM Songs, albums WHERE Songs.album_id = albums.id and albums.id=? and albums.artist_id=?'
        result = sql_execute(mydata.Cursor, statement, [album, artist])
        return json.dumps(result)

@app.route('/music/<artist>/<album>/<song>', methods = ['POST'])
def song_req(artist, album, song):
    mydata = local_db()
    if flask.request.method == 'POST':
        json_data = flask.request.json
        song_id = json_data[0]
        statement = 'SELECT path FROM Songs WHERE id=?'
        song_path = sql_execute(mydata.Cursor, statement, [song_id])[0][0]
        Player.play_song(song_path)
    return "OK"

if __name__ == '__main__':
    http_server = WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    http_server.serve_forever()
