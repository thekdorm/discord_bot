import requests


def get_player_stats(player, role=None):
    if role:
        role = role.lower()
    query = requests.get(f'https://ow-api.com/v1/stats/pc/us/{player.replace("#", "-")}/profile')

    if query.status_code == 200:
        if role:
            for i in range(len(query.json()['ratings'])):
                if query.json()['ratings'][i]['role'] == role:
                    return query.json()['ratings'][i]
                return None

        else:
            return query.json()["ratings"]

    elif query.status_code in [404, 500, 503]:
        return query.status_code


def get_rank(sr):
    if 0 <= sr <= 1499:
        return 'Bronze'

    elif 1500 <= sr <= 1999:
        return 'Silver'

    elif 2000 <= sr <= 2499:
        return 'Gold'

    elif 2500 <= sr <= 2999:
        return 'Platinum'

    elif 3000 <= sr <= 3499:
        return 'Diamond'

    elif 3500 <= sr <= 3999:
        return 'Masters'

    elif 4000 <= sr <= 500:
        return 'Grandmaster'
