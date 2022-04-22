import time

import requests
import json
import threading

#host = "http://pi:pi@10.10.1.121:3000/api"
host = "10.10.1.121"

class PySignageAPI():
    def __init__(self, ip, username, password, port):
        self.host = f"http://{username}:{password}@{ip}:{port}/api"

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

class PySigngagePlayer(PySignageAPI):
    def __init__(self, ip, username, password, port=8000):
        super().__init__(ip, username, password, port)
        self.cd_file_name = "CD 5Min FINAL 20220414.mov"
        self.stream_file_name = "Stream.stream"

        #self.status = self.get_status()

    def get_status(self):
        return self.get_call("/status")

    def play_playlist(self, playlist_id):
        self.post_call(f"/play/files/play?file={playlist_id}")

    def play_file(self, file_id):
        self.post_call(f"/play/files/play?file={file_id}")

    def play_stream(self):
        self.play_file(self.stream_file_name)

    def play_countdown(self):
        self.play_file(self.cd_file_name)

    def forward(self):
        self.post_call("/playlistmedia/forward")



class PySignageServer(PySignageAPI):
    def __init__(self, ip, username, password, port=3000):
        super().__init__(ip, username, password, port)
        self.group_names_countdown_only = ['EquipRe', "Wegweiser_Bar_Mitte", "Wegweiser_Bar_Oben", "Wegweiser_Bar_Unten"]
        self.group_names_countdown_and_stream = ['Beamer+', 'EquipLi']
        self.playlist_countdown_only_id = "Countdown"
        self.playlist_countdown_and_stream_id = 'Video Anzeigen  Countdown'
        self.playerList = {}
        self.groupList = []
        self.update_playerList()
        self.video_players = []
        self.update_video_players()

    class _group():
        def __init__(self, group_id, group_name, group_data):
            self.group_id = group_id
            self.group_name = group_name
            self.group_data = group_data
            self.playlists = []

        def return_scheduled_playlist(self):
            week_day = str((int(time.strftime("%w"))+1)%8)
            month_day = time.strftime("%d")
            time_clock = time.strftime("%H:%M")
            date = time.strftime("%Y-%m-%d")
            self.playlists = self.group_data['data']['deployedPlaylists']


    def get_group_data(self, group_id):
        group_data = self.get_call(f"/groups/{group_id}")
        return group_data

    def update_playerList(self):
        reply = self.get_call("/players")
        for i in reply['data']['objects']:
            id = i['_id']
            name = i['name']
            tvStatus = i['tvStatus']
            attributes = i
            ip = attributes['myIpAddress'].split(' ')[0]
            group_id = attributes['group']['_id']
            group_name = attributes['group']['name']
            group_data = self.get_group_data(group_id)
            #prevent duplicate groups
            self.playerList.update({name: {'id': id, "device_class": PySigngagePlayer(ip, "pi", "pi"), "group_id": group_id, "group_name": group_name, "group_class": self._group(group_id, group_name, group_data), "ip": ip}})

    def update_video_players(self):
        for player in self.playerList:
            if self.playerList[player]['group_name'] in self.group_names_countdown_and_stream or self.playerList[player]['group_name'] in self.group_names_countdown_only:
                self.video_players.append(player)

    def get_playlists(self):
        return self.get_call("/playlists")

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
            if self.playerList[player_name]['group_name'] in self.group_names_countdown_and_stream or self.playerList[player_name]['group_name'] in self.group_names_countdown_only:
                self.forward_playlist(id)

    def start_countdown_thread(self, player_pointer):
        player_pointer.play_countdown()

    def stream_thread(self, player_pointer):
        player_pointer.play_countdown()
        time.sleep(326)
        player_pointer.play_stream()

    def create_threads(self):
        thread_list = []
        for player_name in self.video_players:
            if self.playerList[player_name]['group_name'] in self.group_names_countdown_and_stream:
                thread_list.append(threading.Thread(target=self.stream_thread, args=(self.playerList[player_name]['device_class'],)))
            elif self.playerList[player_name]['group_name'] in self.group_names_countdown_only:
                thread_list.append(threading.Thread(target=self.start_countdown_thread, args=(self.playerList[player_name]['device_class'],)))

        for thread in thread_list:
            thread.start()

pysignageserver = PySignageServer(host, "pi", "pi")
print("Test")
#pysignageserver.play_stream()
#pysignageserver.create_threads()
#pysignageserver.end_stream()

# Wegweiser_Bar_unten = PySigngagePlayer('10.10.1.216', "pi", "pi", 8000)
# Wegweiser_Bar_unten.forward()