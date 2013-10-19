from nose.tools import*
import unittest
import sqlite3
import time

import pimusic.player

MusicDB = sqlite3.connect("/Users/Antoine/Documents/Pn/projects/databases/RpiPlayer.db")
Cursor = MusicDB.cursor()

class TestAudio(unittest.TestCase):
    def setUp(self):
        statement = "SELECT path FROM Songs WHERE Song = ? OR Song = ? OR Song = ?"
        Cursor.execute(statement,["drowned maid", "sinister rouge",
                                            "jotun"])
        self.song_list = Cursor.fetchall()
        self.fifo = "/tmp/musicfifo"

    def test_playlist(self):
        Player = pimusic.player.MPlayerControl(self.fifo)
        assert_false(Player.check_mplayer_pid())
        for song in self.song_list:
            Player.play_song(song[0])
            assert_true(Player.check_mplayer_pid())
        time.sleep(10)
        Player._quit()
