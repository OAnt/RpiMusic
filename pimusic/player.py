#contols mplayer using a fifo from python
import os
import json

import gevent
from gevent import subprocess, socket


class MPlayerControl(object):
    def __init__(self):
        self.process = None
        self.message = None
        self.listeners = []
        self.queue = ["hello"]

    def start(self):
        gevent.spawn(self._read)
        gevent.spawn(self._query_pos)
        gevent.spawn(self._queue_mgmt)

    def _queue_mgmt(self):
        while True:
            while len(self.queue)>1:
                self.queue.pop()
            gevent.sleep()

    def _active(self):
        return self.process is not None and self.process.poll() is None

    def _query_pos(self):
        while True:
            if self._active():
                self.process.stdin.write("get_time_pos\n")
                self.process.stdin.flush()
                gevent.sleep(1)
            gevent.sleep()

    def _read(self):
        while True:
            if self._active():
                message = self.process.stdout.readline()
                self.queue.insert(0, message)
            gevent.sleep()

    def _wrapper_stdin(self, function, *args):
        if self._active():
            try:
                function(*args)
                self.process.stdin.flush()
            except IOError:
                pass
            else:
                return

    def quit(self):
        self._wrapper_stdin(self.process.stdin.write, "quit\n")

    def play_song(self, song_path):
        """Launches gmplayer if not active and play song else do nothing"""
        song_path = song_path.encode('utf-8')
        if self._active():
            try:
                self.process.stdin.write("loadfile '{0}' 1\n".format(song_path))
                self.process.stdin.flush()
            except IOError:
                pass
            else:
                return

        args = ['mplayer', '-slave', song_path]
        self.process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
