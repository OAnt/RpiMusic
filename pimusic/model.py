
import json

class Song(object):
    def __init__(self, song_id=None, title=None, path=None):
        self.title = title
        self.id = song_id
        self.path = path


class SongList(object):
    @staticmethod
    def from_json(data):
        list_details = json.loads(data)
        song_list = SongList(name=list_details.get('name', None),
                             songs=list_details.get('songs', None),
                             list_id=list_details.get('id', None))
        return song_list

    def __init__(self, list_id=None, name=None, songs=None):
        self.id = list_id
        self.name = name
        self.songs = songs

    def iter(self):
        for song in self.songs:
            yield (self.id, song)

    def insert_songs(self, cursor):
            cursor.executemany('INSERT INTO BELONG (playlist, song) VALUES (?, ?)',
                    self.iter())

    def save(self, cursor, conn):
        try:
            cursor.execute('INSERT INTO playlist (name, owner) VALUES (?, ?)',
                    [self.name, 'Public'])
            self.id = cursor.lastrowid
            self.insert_songs(cursor)
            conn.commit()
            return {'id': self.id, 'name':self.name}
        except Exception as e:
            return {'id': None, 'name': None}

    def update(self, cursor, conn):
        try:
            cursor.execute('UPDATE playlist set name=?, owner=? WHERE id=?', [self.name, 'Public', self.id])
            cursor.execute('DELETE FROM belong WHERE playlist=?', [self.id])
            self.insert_songs(cursor)
            conn.commit()
            return {'id': self.id, 'name':self.name}
        except Exception as e:
            print e
            return {'id': None, 'name': None}
