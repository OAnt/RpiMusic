#! /Users/Antoine/.virtualenvs/RpiSpeaker/bin/python

import threading
import sqlite3
import flask
import json
import os

import gevent

import pimusic.player
import conf
from model import SongList

def sql_execute(cursor, statement, values):
    cursor.execute(statement, values)
    result = cursor.fetchall()
    return result

def json_response(data):
    resp = flask.Response(json.dumps(data))
    resp.headers['content-type'] = 'Application/json'
    return resp

def pimusic_server(conf, player):
    DATABASE = conf['database']
    app = flask.Flask(__name__)
    app.config.from_object(conf)

    def local_db():
        mydata = threading.local()
        if not hasattr(mydata, 'Database'):
            mydata.Database = sqlite3.connect(DATABASE)
            mydata.Cursor = mydata.Database.cursor()
        return mydata

    @app.route('/')
    def get_index():
        index = open(os.path.join(conf['static_files'], 'index.html'))
        response = index.read()
        index.close()
        return flask.make_response(response)

    @app.route('/api')
    def api():
        if flask.request.environ.get('wsgi.websocket'):
            ws = flask.request.environ['wsgi.websocket']
            listener = pimusic.player.ConnectionListener(ws, player.input_queue)
            player.listeners.add(listener)
            player.get_metadata()
            player.get_song_list()
            while True:
                if ws.socket is None:
                    return "Bye"
                gevent.sleep(1)
        return "OK"

    @app.route('/player/pause', methods=['GET'])
    def pause_unpause():
        player.pause_unpause()
        return 'done'

    @app.route('/player/next', methods=['GET'])
    def next_song():
        player.next_song()
        return 'done'

    @app.route('/player/previous', methods=['GET'])
    def previous_song():
        player.previous_song()
        return 'done'

    @app.route('/music')
    def get_music():
        mydata = local_db()
        statement = 'SELECT id, name FROM artists'
        result = sql_execute(mydata.Cursor, statement, [])
        return json_response(result)

    @app.route('/music/<artist>', methods=['GET'])
    def artist_req(artist):
        mydata = local_db()
        if flask.request.method == 'GET':
            statement = 'SELECT albums.id, album, albums.artist_id FROM albums, artists WHERE artists.id=? and albums.artist_id = artists.id'
            result = sql_execute(mydata.Cursor, statement, [artist])
            return json_response(result)

    @app.route('/music/<artist>/<album>', methods=['GET'])
    def album_req(artist, album):
        mydata = local_db()
        if flask.request.method == 'GET':
            statement = 'SELECT Songs.id, Song, albums.id, albums.artist_id FROM Songs, albums WHERE Songs.album_id = albums.id and albums.id=? and albums.artist_id=?'
            result = sql_execute(mydata.Cursor, statement, [album, artist])
            return json_response(result)

    @app.route('/music/<artist>/<album>/<song>', methods = ['POST'])
    def song_req(artist, album, song):
        mydata = local_db()
        if flask.request.method == 'POST':
            json_data = flask.request.json
            song_id = json_data[0]
            statement = 'SELECT id, song, path FROM Songs WHERE id=?'
            song_values = sql_execute(mydata.Cursor, statement, [song_id])[0]
            song_details = {'id': song_values[0], 'title': song_values[1], 'path': song_values[2]}
            player.launch([song_details])
        return "OK"

    @app.route('/list', methods = ['GET', 'POST'])
    def handle_all_list():
        mydata = local_db()
        if flask.request.method == 'GET':
            statement = 'SELECT id, name FROM playlist'
            return json_response(sql_execute(mydata.Cursor, statement, []))
        if flask.request.method == 'POST':
            song_list = SongList.from_json(flask.request.data)
            return json_response(song_list.save(mydata.Cursor, mydata.Database))

    @app.route('/list/<list_id>', methods = ['GET', 'POST', 'PUT'])
    def handle_list(list_id):
        mydata = local_db()
        if flask.request.method == 'GET':
            statement = 'SELECT Songs.id, Songs.Song FROM Songs, playlist, belong WHERE Songs.id=belong.song AND playlist.id=? AND belong.playlist=playlist.id'
            result = sql_execute(mydata.Cursor, statement, [list_id])
            return json_response(result)
        if flask.request.method == 'POST':
            statement = 'SELECT Songs.id, Songs.Song, Songs.path FROM Songs, playlist, belong WHERE Songs.id=belong.song AND playlist.id=? AND belong.playlist=playlist.id'
            result = sql_execute(mydata.Cursor, statement, [list_id])
            songs = [{'id': song[0], 'title': song[1], 'path':song[2]} for song in result]
            player.clean()
            player.next_song()
            player.launch(songs)
            return 'OK'
        if flask.request.method == 'PUT':
            song_list = SongList.from_json(flask.request.data)
            return json_response(song_list.update(mydata.Cursor, mydata.Database))

    return app

