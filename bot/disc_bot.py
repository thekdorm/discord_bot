import discord
from datetime import datetime
from discord.ext import commands
from .secrets import TOKEN
from . import linker
from . import hangman_game

log = f'logs/{datetime.now().strftime("%m-%d-%Y-%H%M%S")}.log'
description = 'Separate each command argument with an empty space. arg=val in an argument description means that for ' \
              'argument arg, val is the default if none is specified.\n\n' \
              'Have an idea for a feature I can add? Send it to me with the !idea command!\n' \
              'Developed by: Kyle Dormody'
bot = commands.Bot(command_prefix='!', description=description)
bot.remove_command('help')  # so we can create a custom !help command


@bot.event
async def on_ready():
    with open(log, 'w+') as f:
        f.write(f'Logged in as {bot.user.name}\n------\n')


@bot.command()
async def help(ctx):
    embed = discord.Embed(title=f'Discord Bot Info', description=description)
    embed.add_field(name='Commands', value='!reddit\n'
                                           '\n'
                                           '\n'
                                           '!idea', inline=True)
    embed.add_field(name='Args', value='subreddit\n'
                                       'mode=top[new, rising, confidential, gilded]\n'
                                       'time=day[all, hour, week, month, year]\n'
                                       'None', inline=True)
    embed.add_field(name='Example Usage', value='!reddit aww new\n'
                                                '\n'
                                                '\n'
                                                '!idea [Your idea here]', inline=True)
    await ctx.send(embed=embed)


@bot.command()
async def idea(ctx):
    with open(log, 'a') as f:
        f.write(f'{ctx.message.author}: {ctx.message.content.lstrip("!idea ")}\n')
    await ctx.send(f'Thanks for the suggestion!')


@bot.command()
async def reddit(ctx, sub, mode='top', time='day'):
    print(f'Args were: sub={sub}, mode={mode}, time={time}')  # For debug, print args to console

    reddit_linker = linker.Linker()
    post = reddit_linker.link_post(sub=sub, mode=mode, time_filter=time)

    # Handles text posts, comments and images/GIFs
    if post == '':
        await ctx.send('Arguments are invalid or too many were supplied.')
        raise commands.BadArgument(message='Exception: BadArgument: Mode argument not provided or can\'t be parsed.')
    else:
        if post.__class__.__name__ == 'Comment':
            embed = discord.Embed(title=f'{post.author} in /r/{sub} on {post.submission.title}',
                                  url=f'https://reddit.com/r/{sub}/'
                                      f'{post.submission.id}/'
                                      f'{post.submission.title.replace(" ", "_")}/'
                                      f'{post.id}/')
            embed.add_field(name='Karma', value=post.score, inline=True)
            embed.add_field(name='Comment Body', value=post.body)
        elif post.is_self:
            embed = discord.Embed(title=post.title, url=post.url)
            embed.add_field(name='Karma', value=post.score)
            if len(post.selftext) <= 1024:
                embed.add_field(name='Text Post', value=post.selftext)
            else:
                embed.add_field(name='Text Post, Part 1', value=post.selftext[:1023])
        else:
            embed = discord.Embed(title=post.title, url=post.url)
            embed.set_image(url=post.url)
        await ctx.send(embed=embed)


@reddit.error
async def reddit_error(ctx, error):
    print(error)  # For debug, print exception to console

    if isinstance(error, commands.CommandInvokeError):
        await ctx.send('Oops! Looks like that subreddit might not exist. Check your spelling or try another one.')


class HangmanCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.word = None
        self.places = None
        self.result = None

    @commands.command()
    async def hangman(self, ctx, guess=None):
        if guess is None:
            self.word = hangman_game.get_hangman_word().lower()
            print(self.word)
            self.places = '_'*len(self.word)
            await ctx.send(f'{len(self.word)} letters: \n`{" ".join(self.places)}`')
        print(f'Word is {self.word}, guess was {guess}')
        if self.word and self.places and guess:
            result = hangman_game.check_guess(self.word, guess)
            if result:
                self.places = hangman_game.modify_places(self.places, result, self.word)
                await ctx.send(f'Nice!\n`{" ".join(self.places)}`')
            else:
                await ctx.send(f'Bummer, that letter isn\'t there :(\n`{" ".join(self.places)}`')


bot.add_cog(HangmanCommand(bot))
bot.run(TOKEN)
