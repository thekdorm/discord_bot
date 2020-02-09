import discord
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
from discord.ext import commands
from bot.secrets import token
from bot import linker, hangman_game, overwatch_stats


def get_logfile():
    Path("logs").mkdir(parents=True, exist_ok=True)
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        filename=f'logs/{datetime.now().strftime("%m-%d-%Y-%H%M%S")}.log',
                        level=logging.INFO)

    log = logging.getLogger()
    return log


logger = get_logfile()
description = 'Separate each command argument with an empty space. arg=val in an argument description means that for ' \
              'argument arg, val is the default if none is specified. Values in [] are valid options.\n\n' \
              'Have an idea for a feature I can add? Send it to me with the !idea command!\n' \
              'Developed by: Kyle Dormody'
bot = commands.Bot(command_prefix='!', description=description)
bot.remove_command('help')  # so we can create a custom !help command


@bot.event
async def on_ready():
    print("Logged in!")
    logger.info(f'Logged in as {bot.user.name}!')


@bot.command()
async def help(ctx):
    embed = discord.Embed(title=f'Discord Bot Info', description=description)
    embed.add_field(name='Commands', value='!reddit\n'
                                           '\n'
                                           '\n'
                                           '!idea\n'
                                           '!owstat\n'
                                           '\n'
                                           '!hangman')
    embed.add_field(name='Args', value='subreddit\n'  # !reddit
                                       'mode=top[new, rising, confidential, gilded]\n'
                                       'time=day[all, hour, week, month, year]\n'
                                       'None\n'  # !idea
                                       'player\n'  # !owstat
                                       'role=None[tank, damage, support]\n'
                                       'guess=None')  # !hangman
    embed.add_field(name='Example Usage', value='!reddit aww new\n'
                                                '\n'
                                                '\n'
                                                '!idea [Your idea here]\n'
                                                '!owstat iDelu#1100\n'
                                                '\n'
                                                '!hangman')
    await ctx.send(embed=embed)


@bot.command()
async def idea(ctx):
    logger.critical(f'{ctx.message.author}: {ctx.message.content.lstrip("!idea ")}')
    await ctx.send(f'Thanks for the suggestion!')


@bot.command()
async def owstat(ctx, player, role=None):
    print(f'Args were: player={player}, role={role}')  # For debug, print args to console
    logger.info(f'{ctx.message.author}, owstat: player={player}, role={role}')

    if role:
        result = overwatch_stats.get_player_stats(player, role.lower())
    else:
        result = overwatch_stats.get_player_stats(player)
    if result == 404:
        await ctx.send(f'Bummer, looks like player {player} doesn\'t exist :( '
                       f'make sure spelling and capitalization are correct')
    elif result in [500, 503]:
        await ctx.send("I can't talk to the stats server right now, try again later.")
    else:
        if role and result:
            embed = discord.Embed(title=f'{player}: {role.capitalize()} - {result["level"]} SR')
            embed.set_image(url=result["rankIcon"])
        elif not role and result:
            sr = []
            embed = discord.Embed(title=f'{player} Competitive Stats')
            if len(result) >= 1:
                sr.append(result[0]['level'])
                embed.add_field(name='Role', value=result[0]['role'].capitalize())
                embed.add_field(name='Rank', value=overwatch_stats.get_rank(result[0]['level']))
                embed.add_field(name='SR', value=result[0]['level'])
                if len(result) >= 2:
                    sr.append(result[1]['level'])
                    embed.set_field_at(0, name='Role', value=embed._fields[0]['value'] +
                                                             f'\n{result[1]["role"].capitalize()}')
                    embed.set_field_at(1, name='Rank', value=embed._fields[1]['value'] +
                                                             f'\n{overwatch_stats.get_rank(result[1]["level"])}')
                    embed.set_field_at(2, name='SR', value=embed._fields[2]['value'] +
                                                             f'\n{result[1]["level"]}')
                if len(result) == 3:
                    sr.append(result[2]['level'])
                    embed.set_field_at(0, name='Role', value=embed._fields[0]['value'] +
                                                             f'\n{result[2]["role"].capitalize()}')
                    embed.set_field_at(1, name='Rank', value=embed._fields[1]['value'] +
                                                             f'\n{overwatch_stats.get_rank(result[2]["level"])}')
                    embed.set_field_at(2, name='SR', value=embed._fields[2]['value'] +
                                                           f'\n{result[2]["level"]}')
            embed.set_image(url=result[sr.index(max(sr))]["rankIcon"])
        else:
            logger.error("No stats found.")
            await ctx.send(f'Couldn\'t find stats for {role} for player {player}.')
        if result:
            await ctx.send(embed=embed)

        logger.info(f'Result: {result}')


@bot.command()
async def reddit(ctx, sub, mode='top', time='day'):
    print(f'Args were: sub={sub}, mode={mode}, time={time}')  # For debug, print args to console
    logger.info(f'{ctx.message.author}, reddit: sub={sub}, mode={mode}, time={time}')

    reddit_linker = linker.Linker()
    post = reddit_linker.link_post(sub=sub.lower(), mode=mode.lower(), time_filter=time.lower())

    # Handles text posts, comments and images/GIFs
    if post == '':
        logger.error("Arguments invalid or too many were supplied")
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
    logger.error(f'{error} was raised!')

    if isinstance(error, commands.CommandInvokeError):
        await ctx.send('Oops! Looks like that subreddit might not exist. Check your spelling or try another one.')


class HangmanCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.word = None
        self.places = None
        self.result = None
    # TODO: Add logging here
    @commands.command()
    async def hangman(self, ctx, guess=None):
        print(f'{ctx.message.author}, hangman: guess={guess}')  # For debug, print to console
        logger.info(f'{ctx.message.author}, hangman: guess={guess}')

        if self.word is None:
            self.word = hangman_game.get_hangman_word().lower()
            print(f'Word is {self.word}')
            self.places = '_'*len(self.word)
            await ctx.send(f'{len(self.word)} letters: \n`{" ".join(self.places)}`')
        if self.word and self.places and guess:
            result = hangman_game.check_guess(self.word, guess.lower())
            if result:
                self.places = hangman_game.modify_places(self.places, result, self.word)
                await ctx.send(f'Nice!\n`{" ".join(self.places)}`')
                if '_' not in self.places:
                    self.word = None
                    await ctx.send("You win!")
            else:
                await ctx.send(f'Bummer, that letter isn\'t there :(\n`{" ".join(self.places)}`')


bot.add_cog(HangmanCommand(bot))
bot.run(token)
