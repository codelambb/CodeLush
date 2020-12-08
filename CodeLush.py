import discord
from discord.ext import commands, tasks
import os
from random import choice
import aiohttp
from random import randint
import wikipedia
import time
import datetime
import asyncio
import random
import typing

intents = discord.Intents.all()
prefixes = [">"]
client = commands.Bot(command_prefix=list(prefixes), intents=intents)

client = commands.Bot(command_prefix=prefixes)

status = ['Listening to >help', 'Make sure to read the rules!']

client.remove_command("help")


@client.event
async def on_ready():
    change_status.start()
    print('Bot is ready.')


@tasks.loop(seconds=20)
async def change_status():
    await client.change_presence(activity=discord.Game(choice(status)))


#ping command
@client.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(client.latency * 1000)}ms')


#clear command
@client.command(aliases=["cls", "purge"])
@commands.has_permissions(manage_messages=True, administrator=True)
async def clear(ctx, ammount: int):
    await ctx.channel.purge(limit=ammount + 1)
    await ctx.send(f'I have deleted {ammount} of messages', delete_after=5)
    return


#8ball command
@client.command(aliases=['8ball'])
async def _8ball(ctx, question):
    import random
    responses = [
        "It is certain.",
        "It is decidedly so.",
        "Without a doubt.",
        "Yes - definitely.",
        "You may rely on it.",
        "As I see it, yes.",
        "Most likely.",
        "Outlook good.",
        "Yes.",
        "Signs point to yes.",
        "Reply hazy, try again.",
        "Ask again later.",
        "Better not tell you now.",
        "Cannot predict now.",
        "Concentrate and ask again.",
        "Don't count on it.",
        "My reply is no.",
        "My sources say no.",
        "Outlook not so good.",
        "Very doubtful.",]
    await ctx.send(f'{random.choice(responses)}')


#help command
@client.command(aliases=['h'])
async def help(ctx):
    helpEmbed = discord.Embed(tittle="Help Menu", color=ctx.author.color)
    helpEmbed.set_author(name="Help Menu:\nPrefix = '>'")
    helpEmbed.add_field(
        name="Moderation Command Menu",
        value="```Type >modHelp to open that```",
        inline=True)
    helpEmbed.add_field(
        name="Miscellaneous Command Menu",
        value="```Type >miscHelp to open that```",
        inline=True)

    await ctx.send(embed=helpEmbed)


#modHelp
@client.command()
async def modHelp(ctx):
    mod = discord.Embed(tittle="mod", color=ctx.author.color)
    mod.add_field(
        name="Moderation Command Menu",
        value=
        "```>clear (ammount) : Deletes the specified ammount of messages from the channel```\n```>ban (user) (reasion) : Bans the specified user from the server```\n```>kick (user) (reason) : Kicks the specified user from the server```\n```>mute (user) (reason) : Mutes the specified user from the server```\n```>unmute (user) : Unmutes the specified user```\n```>announce (message) : Sends a announcemnt in sylish embed style```\n"
    )
    mod.set_footer(text="More moderation commands will be added soon")
    await ctx.send(embed=mod)


#miscHelp
@client.command()
async def miscHelp(ctx):
    misc = discord.Embed(tittle="misc", color=ctx.author.color)
    misc.add_field(
        name="Miscellaneous Command Menu",
        value=
        "```>ping : Tells the bot's latency```\n```>8ball (question) : Tells the answer of the asked question in a random yes/no answer```\n```>meme : Send a hot meme from reddit```\n```>userinfo (user) : Send information about mentioned user```\n```>define (querry) : Sends a definition of your querry from wikipedia```\n"
    )
    ctx.send(embed=misc)

