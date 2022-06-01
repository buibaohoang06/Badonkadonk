from discord.ext import commands
from dotenv import load_dotenv
from os import getenv
import urllib.request
from urllib.error import HTTPError
import discord
import json
import requests
import random
bot = commands.Bot(command_prefix="els ", help_command=None)

@bot.event
async def on_ready():
    print("Ready!")
@bot.command()
async def ping(ctx):
    await ctx.channel.send("Pong!")
#get help
@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Help List", color=0xBB6464)
    embed.add_field(name="Prefix", value="els", inline=False)
    embed.add_field(name="valorant_info <name> <tag>", value="Gather Valorant information of the aforementioned person.", inline=False)
    embed.add_field(name="match_history <name> <tag> <region (ap/br/eu/kr/latam/na)> <amount>", value="Gather match history (5 max).", inline=False)
    embed.add_field(name="dice", value="Roll a random number from 1 to 6.", inline=False)
    embed.add_field(name="howgay <ping a person>", value="Determine how gay is the pinged person.", inline=False)
    embed.add_field(name="howsimp <ping a person>", value="Determine how simp is the pinged person.", inline=False)
    embed.add_field(name="getmeme <ping a person>", value="Get a random meme.")
    embed.add_field(name="pp <ping a person>", value="pp size machine.")
    embed.add_field(name="insult <ping a person>", value="Insult someone.")
    embed.add_field(name="rule34 <tag>", value="Fetch an image from the Rule34 API.", inline=False)
    await ctx.channel.send(embed=embed)
    await ctx.channel.send("All APIs and images belong to their rightful owner.")
    await ctx.channel.send("Made with :heart: by Harvey Bui.")
#valorant info
@bot.command()
async def valorant_info(ctx, name : str, tag : str):
    try:
        url = f'https://api.henrikdev.xyz/valorant/v1/account/{name}/{tag}'
        #set header 
        request = urllib.request.Request(url)
        request.add_header("User-Agent", "Mozilla/5.0")
        response = urllib.request.urlopen(request)
        response_json = json.loads(response.read().decode())
        level = response_json['data']['account_level']
        banner = response_json['data']['card']['small']
        region = response_json['data']['region']
        #gather more info
        puuid = response_json['data']['puuid']
        url2 = f'https://api.henrikdev.xyz/valorant/v1/by-puuid/mmr/{region}/{puuid}'
        request2 = urllib.request.Request(url2)
        request2.add_header("User-Agent", "Mozilla/5.0")
        response2 = json.loads(urllib.request.urlopen(request2).read().decode())
        rank = response2['data']['currenttierpatched']
        elo = response2['data']['elo']

        embed = discord.Embed(title=name + "'s info", color=0xBB6464)
        embed.add_field(name="Name", value=name)
        embed.add_field(name="Tag", value="#" + tag)
        embed.add_field(name="Level", value=level)
        embed.add_field(name="Region", value=region)
        embed.add_field(name="Rank", value=rank)
        embed.add_field(name="ELO", value=elo)
        embed.set_thumbnail(url=banner)
        await ctx.channel.send(embed=embed)
    except HTTPError:
        await ctx.channel.send("Error occured, try again later.")
