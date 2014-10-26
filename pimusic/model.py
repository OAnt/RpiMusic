import json

class Song(object):
    def __init__(self, song_id=None, title=None, path=None):
        self.title = title
        self.id = song_id
        self.path = path


class SongList(object):
    def __init__(self, list_id=None, name=None, songs=None):
        self.id = list_id
        self.name = name
        self.songs = songs

    def iter(self):
        for song in self.songs:
            yield (self.id, song)

    def save(self, cursor, conn):
        try:
            cursor.execute('INSERT INTO playlist (name, owner) VALUES (?, ?)',
                    [self.name, 'Public'])
            self.id = cursor.lastrowid
            cursor.executemany('INSERT INTO BELONG (playlist, song) VALUES (?, ?)',
                    self.iter())
            conn.commit()
            return 'OK', 200
        except Exception as e:
            return 'NOK', 400
