# discord_bot
Discord bot for various functionalities. Runs on Windows 10 and Raspbian (Linux distro for Raspberry Pi 3b+). Main functionality is the `!profile` command. The bot maintains an SQL database for each server it is in that keeps track of all users in that server, and can store usernames across all of the major storefronts/game services (Steam, Battle.net, Epic, Origin etc). 

## SETUP

Clone repo to wherever and create a new virtual environment if preferred. Activate venv and install requirements from requirements.txt. The bot requires a few secret tokens that should be placed in bot/secrets.py, `token` and `owner` are for Discord. `token` can be obtained by going to https://discordapp.com/developers/applications/ and creating a new bot. `owner` is for major SQL database modifications such as adding/removing columns. The bot will only carry out some actions if the command comes from the bot owner. `owner` ID can be found by adding the line `print(ctx.message.author.id)` to any of the commands and then calling the command; if you'd like to be the owner, send a command with that line and the bot will print your ID to STDOUT. The bot also needs some stuff for the Reddit API to work: `secret`, `client_id` and `user_agent`, all of which can be obtained by going to https://www.reddit.com/wiki/api and making a new application. 

## Commands:

!help                    Display help
!idea                    Send the bot owner a message for functionality ideas :)
!profile args=(action [add, get], user=None ['me', other_user], account_type=None [steam, battlenet, origin, epic, activision], account=None)
!reddit args=(subreddit, mode=top[new, rising, controversial, gilded], time=day[all, hour, week, month, year])
!owstat args=(player, role=None[tank, damage, support])
!hangman args=(guess)

## Example Usage:
!profile add me steam TheKDorm
!profile get me all
!profile get all all
!profile add "Kygo Ren" origin MstrDelusiional

!reddit aww
!reddit aww controversial

!owstat iDelu#1100
!owstat iDelu#1100 tank
