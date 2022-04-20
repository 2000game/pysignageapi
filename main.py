import requests
import json

#host = "http://pi:pi@10.10.1.121:3000/api"
host = "10.10.1.121"

class PySigngagePlayer():
    def __init__(self, ip, username, password, port=8000):
        self.host = f"http://{username}:{password}@{ip}:{port}/api"
        self.status = self.get_status()


    def post_call(self, datapoint, body=None):
        r = requests.post(self.host + datapoint, data=body)
        if r.status_code == 200:
            return True
        else:
            raise TypeError

    def get_call(self, datapoint):
        r = requests.get(self.host + datapoint)
        if r.status_code == 200:
            return self.string_to_json(r.text)
        else:
            return

    def string_to_json(self, string):
        return json.loads(string)

    def get_status(self):
        return self.get_call("/status")

    def play_playlist(self, playlist_id):
        self.post_call(f"/play/files/play?file={playlist_id}")

class PySignage():
    def __init__(self, ip, username, password, port=3000):
        self.host = f"http://{username}:{password}@{ip}:{port}/api"
        self.group_names_countdown_only = ['EquipRe', "Wegweiser_Bar_Mitte", "Wegweiser_Bar_Oben", "Wegweiser_Bar_Unten"]
        self.group_names_countdown_and_stream = ['Beamer+', 'EquipLi', 'Strkr22 - Individuel']
        self.playlist_countdown_only_id = "Countdown"
        self.playlist_countdown_and_stream_id = 'Video Anzeigen  Countdown'
        self.playerList = {}
        self.groupList = []
        self.update_playerList()
        self.video_players = []
        self.update_video_players()


    def update_playerList(self):
        reply = self.get_call("/players")
        for i in reply['data']['objects']:
            id = i['_id']
            name = i['name']
            tvStatus = i['tvStatus']
            attributes = i
            device = _device(id, name, tvStatus, attributes)
            self.playerList.update({name: {'id': id, "device_class": device, "group_id": attributes['group']['_id'], "group_name": attributes['group']['name'], "ip": attributes['myIpAddress'].split(' ')[0]}})

    def update_video_players(self):
        for player in self.playerList:
            if self.playerList[player]['group_name'] in self.group_names_countdown_and_stream or self.playerList[player]['group_name'] in self.group_names_countdown_only:
                self.video_players.append(player)

    def get_call(self, datapoint):
        r = requests.get(self.host + datapoint)
        if r.status_code == 200:
            return self.string_to_json(r.text)
        else:
            return


    def post_call(self, datapoint, body=None):
        r = requests.post(self.host + datapoint, data=body)
        if r.status_code == 200:
            return True
        else:
            raise TypeError

    def get_playlists(self):
        return self.get_call("/playlists")

    def string_to_json(self, string):
        return json.loads(string)

    def playlist_once(self, player_id, playlist_id):
        self.post_call(f"/setplaylist/{player_id}/{playlist_id}")

    def forward_playlist(self, player_id):
        self.post_call(f"/playlistmedia/{player_id}/forward")

    def play_stream(self):
        for player_name in self.video_players:
            id = self.playerList[player_name]['id']
            if self.playerList[player_name]['group_name'] in self.group_names_countdown_and_stream:
                self.playlist_once(id, self.playlist_countdown_and_stream_id)
            elif self.playerList[player_name]['group_name'] in self.group_names_countdown_only:
                self.playlist_once(id, self.playlist_countdown_only_id)

    def end_stream(self):
        for player_name in self.video_players:
            id = self.playerList[player_name]['id']
            if self.playerList[player_name]['group_name'] in self.group_names_countdown_and_stream:
                self.forward_playlist(id)

class _group():
    def __init__(self, id, name):
        self.id = id
        self.name = name

class _device():
    def __init__(self, id, name, tvStatus, attributes):
        self.id = id
        self.name = name
        self.tvStatus = tvStatus
        self.group_id = attributes['group']['_id']
        self.group_name = attributes['group']['name']
        self.attributes = attributes

pysignage = PySignage(host, "pi", "pi")

Wegweiser_Bar_unten = PySigngagePlayer('10.10.1.221', "pi", "pi", 8000)
Wegweiser_Bar_unten.play_playlist('Countdown')