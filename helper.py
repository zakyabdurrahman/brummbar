class songList:
    def __init__(self, guild):
        self.guild = guild
        self.songs = []
        self.index = 0
        self.loop = False
    def add(self, track):
        self.songs.append(track)

#songList is a class containing info for a player, including the track index, the tracks, and loop bool