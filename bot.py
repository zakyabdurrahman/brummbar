import discord, os, logging, pomice, time, asyncio





from helper import songList
from discord.ext import commands



playing = False
logging.basicConfig(level=logging.CRITICAL, format=' %(asctime)s - %(levelname)s - %(message)s')
class MyBot(commands.Bot):
    def __init__(self) -> None:
        watching = discord.Activity(type=discord.ActivityType.watching, name='for !p to play music')
        super().__init__(command_prefix='!', activity=watching)
        self.help_command = None
        self.add_cog(Misc(self))
        self.add_cog(Music(self))

    async def on_ready(self) -> None:
        logging.critical('i\'m ready')
        await self.cogs['Music'].start_nodes()





class Misc(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.songs = []
    
    @commands.command(aliases=['s'])
    async def sieg(self, ctx: commands.Context):
        await ctx.send('Heil!')
    
    @commands.command(aliases=['h'])
    async def help(self, ctx: commands.Context):
        embed = discord.Embed(title="Commands", description="""This is all kinds of commands you can use. 
        Its honestly pretty barebone right now, but I will add more features in some time.
        """, color=discord.Color.purple())
        embed.add_field(name="!p + <keyword>", value="Use this command to play an audio from Youtube. e.g `!p panzelied`", inline=False)
        embed.add_field(name="(!q or !query) + <keyword>", value="Use this command to search Youtube, it will return top 5 entry that matched", inline=False)
        embed.add_field(name="!stop", value="Use this command to stop, clear all playlist and disconnect the bot", inline=False)
        embed.add_field(name='(!playlist or !np or !pl)', value="Use this command to see the current playlist")
        embed.add_field(name='(!loop or !l)', value="Use this command to enable Brummbar to loop the playlist")
        await ctx.send(embed=embed)

class Music(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.pomice = pomice.NodePool()
        self.i = 0 #for indexing
        self.trackList = []
        self.vc = []
    async def start_nodes(self):
        await self.pomice.create_node(bot=self.bot, host='node1.cjstevenson.com', port='25503', password='lookbehindyou', identifier='RussianMartabak', spotify_client_id=None, spotify_client_secret=None)
        logging.critical("node ready")
    
    def findsongList(self, guild):
        for songlist in self.trackList:
            if songlist.guild == guild:
                return songlist
        return None
    
    @commands.Cog.listener()
    #listen if bot disconnected
    async def on_voice_state_update(self, member, before, after):
        logging.critical(f"the member: {member} changed, {before.channel} -> {after.channel}")
        try: 
            functionGuild = before.channel.guild
        except: 
            functionGuild = None
        if member == self.bot.user and after.channel == None:
            
            #find the voiceclient 
            for VClient in self.bot.voice_clients:
                if VClient.guild == functionGuild:
                    dead = VClient.is_dead
                    logging.critical(f'vclient found: {VClient}, is it dead? {dead}')
                    await VClient.destroy()
                    break
            
    
    
    
    
    @commands.Cog.listener()
    #add 1 to i when a player start a track
    async def on_pomice_track_start(self, player, track):
        logging.critical(f'{track} is starting')
        playlist = self.findsongList(player.guild)
        if playlist:
            playlist.index += 1



    @commands.command(aliases=['query'])
    async def q(self, ctx: commands.Context, *, search: str):
        try:
            player = self.vc[0]
        except:
            ctx.send("bot not connected yet")
            return
        results = await player.get_tracks(query=f'{search}')
        if results:
            await ctx.send("**Tracks Found: **")
            limit = min(len(results), 5)
            limit += 1
            for i in range(1, limit):
                await ctx.send(f"`{i}. {results[i].title}`")
        else:
            ctx.send("not found or bot isn't connected to vc yet")

    @commands.command(aliases=['l'])
    async def loop(self, ctx: commands.Context):
        localSongList = self.findsongList(ctx.guild)
        if localSongList:
            if localSongList.loop == False:
                localSongList.loop = True
                await ctx.send('**Loop Enabled**')
            else:
                localSongList.loop = False
                await ctx.send('**Loop Disabled**')



    @commands.command(aliases=['np', 'pl'])
    async def playlist(self, ctx: commands.Context):
        localSongList = self.findsongList(ctx.guild)
        i = 0
        if localSongList:
            await ctx.send('**Currently Playing:**')
            for song in localSongList.songs:
                i += 1
                await ctx.send(f'`{i}. {song.title}`')
        else:
            await ctx.send('There is no playlist')
        
    @commands.command(aliases=['play'])
    async def p(self, ctx: commands.Context, *, search: str):
        #make bot join and check if it already joined a vc
        
        if search:
            try:
                #is it in the vc user in?
                logging.critical('the try is invoked')
                vc = ctx.author.voice.channel
                
                #if bot is not in the vc
                if not self.bot.user in vc.members:
                    
                    VClient = await vc.connect(cls=pomice.Player)
                    
                    guildSongList = songList(VClient.guild)
                    self.trackList.append(guildSongList)
                    self.vc.append(VClient)
                #if bot already in vc
                else : 
                    for channel in self.bot.voice_clients:
                        if channel.channel == vc:
                            VClient = channel
                            break
                    for item in self.trackList:
                        if item.guild == VClient.guild:
                            guildSongList = item
                            break
                    guildSongList = self.findsongList(ctx.guild)
                
                
                if not guildSongList:
                    guildSongList = songList(VClient.guild)
                    self.trackList.append(guildSongList)
                logging.critical(VClient.is_playing)
                results = await VClient.get_tracks(query=f'{search}')
                
                if results and VClient.is_playing == False:
                        
                    await VClient.play(track=results[0])
                    guildSongList.add(results[0])
                    music = str(results[0].title)
                    thumbnail = str(results[0].uri)
                    #track announcer
                    logging.critical(results)
                    await ctx.send(f"**Playing** `{music}`")
                    
                    return   
                        
                elif results:
                    guildSongList.add(results[0])
                    await ctx.send(f"**Added** `{results[0].title}` to queue")
                    logging.critical(guildSongList.songs)

                else: 
                    await ctx.send('either no results or bot is still playing')
                    
            except BaseException as err:
                await ctx.send("you are not in a voice channel")
                logging.critical(f"exception occured {err}")
    

    @commands.command()
    async def stop(self, ctx: commands.Context):
        
        
        for vc in self.bot.voice_clients:
            if vc.is_playing and vc.guild==ctx.guild:
                playlist = self.findsongList(vc.guild)
                await vc.stop()
                if playlist:
                    self.trackList.remove(playlist)
                break
     
    @commands.Cog.listener()
    async def on_pomice_track_end(self, player, track, reason):
        #check list and play next song in list
        #reset index if its already maximum
        #find the correct songlist in self.tracklist 
        logging.critical("a player has stopped playing track")
        if player.is_playing:
            await player.stop()
        playlist = self.findsongList(player.guild)
        try: #this is the mechanism to play through the playlist ot looping
            await player.play(playlist.songs[playlist.index])
            logging.critical(f'current index is {playlist.index}')
        except: 
            if playlist.loop == True:
                playlist.index = 0
                await player.play(playlist.songs[0])
            else:
                logging.critical('no next song')
        await asyncio.sleep(20)
        if not player.is_playing:
            if playlist:
                self.trackList.remove(playlist)
                playlist.index = 0
            await player.destroy()
        logging.critical(player.current)
        logging.critical(track)
        logging.critical(reason)
        
    
               #break
TOKEN = os.getenv("TOKEN")
bot = MyBot()
bot.run(TOKEN)
