import praw
from secrets import secret, client_id, user_agent


class Linker:
    def __init__(self):
        self.linker = praw.Reddit(client_id=client_id,
                                  client_secret=secret,
                                  user_agent=user_agent)

    # Function to grab top post of specified subreddit. Time filter optional, default to day.
    def link_post(self, sub, mode='top', time_filter='day'):
        if mode == 'top':
            posts = self.linker.subreddit(sub).top(limit=1, time_filter=time_filter)
        elif mode == 'controversial':
            posts = self.linker.subreddit(sub).controversial(limit=1, time_filter=time_filter)
        elif mode == 'new':
            posts = self.linker.subreddit(sub).new(limit=1)
        elif mode == 'rising':
            posts = self.linker.subreddit(sub).rising(limit=1)
        elif mode == 'gilded':
            posts = self.linker.subreddit(sub).gilded(limit=1)
        else:
            posts = ''
            return posts
        for p in posts:
            return p  # couldn't find a better way to do this, return posts will print object reference in memory


if __name__ == '__main__':
    reddit = praw.Reddit(client_id=client_id,
                         client_secret=secret,
                         user_agent=user_agent)

    sub = input("Enter a subreddit:")
    ps = reddit.subreddit(sub).top(limit=1, time_filter='day')
    for s in ps:
        print(s.title)
        print(s.url)
