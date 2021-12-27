import re
import time

from rcon import Client
from requests import post
from json import load

"""
example rcon.json:
{
    "ip": "127.0.0.1",
    "port": 25575,
    "password": "YourPasswordHere",
    "webhook": "(discord webhook)"
}
omit password field entirely if there is no password
"""
CONFIG_FILE = "rcon.json"
with open(CONFIG_FILE) as f:
    configuration = load(f)

password = configuration['password'] if 'password' in configuration.keys() else None

last_data = {
    "player_count": None,
    "max_players": None,
    "players": None
}

try:
    with Client(configuration['ip'], configuration['port'], passwd=password) as cli:
        while True:
            grab = r'.*?(\d+).*?(\d+).*?: (.*)'
            resp = cli.run('list')
            print(resp)
            player_count, max_players, players = re.search(grab, resp).groups()
            if None in last_data.values():
                r = post(configuration['webhook'], json={
                    "embeds": [
                        {
                            "title": "Connected",
                            "color": 65280,
                            "description": f'{player_count}/{max_players} players online:\n{players}'
                        }
                    ]
                })
                print(f'"Connected" message, {r.status_code}')
            else:
                diff = int(player_count) - int(last_data["player_count"])
                if diff > 0:
                    r = post(configuration['webhook'], json={
                        "embeds": [
                            {
                                "title": f"{diff} player joined",
                                "color": 65280,
                                "description": f'{player_count}/{max_players} players online:\n{players}'
                            }
                        ]
                    })
                    print(f'"Joined" message, {r.status_code}')
                if diff < 0:
                    diff = abs(diff)
                    r = post(configuration['webhook'], json={
                        "embeds": [
                            {
                                "title": f"{diff} player left",
                                "color": 16711680,
                                "description": f'{player_count}/{max_players} players online:\n{players}'
                            }
                        ]
                    })
                    print(f'"Left" message, {r.status_code}')
            last_data["player_count"] = player_count
            last_data["max_players"] = max_players
            last_data["players"] = players
            time.sleep(1)
except KeyboardInterrupt as e:
    r = post(configuration['webhook'], json={
        "embeds": [
            {
                "title": "Stopped",
                "color": 16711680,
                "description": f'The service was manually stopped.'
            }
        ]
    })
    print(f'"Stopped" message, {r.status_code}')
    exit(0)
except:
    r = post(configuration['webhook'], json={
        "embeds": [
            {
                "title": "Crashed",
                "color": 16711680,
                "description": f'The service crashed. Please report this error to penguinencounter#8516.'
            }
        ]
    })
    print(f'"Crashed" message, {r.status_code}')
    exit(1)
