#contols mplayer using a fifo from python
import os
import json
import errno

import gevent
from gevent import subprocess, socket, queue

def output_parser(out_string):
    return dict(zip(["message", "value"], out_string.strip().split("=")))

class MPlayerControl(object):
    def __init__(self):
        self.process = None
        self.message = None
        self.listeners = []
        self.queue = queue.Queue()

    def start(self):
        gevent.spawn(self._queue_mgmt)

    def _queue_mgmt(self):
        while True:
            message = self.queue.get()
            parsed_message = output_parser(message)
            keep_list = []
            for listener in self.listeners:
                try:
                    listener.send(json.dumps(parsed_message))
                    keep_list.append(listener)
                except IOError as e:
                    pass
            self.listeners = keep_list

    def _active(self):
        return self.process is not None and self.process.poll() is None

    def _query_pos(self):
        while True:
            if self._active():
                self.process.stdin.write("get_percent_pos\n")
                self.process.stdin.flush()
                gevent.sleep(1)
            else:
                raise gevent.GreenletExit
            gevent.sleep()

    def _read(self):
        while True:
            if self._active():
                message = self.process.stdout.readline()
                self.queue.put(message)
            else:
                raise gevent.GreenletExit
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

        args = ['mplayer', '-slave', '-quiet', song_path]
        self.process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        gevent.spawn(self._read)
        gevent.spawn(self._query_pos)