#ban command
@client.command(aliases=['b'])
@commands.has_permissions(ban_members=True, administrator=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    await ctx.send(f'Banned {member} from the server.')
    await member.ban(reason=reason)


#kick command
@client.command(aliases=['k'])
@commands.has_permissions(kick_members=True, administrator=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    await ctx.send(f'Kicked {member} from the server.')
    await member.kick(reason=reason)

#unban command
@client.command(aliases=['ub'])
@commands.has_permissions(ban_members=True, administrator=True)
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user

        if(user.name, user.discriminator) == (member_name,member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'Unbanned {user.name}#{user.discriminator}')
            return

    await ctx.send(member+" was not found")

#mute command
@client.command()
@commands.has_permissions(
    kick_members=True,
    manage_messages=True,
    administrator=True,
    manage_roles=True)
async def mute(ctx, member: discord.Member, mute_time: int, *, reason=None):
    if not member:
        await ctx.send("Who do you want me to mute?")
        return
    role = discord.utils.get(ctx.guild.roles, name="Muted")

    if not role:
        await ctx.guild.create_role(name='Muted')

    for channel in ctx.guild.channels:
        await channel.set_permissions(
            role,
            speak=False,
            send_messages=False,
            read_message_history=True,
            read_messages=True)

    await member.add_roles(role)
    await ctx.send(f"{member.mention} was muted for {reason}")
    await member.send(f"You were muted in **{ctx.guild}** for {reason}")

    await asyncio.sleep(mute_time)
    await member.remove_roles(role)
    await ctx.send(f"{member.mention} was unmuted")
    await member.send(f"You were unmuted in **{ctx.guild}**")


#unmute command
@client.command()
@commands.has_permissions(manage_roles=True, administrator=True)
async def unmute(ctx, member: discord.Member):
    mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")
    await member.remove_roles(mutedRole)
    await ctx.send(f'Unmuted {ctx.members.mention}')
    await member.send(f'You have been unmuted from the server {ctx.guild.name}'
                      )


#meme command
@client.command()
async def meme(ctx):
    async with aiohttp.ClientSession() as cs:
        async with cs.get(
                'https://www.reddit.com/r/dankmemes/new.json?sort=hot') as r:
            res = await r.json()
            embed = discord.Embed(title="Memes", color=discord.Color.orange())
            embed.set_image(url=res['data']['children'][random.randint(0, 25)]
                            ['data']['url'])
            await ctx.send(embed=embed)


#kill command
@client.command()
async def kill(ctx, user):
    k = random.randint(0, 5)
    if k == 0:
        await ctx.send(
            f'You challenged {user} to a fist fight to the death. You won.')
    if k == 2:
        await ctx.send(f'{user} had a mid air collision with nyan-cat')
    if k == 3:
        await ctx.send(
            f'{user} fell down a cliff while playing Pokemon Go. Good job on keeping your nose in that puny phone. :iphone:'
        )
    if k == 4:
        await ctx.send(
            f"{user} presses a random button and is teleported to the height of 100m, allowing them to fall to their inevitable death.\nMoral of the story: Don't go around pressing random buttons."
        )
    if k == 5:
        await ctx.send(
            f'{user} is sucked into Minecraft. {user}, being a noob at the so called Real-Life Minecraft faces the Game Over screen.'
        )


#welcome commands
class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = self.bot.get_channel(id=783306605466746881)

        if member.bot == True:
            botrole = discord.utils.get(member.guild.roles, name="Members Bots")
            await member.add_roles(botrole)

        else:
            verifiedrole = discord.utils.get(member.guild.roles, name='Verified')
            await member.add_roles(verifiedrole)

            em = discord.Embed(
                title=f"Hi{member}, Welcome to CodeLush.", description="Thanks for joining this server", color=discord.Color.gree())

            await channel.send(embed=em)
            await member.send(embed=em)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = self.bot.get_channel(id=783306605466746881)

        em = discord.Embed(title=f"It seems like {member.name} just left us", color=discord.Color.red())

        await channel.send(embed=em)

def setup(bot):
    bot.add_cog(Welcome(bot))


#announcemnt command
@client.command(aliases=["ann"])
@commands.has_permissions(administrator=True, manage_messages=True, manage_roles=True, ban_members=True, kick_members=True)
async def announce(ctx,*,message):
    anno = discord.Embed(tittle="ann", color=ctx.author.color)
    anno.add_field(name="Announcement", value=message)
    anno.set_footer(text=f"Announcement by {ctx.author.name}")
    await ctx.send(embed=anno)
    await ctx.send('@everyone', delete_after=3)

#define command
@client.command()
async def define(ctx,*, ask):
    definition = wikipedia.summary(ask, sentences=3, chars=1000, auto_suggest=False, redirect=True) 
    search = discord.Embed(color=ctx.author.color)
    search.add_field(name=ask, value=definition, inline=False)
    await ctx.send(embed=search)

#userinfo command
@client.command(aliases=["ui"])
async def userinfo(ctx, member: discord.Member):
  
  em=discord.Embed(color=member.color)

  em.set_author(name=f"{member.name}'s info")
  em.set_thumbnail(url=member.avatar_url)
  em.set_footer(text=f"Requested by {ctx.author.name}")

  em.add_field(name='Member Name', value=member.name)
  em.add_field(name="Member name in guild", value=member.display_name)

  em.add_field(name="Joined at:", value=member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))

  await ctx.send(embed=em)

#all the errors

#clear error
@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
     em = discord.Embed(title = "Error", description = "Either you have used the command incorrecly or you dont have permission to use this command.", color = discord.Color.red())
     await ctx.send(embed=em, delete_after=5)
    

#8ball error
@_8ball.error
async def _8ball_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
     em = discord.Embed(title = "Error", description = "8ball didnt gave an answer cause you didnt even ask a question idiot", color = discord.Color.red())
     await ctx.send(embed=em, delete_after=5)


#ban error
@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
     em = discord.Embed(title = "Error", description = "Either you have used the command incorrecly or you dont have permission to use this command.", color = discord.Color.red())
     await ctx.send(embed=em, delete_after=5)

#kick error
@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
     em = discord.Embed(title = "Error", description = "Either you have used the command incorrecly or you dont have permission to use this command.", color = discord.Color.red())
     await ctx.send(embed=em, delete_after=5)

#unban error
@unban.error
async def unban_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):

        em=discord.Embed(title="Error", description="Either you have used the command incorrecly or you dont have permission to use this command or that user is not banned at this server", color=discord.Color.red())

        await ctx.send(embed=em, delete_after=5)
        

#userinfo error
@userinfo.error
async def userinfo_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):

        em = discord.Embed(title = "Error", description = "Please pass all required arguments", color = discord.Color.red())

        await ctx.send(embed=em, delete_after=5)

#define error
@define.error 
async def define_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        em=discord.Embed(title="Error", description="Either you have used the command incorrecly or wikipedia cant find the definitation of that", color=discord.Color.red())
        await ctx.send(embed=em, delete_after=5)

client.run(os.environ['DISCORD_TOKEN'])