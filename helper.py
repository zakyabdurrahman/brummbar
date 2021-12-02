class songList:
    def __init__(self, guild):
        self.guild = guild
        self.songs = []
        self.index = 0
        
    def add(self, track):
        self.songs.append(track)

