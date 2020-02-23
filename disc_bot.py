import os
import discord
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
from discord.ext import commands
from bot.secrets import token, owner
from bot import linker, hangman_game, overwatch_stats
from db import sql_external_profiles


def get_logfile():  # make logfile for debug purposes
    Path("logs").mkdir(parents=True, exist_ok=True)
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        filename=f'logs/{datetime.now().strftime("%m-%d-%Y-%H%M%S")}.log',
                        level=logging.INFO)

    log = logging.getLogger()
    return log


def create_db():  # create new SQL db for each server the bot connects IF db doesn't exist on startup; else do nothing
    Path("db").mkdir(parents=True, exist_ok=True)
    for guild in bot.guilds:
        db = f'db/{guild}-{guild.id}.db'
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), db)
        result = sql_external_profiles.create_db(db_path)  # create the server-specific db if it doesn't exist already
        if result == 1:
            logger.info(f'DB created successfully: {db}')
        elif result == 0:
            logger.info(f'{db} already exists, continuing...')
        for member in guild.members:
            if not member.bot:  # only add non-bot users to db
                sql_external_profiles.add_user(db_path, member.name)


logger = get_logfile()
description = 'Separate each command argument with an empty space. arg=val in an argument description means that for ' \
              'argument arg, val is the default if none is specified. Values in [] are valid options.\n\n' \
              'Have an idea for a feature I can add? Send it to me with the !idea command!\n' \
              'Developed by: Kyle Dormody'
bot = commands.Bot(command_prefix='!', description=description)
bot.remove_command('help')  # so we can create a custom !help command


@bot.event  # do all this stuff when bot connects successfully
async def on_ready():
    bot.owner_id = owner
    print(f'Logged in as {bot.user.name}!')
    logger.info(f'Logged in as {bot.user.name}!')
    create_db()


@bot.command()
async def help(ctx):  # custom !help command for all bot features
    embed = discord.Embed(title=f'Discord Bot Info', description=description)
    embed.add_field(name='Commands', value='!reddit\n'
                                           '\n'
                                           '\n'
                                           '!idea\n'
                                           '!owstat\n'
                                           '\n'
                                           '!profile\n'
                                           '\n'
                                           '\n'
                                           '\n'
                                           '!hangman')
    embed.add_field(name='Args', value='subreddit\n'  # !reddit
                                       'mode=top[new, rising, confidential, gilded]\n'
                                       'time=day[all, hour, week, month, year]\n'
                                       'None\n'  # !idea
                                       'player\n'  # !owstat
                                       'role=None[tank, damage, support]\n'
                                       'action [add, get]\n'  # !profile
                                       'user=None (defaults to yourself) ["me", other_user]\n'
                                       'account_type=None [steam, battlenet, origin, epic, activision, etc]\n'
                                       'account=None (this is where you\'d specifiy the account name\n'
                                       'guess=None')  # !hangman
    embed.add_field(name='Example Usage', value='!reddit aww new\n'
                                                '\n'
                                                '\n'
                                                '!idea [Your idea here]\n'
                                                '!owstat iDelu#1100\n'
                                                '\n'
                                                '!profile add me\n'
                                                '!profile add me steam TheKDorm\n'
                                                '!profile get all all\n'
                                                '!profile get "Kygo Ren" all\n'
                                                '!hangman')
    await ctx.send(embed=embed)


@bot.command()
async def idea(ctx):  # !idea command for users to send me bot functionality ideas
    logger.critical(f'{ctx.message.author}: {ctx.message.content.lstrip("!idea ")}')
    await ctx.send(f'Thanks for the suggestion!')


@bot.command()
async def owstat(ctx, player, role=None):  # !owstat, gets Overwatch competitive stats for player
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
async def reddit(ctx, sub, mode='top', time='day'):  # !reddit, grabs top subreddit post and formats
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
async def reddit_error(ctx, error):  # !reddit error handling
    print(error)  # For debug, print exception to console
    logger.error(f'{error} was raised!')

    if isinstance(error, commands.CommandInvokeError):
        await ctx.send('Oops! Looks like that subreddit might not exist. Check your spelling or try another one.')


