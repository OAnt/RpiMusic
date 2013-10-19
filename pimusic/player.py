#contols mplayer using a fifo from python
import subprocess
import os
class MPlayerControl(object):
    def __init__(self, fifo):
        self.fifo = fifo
        self.statedb = None
        self.process = None
        os.remove(self.fifo)
        os.mkfifo(self.fifo)

    def check_mplayer_pid(self):
        """Checks if an instance of mplayer is active, return True if it is
        False otherwise
        """
        try:
            exe_path = os.readlink("/proc/{0}/exe".format(self.process.pid))
            exe_path, process = os.path.split(exe_path)
        except OSError:
            return False
        if process == "mplayer":
            return True
        else:
            return False

    def _update_fifo(self, song):
        fifo = open(self.fifo, 'w')
        fifo.write("loadfile '{0}' 1".format(song))

    def play_song(self, song_path):
        """Launches mplayer if not active and play song else do nothing"""
        if not check_mplayer_pid():
            args = ['mpalyer', '-slave', '-input',
                    'file={0}'.format(self.fifo),
                    song_path]
            self.process = subprocess.Popen(args)
        else:
            self._update_fifo(song)

    def add_song(self, song):
        """adds a to mplayer's queue"""
        pass
