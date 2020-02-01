import discord
from discord.ext import commands
from secrets import TOKEN
import linker

description = 'Separate each command argument with an empty space. arg=val in an argument description means that for ' \
              'argument arg, val is the default if none is specified.'
bot = commands.Bot(command_prefix='!', description=description)
bot.remove_command('help')


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}\n------')


@bot.command()
async def help(ctx):
    embed = discord.Embed(title=f'Discord Bot Info', description=description)
    embed.add_field(name='Commands', value='!reddit', inline=True)
    embed.add_field(name='Args', value='subreddit, mode=top, time=day', inline=True)
    embed.add_field(name='Example Usage', value='!reddit aww new', inline=True)
    await ctx.send(embed=embed)


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


bot.run(TOKEN)
