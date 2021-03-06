import asyncio
import lightbulb 
import hikari
import jokeapi
from utils import get_news, eightball_response, hack_user

class Misc(lightbulb.Plugin):
    def __init__(self):
        self.bot: lightbulb.BotApp
        super().__init__("Miscellaneous Commands", "Miscellaneous Utility Commands")

misc = Misc()


@misc.command
@lightbulb.option(name="query", description="The subject to search for!", type=str, required=True)
@lightbulb.command(name="news", description="...", auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def news_command(ctx: lightbulb.SlashContext):
    query = ctx._options.get("query")
    response = await get_news(api_key=misc.bot.news_key, query=query, req_client=misc.bot.http)
    news_error = response.get("error")
    if news_error:
        return await ctx.respond(news_error)

    embed = hikari.Embed(title=response.get("title"), description=response.get("description"), colour=ctx.author.accent_colour).add_field("** **", response.get("content")).add_field("Author", response.get("author")).add_field("Article", f"You can get the article [here]({response.get('url')})!").set_thumbnail(response.get("image"))
    return await ctx.respond(embed=embed)

@misc.command
@lightbulb.option(name="word", description="The word to search!", type=str, required=True)
@lightbulb.command(name="def", description="Get the meaning of a word!", ephemeral=True, auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def get_meaning(ctx: lightbulb.SlashContext):
    word_to_search = ctx._options.get("word")
    resp = await misc.bot.http.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word_to_search}")
    if resp.status != 200:
        return await ctx.respond("Could not find that word!")
    content = await resp.json()
    data = content[0]
    embed = hikari.Embed(title=data['word'], description=f"{data['phonetics'][1]['text']}\nYou can listen to the pronunciation [here]({data['phonetics'][0]['audio']}) (if applicable)", colour=ctx.author.accent_color).add_field("Part of Speech", data['meanings'][0]['partOfSpeech']).add_field("More Links", "\n".join(data['sourceUrls'])).add_field("Definitions", "\n- ".join([definit['definition'] for definit in data['meanings'][0]['definitions']]))
    await ctx.respond(embed=embed)

@misc.command
@lightbulb.command(name="insult", description="Send something insulting!", ephemeral=True, auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def get_insult(ctx: lightbulb.SlashContext):
    resp = await misc.bot.http.get("https://evilinsult.com/generate_insult.php?lang=en&type=json")
    if resp.status != 200:
        return await ctx.respond("Could not find an insult!")
    data = await resp.json()
    return await ctx.respond(f"**{data['insult']}**")

@misc.command
@lightbulb.command(name="quote", description="Get a quote!", auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def get_quote(ctx: lightbulb.SlashContext):
    resp = await misc.bot.http.get("https://zenquotes.io/api/random")
    if resp.status != 200:
        return await ctx.respond("Could not get a quote!")
    data = await resp.json()
    await ctx.respond("**" + data[0]['q'] + "**" + " - " + "*" + data[0]['a'] + "*")

@misc.command
@lightbulb.option(name="movie", description="The Movie name!", type=str, required=True)
@lightbulb.command(name="movie", description="Get information about a movie!", auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def get_movie_data(ctx: lightbulb.SlashContext):
    movie = ctx._options.get("movie")
    res = await misc.bot.http.get(f"http://www.omdbapi.com/?t={movie.title()}&plot=full&apikey=" + misc.bot.movie_key)
    if res.status != 200:
        return await ctx.respond("Could not find that movie!")
    content = await res.json()
    embed = hikari.Embed(title=content['Title']).add_field(name="Released", value=content['Released']).add_field(name="Duration", value=content['Runtime']).add_field(name="Genre", value=content['Genre']).add_field(name="Rated", value=content['Rated']).add_field(name="Directed By", value=content['Director']).add_field(name="Casts", value=content['Actors']).set_thumbnail(content['Poster'])
    if len(content['Plot']) > 200:
        _plot = content['Plot']
        plot = _plot[:200]
    embed.add_field(name="Plot", value=f"{plot}...", inline=False).add_field(name="Country", value=content['Country']).add_field(name="Awards", value=content['Awards']).add_field(name="IMDB Rating", value=content['imdbRating']).add_field(name="Box Office Earnings", value=content['BoxOffice']).add_field(name="IMDB Upvotes", value=content['imdbVotes'])
    await ctx.respond(embed=embed)
    
    for rate in content['Ratings']:
        embed.add_field(name=rate['Source'], value=rate['Value'])

@misc.command
@lightbulb.command(name="joke", description="Get a random joke!", auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def get_joke(ctx: lightbulb.SlashContext):
    j = await jokeapi.Jokes()
    raw_joke = await j.get_joke(safe_mode=True)
    if raw_joke['type'] == "single":
        embed = hikari.Embed(title="J.O.K.E", description=raw_joke['joke'], color=ctx.author.accent_colour)
    else:
        embed = hikari.Embed(title="J.O.K.E", description=f"{raw_joke['setup']}\n{raw_joke['delivery']}", color=ctx.author.accent_colour)
    await ctx.respond(embed=embed)

@misc.command
@lightbulb.command(name="meme", description="Get a meme", auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def get_meme(ctx: lightbulb.SlashContext):
    resp = await misc.bot.http.get("https://meme-api.herokuapp.com/gimme")
    content = await resp.json()
    embed = hikari.Embed(title= content["title"], description=f"By: {content['author']}", color=ctx.author.accent_color).set_footer(text=f"Reddit Page: {content['postLink']}").set_image(content["url"])
    await ctx.respond(embed=embed)

@misc.command
@lightbulb.option(name="query", description="Eightball requires your views.", type=str, required=True)
@lightbulb.command(name="8ball", description="Let the 8ball decide!", auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def eightball(ctx: lightbulb.SlashContext):
    await ctx.respond(eightball_response())

@misc.command
@lightbulb.option(name="member", description="The member to hack!", type=hikari.Member, required=True)
@lightbulb.command(name="hack", description="Hack a user! WARNING: This is a dangerous and real hack", auto_defer=True, ephemeral=False)
@lightbulb.implements(lightbulb.SlashCommand)
async def hack_(ctx: lightbulb.SlashContext):
    member = ctx._options.get("member")
    hac_c = hack_user(member)
    msg = await ctx.respond("The completely reliable and dangerous hack will begin in just a few moments...")
    await asyncio.sleep(3)
    for hack in hac_c:
        await msg.edit(content=hack)
        await asyncio.sleep(2)

@misc.command
@lightbulb.option(name="query", description="The topic to search for!", required=True, type=str)
@lightbulb.command(name="spotify", description="Search spotify for information!", auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def spotify_(ctx: lightbulb.SlashContext):
    query = ctx._options.get("query")
    data = misc.bot.spotify_search(query, limit=1)
    sp_data = data['tracks']['items'][0]
    album_type = sp_data['album']['album_type']
    if album_type == 'single':
        song_url = sp_data['external_urls']['spotify']
        song_name = sp_data['name']
        artists = sp_data['artists'][0]['name']
        album_type = sp_data['album']['type']
        album_url = sp_data['album']['external_urls']['spotify']
        artists_url = sp_data['artists'][0]['external_urls']['spotify']
        embed = hikari.Embed(title=song_name, description="", color=ctx.author.accent_color).set_thumbnail(sp_data['album']['images'][0]['url'])

        embed.description += f"[{song_name}]({song_url})\n[{artists}]({artists_url})\n[Album]({album_url})\nAlbum Type: {album_type}"

        await ctx.respond(embed=embed)

    elif album_type == 'compilation':
        album_tracks = sp_data['album']['total_tracks']
        album_name = sp_data['album']['name']
        track_url = sp_data['external_urls']['spotify']
        album_release = sp_data['album']['release_date']
        album_link = sp_data['album']['external_urls']['spotify']
        album_image = sp_data['album']['images'][0]['url']
        embed2 = hikari.Embed(title=album_name, description="", color=ctx.author.accent_color).set_thumbnail(album_image)

        embed2.description += f"[Top Track in  the Album]({track_url})\n[Album]({album_link})\nTotal Number of tracks in Album: **{album_tracks}**\nRelease Date: **{album_release}**"

    else:
        return await ctx.respond("Could not get that...")

def load(bot: lightbulb.BotApp):
    bot.add_plugin(misc)