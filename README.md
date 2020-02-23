# discord_bot
Discord bot for various functionalities. Runs on Windows 10 and Raspbian (Linux distro for Raspberry Pi 3b+). Main functionality is the `!profile` command. The bot maintains an SQL database for each server it is in that keeps track of all users in that server, and can store usernames across all of the major storefronts/game services (Steam, Battle.net, Epic, Origin etc). 

## Setup:

Clone repo to wherever and create a new virtual environment if preferred. Activate venv and install requirements from requirements.txt. The bot requires a few secret tokens that should be placed in bot/secrets.py, `token` and `owner` are for Discord. `token` can be obtained by going to https://discordapp.com/developers/applications/ and creating a new bot. `owner` is for major SQL database modifications such as adding/removing columns. The bot will only carry out some actions if the command comes from the bot owner. `owner` ID can be found by adding the line `print(ctx.message.author.id)` to any of the commands and then calling the command; if you'd like to be the owner, send a command with that line and the bot will print your ID to STDOUT. The bot also needs some stuff for the Reddit API to work: `secret`, `client_id` and `user_agent`, all of which can be obtained by going to https://www.reddit.com/wiki/api and making a new application. MySQL may need some extra care to get installed properly; specifically, I had to download the .whl from https://www.lfd.uci.edu/~gohlke/pythonlibs/#mysqlclient for my Python version on Windows 10 and use `easy_install` in the venv\Scripts directory to get it to install properly. For Raspbian Linux I had to install the following: `sudo apt-get install mysql-server` and `sudo apt-get install libmariadbclient-dev`.

## Commands:

- !help
  - Display help  
- !idea
  - Send the bot owner a message for functionality ideas :)  
- !profile 
  - Functionality to manipulate the server-specific SQL database
    - args=(action [add, get], user=None ['me', other_user], account_type=None [steam, battlenet, origin, epic, activision], account=None)  
- !reddit
  - Reddit API to embed Reddit posts/comments/images/GIFs
    - args=(subreddit, mode=top[new, rising, controversial, gilded], time=day[all, hour, week, month, year])  
- !owstat
  - Overwatch stats API to get competitive rank stats for player
    - args=(player, role=None[tank, damage, support])  
- !hangman 
  - The dankest hangman implementation you'll ever come across, for when you're feeling extra lonely
    - args=(guess)  

## Example Usage:
!profile add me steam TheKDorm  
!profile get me all  
!profile get all all  
!profile add "Kygo Ren" origin MstrDelusiional  

!reddit aww  
!reddit aww controversial  

!owstat iDelu#1100  
!owstat iDelu#1100 tank  
