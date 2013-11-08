import json
import re
import gevent
from gevent import subprocess, socket, queue

def output_parser(out_string):
    return dict(zip(["message", "value"], re.split('[:=]', out_string.strip().replace("'", ""), 1)))

class MPlayerControl(object):
    def __init__(self):
        self.process = None
        self.message = None
        self.listeners = []
        self.Queue = queue.Queue()
        self.song_list = []
        self.player_launched = False
        self.index = 0

    def launch(self, song):
        self.song_list.append(song)
        self.Queue.put({"message": "list", "value": self.song_list})
        if not self.player_launched:
            self.index = 0
            self.player_launched = gevent.spawn(self._song_queue_mgmt)

    def _song_queue_mgmt(self):
        self.player_launched = True
        while self.index < len(self.song_list) or self._active():
            if not self._active():
                self.play_song(self.song_list[self.index]["path"])
                self.Queue.put({"message": "index", "value": self.index})
                self.index = self.index + 1
            gevent.sleep(0.5)
        self.player_launched = False
        self.index = 0

    def start(self):
        gevent.spawn(self._queue_mgmt)

    def _queue_mgmt(self):
        while True:
            message = self.Queue.get()
            keep_list = []
            for listener in self.listeners:
                try:
                    listener.send(json.dumps(message))
                    keep_list.append(listener)
                except IOError as e:
                    pass
            self.listeners = keep_list

    def _active(self):
        return self.process is not None and self.process.poll() is None

    def _query_pos(self):
        while True:
            if self._active():
                self.process.stdin.write("pausing_keep_force get_percent_pos\n")
                self.process.stdin.flush()
                gevent.sleep(1)
            else:
                raise gevent.GreenletExit
            gevent.sleep()

    def _read(self):
        while True:
            if self._active():
                message = self.process.stdout.readline()
                parsed_message = output_parser(message)
                self.Queue.put(parsed_message)
            else:
                raise gevent.GreenletExit
            gevent.sleep()

    def _wrapper_stdin(self, command):
        if self._active():
            try:
                self.process.stdin.write(command)
                self.process.stdin.flush()
            except IOError:
                pass
            else:
                return

    def quit(self):
        self._wrapper_stdin("quit\n")

    def get_song_list(self):
        self.Queue.put({"message": "list", "value": self.song_list})

    def get_metadata(self):
        self._wrapper_stdin("pausing_keep_force get_meta_artist\n")
        self._wrapper_stdin("pausing_keep_force get_meta_album\n")
        self._wrapper_stdin("pausing_keep_force get_meta_title\n")
        self._wrapper_stdin("pausing_keep_force get_property pause\n")

    def next_song(self):
        self._wrapper_stdin("stop\n")

    def previous_song(self):
        self.index = self.index - 2
        self._wrapper_stdin("stop\n")

    def pause_unpause(self):
        self._wrapper_stdin("pause\n")
        self._wrapper_stdin("pausing_keep_force get_property pause\n")

    def play_song(self, song_path):
        """Launches gmplayer if not active and play song else do nothing"""
        song_path = song_path.encode('utf-8')
        if self._active():
            try:
                self.process.stdin.write("pausing_keep_force loadfile '{0}' 1\n".format(song_path))
                self.process.stdin.flush()
            except IOError:
                pass
            else:
                return

        args = ['mplayer', '-slave', '-quiet', song_path]
        self.process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        gevent.spawn(self._read)
        gevent.spawn(self._query_pos)

