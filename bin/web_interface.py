#! /home/pi/.virtualenvs/PyPlayer/bin/python

import threading
import sqlite3
import flask
import json
import os

import gevent
from gevent.wsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

import pimusic.player

DATABASE = '/home/pi/databases/usrDB3.db'
#DEBUG = True
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
def get_index():
    index = open('/home/pi/projects/RpiMusic/static/index.html')
    response = index.read()
    index.close()
    return flask.make_response(response)

@app.route('/api')
def api():
    if flask.request.environ.get('wsgi.websocket'):
        ws = flask.request.environ['wsgi.websocket']
        Player.websockets[ws.socket] = ws
        Player.get_metadata()
        Player.get_song_list()
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

@app.route('/player/volume', methods=['POST'])
def set_volume():
    if flask.request.method == 'POST':
        json_data = flask.request.json
        print json_data
    #print flask.request.json

@app.route('/music')
def get_music():
    mydata = local_db()
    statement = 'SELECT id, name FROM artists'
    result = sql_execute(mydata.Cursor, statement, [])
    return json.dumps(result)

@app.route('/music/<artist>', methods=['GET'])
def artist_req(artist):
    mydata = local_db()
    if flask.request.method == 'GET':
        statement = 'SELECT albums.id, album, albums.artist_id FROM albums, artists WHERE artists.id=? and albums.artist_id = artists.id'
        result = sql_execute(mydata.Cursor, statement, [artist])
        return json.dumps(result)

@app.route('/music/<artist>/<album>', methods=['GET'])
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
        statement = 'SELECT song, path FROM Songs WHERE id=?'
        song_values = sql_execute(mydata.Cursor, statement, [song_id])[0]
        song_details = {"title": song_values[0], "path": song_values[1]}
        Player.launch(song_details)
    return "OK"

if __name__ == '__main__':
    app.debug = True
    http_server = WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    http_server.serve_forever()
