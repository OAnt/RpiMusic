import threading
import sqlite3
import flask
import json

import pimusic.player

DATABASE = '/Users/Antoine/Documents/Pn/projects/databases/RpiPlayer.db'
DEBUG = True
Player = pimusic.player.MPlayerControl('/tmp/musicfifo')

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
        statement = 'SELECT Songs.id, Song, albums.id, albums.artist_id, path FROM Songs, albums WHERE Songs.album_id = albums.id and albums.id=? and albums.artist_id=?'
        result = sql_execute(mydata.Cursor, statement, [album, artist])
        return json.dumps(result)

@app.route('/music/<artist>/<album>/<song>', methods = ['POST'])
def song_req(artist, album, song):
    mydata = local_db()
    if flask.request.method == 'POST':
        json_data = flask.request.json
        song_path = json_data[4]
        Player.play_song(song_path)

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 8000)