@valorant_info.error
async def valinfoerror(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.channel.send(f"Insufficient Arguments. Try again or reference the help command.\nRaised error: {error}")
    elif isinstance(error, commands.BadArgument):
        await ctx.channel.send(f"Data type not supported. Try again using the correct form.\nRaised error: {error}")
#match history
@bot.command()
async def match_history(ctx, name : str, tag : str, region : str, amount : int):
    await ctx.channel.send("Gathering Info.")
    await ctx.channel.send("The response is immediate. If no data is displayed, the account haven't played any match this season.")
    try:
        url = f'https://api.henrikdev.xyz/valorant/v3/matches/{region}/{name}/{tag}'
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        res = json.loads(urllib.request.urlopen(req).read().decode())
        #respond with an embed
        if int(amount) > len(res['data']):
            await ctx.channel.send("Sorry. The amount you entered surpassed the preset amount. (Max. 5)")
        else:
            for i in range(0, int(amount)):
                #check team side
                if res['data'][i]['metadata']['mode'] == "Deathmatch":
                    winner = res['data'][i]['kills'][len(res['data'][i]['kills']) - 1]['killer_display_name']
                    time = res['data'][i]['metadata']['game_start_patched']
                    game_map = res['data'][i]['metadata']['map']
                    server = res['data'][i]['metadata']['cluster']
                    embed = discord.Embed(title="Match History of " + name, color=0xBB6464)
                    embed.add_field(name="Time", value=time, inline=False)
                    embed.add_field(name="Winner", value=winner)
                    embed.add_field(name="Map", value=game_map)
                    embed.add_field(name="Server", value=server)
                    embed.add_field(name="Mode", value="Deathmatch")
                    await ctx.channel.send(embed=embed)
                else:
                    #look for winner
                    for j in range(0, len(res['data'][i]['players']['all_players'])):
                        if res['data'][i]['players']['all_players'][j]['name'] == name:
                            team = res['data'][i]['players']['all_players'][j]['team']
                            status = res['data'][i]['teams'][team.lower()]['has_won']
                            break
                        else:
                            continue
                    time = res['data'][i]['metadata']['game_start_patched']
                    game_mode = res['data'][i]['metadata']['mode']
                    game_map = res['data'][i]['metadata']['mode']
                    server = res['data'][i]['metadata']['cluster']
                    embed = discord.Embed(title="Match History of " + name, value=time, inline=False, color=0xBB6464)
                    embed.add_field(name="Time", value=time, inline=False)
                    embed.add_field(name="Mode", value=game_mode)
                    embed.add_field(name="Map", value=game_map)
                    embed.add_field(name="Server", value=server)
                    embed.add_field(name="Your team", value=team)
                    embed.add_field(name="Win (True/False)", value=status)
                    await ctx.channel.send(embed=embed)
    except HTTPError:
        await ctx.channel.send("Error occurred when fetching data. Error: " + res['message'])
@match_history.error
async def mherror(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.channel.send(f"Insufficient Arguments. Try again or reference the help command.\nRaised error: {error}")
    elif isinstance(error, commands.BadArgument):
        await ctx.channel.send(f"Data type not supported. Try again using the correct form.\nRaised error: {error}")
#fun and games
@bot.command()
async def dice(ctx):
    answer = random.randint(1, 6)
    image = ""
    if answer == 1:
        image = "https://i.ibb.co/JxCQbs2/Screenshot-2022-05-29-095331.png"
    elif answer == 2:
        image = "https://i.ibb.co/wMNyxqs/Screenshot-2022-05-29-095529.png"
    elif answer == 3:
        image = "https://i.ibb.co/5nW9S0s/Screenshot-2022-05-29-095633.png"
    elif answer == 4:
        image = "https://i.ibb.co/WBhpwD8/Screenshot-2022-05-29-095717.png"
    elif answer == 5:
        image = "https://i.ibb.co/9Y7fWxk/Screenshot-2022-05-29-095746.png"
    elif answer == 6:
        image = "https://i.ibb.co/NnXC9XP/Screenshot-2022-05-29-095817.png"
    
    embed = discord.Embed(title="The Dice has Spoken!", color=0xBB6464)
    embed.add_field(name="Rolled", value=answer)
    embed.set_thumbnail(url=image)
    await ctx.channel.send(embed=embed)
@bot.command()
async def howgay(ctx, *,  avamember : discord.Member=None):
    amount = random.randint(0, 100)
    embed = discord.Embed(title="Thiels Bot Gay-inator", color=0xBB6464)
    embed.add_field(name="Gay Amount", value=str(avamember) + "is " + str(amount) + "% gay :rainbow_flag:")
    embed.set_thumbnail(url=avamember.avatar_url)
    await ctx.channel.send(embed=embed)
@howgay.error
async def howgay_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.channel.send("You have to provide an username!")
@bot.command()
async def howsimp(ctx, *, member : discord.Member=None):
    amount = random.randint(0, 100)
    embed = discord.Embed(title="Thiels Bot Simp-inator", color=0xBB6464)
    embed.add_field(name="Simp Amount", value=str(member) + " is " + str(amount) + "% simp :female_sign:")
    embed.set_thumbnail(url=member.avatar_url)
    await ctx.channel.send(embed=embed)
@howsimp.error
async def howsimperror(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.channel.send("You need to provide an username!")
@bot.command()
async def getmeme(ctx):
    try:
        with urllib.request.urlopen("https://meme-api.herokuapp.com/gimme") as meme_url:
            data = json.loads(meme_url.read().decode())
            data_return = data['preview'][3]
        await ctx.channel.send(data_return)
    except json.IndexError:
        await ctx.channel.send("The API couldn't fetch anything. Try again later.")
@bot.command()
async def insult(ctx, name):
	with urllib.request.urlopen("https://evilinsult.com/generate_insult.php?lang=en&type=json") as insult:
		data = json.loads(insult.read().decode())
		response = data['insult']
	await ctx.channel.send(f"{name}. {response}")
@insult.error
async def insult_error(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.channel.send("You haven't mentioned who you wanted to roast. Mention that person and try again!")
@bot.command()
async def pp(ctx, name : discord.Member = None):
    embed = discord.Embed(title="Thiels Bot PP-Inator", color=0xBB6464)
    embed.add_field(name="PP Size", value=str("8" + "=" * random.randint(1, 30) + "D"))
    embed.set_thumbnail(url=name.avatar_url)
    await ctx.channel.send(embed=embed)
@pp.error
async def pperror(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.channel.send("You need to mention someone.")
@bot.command()
async def rule34(ctx, tag):
    message = tag.replace(" ", "%20")
    if message == "random":
        url = "https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags=*"
        with urllib.request.urlopen(url) as r34:
            data = json.loads(r34.read().decode())
            data_return = data[random.randint(0, len(data))]['sample_url']
        await ctx.channel.send(data_return)
    else:
        url = "https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags=" + message
        try:
            with urllib.request.urlopen(url) as r34:
                data = json.loads(r34.read().decode())
                data_return = data[random.randint(0, len(data))]['sample_url']
            await ctx.channel.send(data_return)
        except json.JSONDecodeError:
            await ctx.channel.send("Invalid keywords, please try again")
        except json.IndexError:
            await ctx.channel.send("Can't find anything with the given keyword") 
@rule34.error
async def r34error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.channel.send("Missing required argument!")
@bot.command()
async def hypixel_info(ctx, username):
    #get uuid
    with urllib.request.urlopen(f'https://api.mojang.com/users/profiles/minecraft/{username}') as data:
        res = json.loads(data.read().decode())
        uuid = res['id'] 
    #get data from hypixel api
    with urllib.request.urlopen(f'https://api.hypixel.net/player?key=1eff5fd3-5ddc-4d6b-ad91-8533a558c63a&uuid={uuid}') as hypixel:
        player_data = json.loads(hypixel.read().decode())
    #process rank
    if player_data['player']['newPackageRank'] == "VIP_PLUS":
        rank = "VIP+"
    elif player_data['player']['newPackageRank'] == "VIP":
        rank = "VIP"
    elif player_data['player']['newPackageRank'] == "MVP":
        rank = "MVP"
    elif player_data['player']['newPackageRank'] == "MVP_PLUS":
        rank = "MVP+"
    elif player_data['player']['newPackageRank'] == "MVP_PLUS" and player_data['player']['monthlyPackageRank'] == "SUPERSTAR":
        rank = "MVP++"
    embed = discord.Embed(title=username + "'s info", color=0xBB6464)
    embed.add_field(name="Username", value=username)
    embed.add_field(name="Rank", value=rank)
    embed.add_field(name="Karma", value=player_data['player']['karma'])
    embed.add_field(name="Bedwars Level", value=player_data['player']['achievements']['bedwars_level'])
    embed.add_field(name="Total beds broken", value=player_data['player']['achievements']['bedwars_beds'])
    embed.add_field(name="Total Bedwars Wins", value=player_data['player']['achievements']['bedwars_wins'])
    embed.add_field(name="Skywars Level", value=player_data['player']['achievements']['skywars_you_re_a_star'])
    embed.set_thumbnail(url="https://mc-heads.net/avatar" + uuid)
    await ctx.channel.send(embed=embed)
if __name__ == "__main__":
    load_dotenv()
    bot.run(getenv("TOKEN"))