@bot.command()
async def profile(ctx, action, user=None, account_type=None, account=None):  # SQL db stuff for !profile
    Path("db").mkdir(parents=True, exist_ok=True)
    db = f'db/{ctx.guild}-{ctx.guild.id}.db'
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), db)
    logger.info(f'{ctx.message.author}, profile: db={db_path}, user={user}, action={action}, '
                f'account={account}, account_type={account_type}')

    if not user or user.lower() == 'me':
        user = ctx.message.author.name  # user is whoever used the command for cleanliness; 'me' easy to write
    print(f'action={action}, user={user}, type={account_type}, account={account}')  # For debug

    if action.lower() == 'add':
        if not account_type and not account:  # just add a user to db
            sql_external_profiles.add_user(db_path, user)
            logger.info(f'Added {user} to {db_path}')
            await ctx.send(f'Added {user} to db')

        else:  # add specified account to user
            result = sql_external_profiles.modify_user(db_path, user, column=account_type.lower(), value=account)
            if result == 0:
                logger.info(f'{user} not in database!')
                await ctx.send(f'{user} not in database!')
            elif result == 1:
                logger.info(f'Modified {user}: {account_type}-{account}')
                await ctx.send(f'Modified {user}: {account_type}-{account}')
            else:
                logger.info('Unknown error occurred.')
                await ctx.send('Unknown error occurred.')

    elif action.lower() == 'get':
        columns = sql_external_profiles.get_columns(db_path, 'users')  # get column names of db for embed and debug

        if user is not ctx.message.author.name and user.lower() == 'all' and account_type == 'all':  # get all
            result = sql_external_profiles.get_record(db_path)
            embed = discord.Embed(title='All accounts for all server members')
            for column in columns:
                value = ''
                for res in result:
                    value = value + res[columns.index(column)] + '\n'
                embed.add_field(name=column.capitalize(), value=value)
            logger.info(f'Get result: {result}')

        elif account_type and account_type == 'all':  # get all accounts for user
            result = sql_external_profiles.get_record(db_path, user, account_type)
            embed = discord.Embed(title=f'All accounts for user {user}')
            for column in columns:
                embed.add_field(name=column.capitalize(), value=result[0][columns.index(column)])
            logger.info(f'Get result: {result}')

        else:  # get specified account for user
            if account_type is None:
                account_type = 'all'
            result = sql_external_profiles.get_record(db_path, user, account_type)
            embed = discord.Embed(title=f'{account_type.capitalize()} account for user {user}')
            embed.add_field(name=account_type.capitalize(), value=result[0][0])
            logger.info(f'Get result: {result[0][0]}')

        await ctx.send(embed=embed)

    elif action.lower() == 'delete':  # reserved for bot.owner, deletes user from db
        if ctx.message.author.id == bot.owner_id:
            sql_external_profiles.delete_user(db_path, user)
            logger.info(f'Deleted entries for user {user}.')
            await ctx.send(f'Deleted entries for user {user}.')
        else:
            logger.info(f'Unauthorized user {user} for this action, aborting.')
            await ctx.send(f'Unauthorized user {user} for this action, aborting.')

    elif action.lower() == 'add_column':  # reserved for bot.owner, adds new column to db
        if ctx.message.author.id == bot.owner_id:
            sql_external_profiles.modify_column(db_path, 'add', user)
            logger.info(f'Added column {user}.')
            await ctx.send(f'Added column {user}.')
        else:
            logger.info(f'Unauthorized user {user} for this action, aborting.')
            await ctx.send(f'Unauthorized user {user} for this action, aborting.')

    elif action.lower() == 'drop_column':  # reserved for bot.owner, drops column from db
        if ctx.message.author.id == bot.owner_id:
            sql_external_profiles.modify_column(db_path, 'drop', user)
            logger.info(f'Dropped column {user}.')  # use user here cus it's reserved and this is easiest way
            await ctx.send(f'Dropped column {user}.')  # use user here cus it's reserved and this is easiest way
        else:
            logger.info(f'Unauthorized user {user} for this action, aborting.')
            await ctx.send(f'Unauthorized user {user} for this action, aborting.')

    else:
        logger.error(f'Action argument not recognized: {action}')
        await ctx.send(f'Action argument not recognized: {action}. Valid options are: add, get')


@profile.error
async def profile_error(ctx, error):  # !profile error handling
    print(error)  # For debug, print exception to console
    logger.error(f'{error} was raised!')

    await ctx.send('Invalid combination of arguments. Try again or look at !help.')


# TODO: Make DB stuff its own class???


class HangmanCommand(commands.Cog):  # !hangman game class, class allows us to preserve word between guesses
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
