import pygame
import gevent
import threading

class Player(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        pygame.mixer.init()
        self.player = pygame.mixer.music
        self.queue = []
        self.playing = False

    def play(self):
        self.player.play()

    def load(self):
        try:
            self.player.load(self.queue.pop(0))
        except IndexError:
            self.playing = False

    def next_song(self):
        self.load()
        self.play()

    def pause(self):
        self.player.pause()

    def stop(self):
        self.player.stop()

    def add_song(self, song):
        self.queue.append(song)

    def launch(self):
        self.stop()
        self.playing = True
        self.start()

    def run(self):
        while True:
            if not self.player.get_busy():
                self.next_song()
            if not self.playing:
                break
