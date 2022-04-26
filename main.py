import time


import threading
from datetimerange import DateTimeRange
import datetime
from PySignageRequestAPI import PySignageAPI
from PyPlayerAPI import PySigngagePlayer

host = "10.10.1.121"


class PySignageServer(PySignageAPI):
    def __init__(self, ip, username, password, port=3000):
        super().__init__(ip, username, password, port)
        self.stream_thread_list = None
        self.countdown_thread_list = None
        self.stream_only_thread_list = None
        self.countdown_only_thread_list = None
        self.group_names_countdown_only = ['EquipRe', "Wegweiser_Bar_Mitte", "Wegweiser_Bar_Oben", "Wegweiser_Bar_Unten"]
        self.group_names_countdown_and_stream = ['Beamer+', 'EquipLi']
        self.playlist_countdown_only_id = "Countdown"
        self.playlist_countdown_and_stream_id = 'Video Anzeigen Countdown'
        self.playlists = []
        self.device_dict = {}
        self.group_dict = {}
        self.refresh_data()

    class _group():
        def __init__(self, group_id, group_name, group_data):
            self.group_id = group_id
            self.group_name = group_name
            self.group_data = group_data
            self.playlists = []
            self.last_deploy_timestamp = int(group_data['lastDeployed'])
            self.refresh_playlists()

        def refresh_playlists(self):
            self.playlists = self.group_data['deployedPlaylists']

        def return_scheduled_playlist(self):
            week_day = (int(time.strftime("%w"))+1)%8
            month_day = int(time.strftime("%d"))
            current_time = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+0100")
            default_playlist = self.playlists[0]
            possible_playlists = []
            for playlist in self.playlists[1:]:
                if playlist['plType'] != "regular":
                    continue
                settings = playlist['settings']
                if settings['timeEnable']:
                    if week_day in settings['weekdays']:
                        if month_day in settings['monthdays']:
                            if 'startdate' in settings:
                                startdate = settings['startdate'][:19]+ "+0000"
                                enddate = settings['enddate'][:19]+"+0000"
                                starttime = settings['starttimeObj'][10:19] + "+0000"
                                endtime = settings['endtimeObj'][10:19] + "+0000"
                                time_range = DateTimeRange(starttime, endtime)
                                date_range = DateTimeRange(startdate, enddate)
                                if current_time in time_range and current_time in date_range:
                                    possible_playlists.append(playlist)
                            else:
                                starttime = settings['starttime']
                                endtime = settings['endtime']
                                time_now = datetime.datetime.now()
                                starttime = time_now.replace(hour=int(starttime[:2]), minute=int(starttime[3:5]), second=0, microsecond=0)
                                endtime = time_now.replace(hour=int(endtime[:2]), minute=int(endtime[3:5]), second=0, microsecond=0)
                                if time_now >= starttime and time_now <= endtime:
                                    possible_playlists.append(playlist)

            if len(possible_playlists) == 0:
                return default_playlist
            elif len(possible_playlists) == 1:
                return possible_playlists[0]
            else:
                closest_start_time = None
                for playlist in possible_playlists:
                    settings = playlist['settings']
                    if "starttime" in settings:
                        if closest_start_time is None:
                            closest_start_time = settings['starttime']
                        else:
                            starttime = settings['starttime']
                            time_now = datetime.datetime.now()
                            closest_time =  time_now.replace(hour=int(closest_start_time[:2]), minute=int(closest_start_time[3:5]), second=0, microsecond=0)
                            starttime = time_now.replace(hour=int(starttime[:2]), minute=int(starttime[3:5]), second=0, microsecond=0)
                            if starttime > closest_time:
                                closest_start_time = settings['starttime']
            return next(playlist for playlist in possible_playlists if playlist['settings']['starttime'] == closest_start_time)



    class _device():
        def __init__(self, id, name, ip, player_class, group_id, group_pointer, device_data):
            self.id = id
            self.name = name
            self.ip = ip
            self.player_class = player_class
            self.group_id = group_id
            self.group_pointer = group_pointer
            self.device_data = device_data
            self.active_playlist = device_data['currentPlaylist']

    def deploy(self, group_pointer):
        timestamp = int(datetime.datetime.now().timestamp()*1000)
        if group_pointer.last_deploy_timestamp in range(group_pointer.last_deploy_timestamp - 10, timestamp):
            body = {"deploy": True, "exportAssets": False, "_id": group_pointer.group_id, "name": group_pointer.group_name}
            self.post_call(f"/groups/{group_pointer.group_id}", body)
            group_pointer.last_deployed_timestamp = timestamp

    def get_group_data(self, group_id):
        group_data = self.PySignageServer.get_call(f"/groups/{group_id}")
        return group_data

    def deploy_all_groups(self):
        for group in self.group_dict.values():
            self.deploy(group)


    def refresh_data(self):
        self.refresh_group_dict()
        self.refresh_device_dict()
        self.refresh_playlists()
        self.create_threads()

    def refresh_group_dict(self):
        self.group_dict = {}
        for group in self.get_call("/groups")['data']:
            if group['name'] == 'default':
                continue
            group_object = self._group(group['_id'], group['name'], group)
            self.group_dict.update({group['_id']: group_object})

    def refresh_device_dict(self):
        self.device_dict = {}
        for device in self.get_call("/players")['data']["objects"]:
            id = device['_id']
            name = device['name']
            ip = device['myIpAddress'].split(" ")[0]
            player_class = PySigngagePlayer(ip, 'pi', 'pi')
            group_id = device['group']['_id']
            group_pointer = self.group_dict[group_id]
            device_class = self._device(id, name, ip, player_class, group_id, group_pointer, device)
            self.device_dict.update({id: {"name": name, "device_class": device_class, "group_id": group_id, "group_pointer": group_pointer, "player_class": player_class}})

    def refresh_playlists(self):
        for group in self.group_dict.values():
            for playlist in group.group_data['playlists']:
                playlist_name = playlist['name']
                if playlist_name not in self.playlists:
                    self.playlists.append(playlist_name)

    def play_playlist_on_all_devices(self, playlist_name):
        for device in self.device_dict.values():
            playlists = self.return_group_playlist_names(device['group_id'])
            if playlist_name in playlists:
                device['device_class'].player_class.play_playlist(playlist_name)

    def return_group_playlist_names(self, group_id):
        playlist_names = []
        for playlist in self.group_dict[group_id].group_data['deployedPlaylists']:
            playlist_names.append(playlist['name'])
        return playlist_names

    def forward_playlist(self, player_id):
        self.post_call(f"/playlistmedia/{player_id}/forward")

    def return_to_scheduled_playlists(self):
        self.refresh_data()
        for device in self.device_dict.values():
            scheduled_playlist = device['group_pointer'].return_scheduled_playlist()['name']
            if device['device_class'].active_playlist != scheduled_playlist:
                device['player_class'].play_playlist(scheduled_playlist)
            # if self.playlist_countdown_and_stream_id in device['group_pointer']['playlists']:
            #     playlist = device['group_pointer'].return_scheduled_playlist()
            #     device['player_class'].play_playlist(playlist['name'])

    def countdown_thread(self, device_class):
        player_class = device_class.player_class
        player_class.play_countdown()
        time.sleep(10)
        group_pointer = device_class.group_pointer
        self.deploy(group_pointer)

    def countdown_file_thread(self, device_class):
        #remove deploy only do forward only play files not playlists
        player_class = device_class.player_class
        player_class.play_cd_only()
        time.sleep(326)
        group_pointer = device_class.group_pointer
        #self.deploy(group_pointer)
        player_class.forward()

    def stream_thread(self, player_pointer):
        player_pointer.play_cd_stream()

    def stream_only_thread(self, player_pointer):
        player_pointer.play_stream_only()

    def create_threads(self):
        stream_thread_list = []
        countdown_thread_list = []
        stream_only_thread_list = []
        countdown_only_thread_list = []
        for device in self.device_dict.values():
            device_playlists = device['group_pointer'].group_data['playlists']
            for playlist in device_playlists:
                name = playlist['name']
                if name == self.playlist_countdown_and_stream_id:
                    stream_thread_list.append(threading.Thread(target=self.stream_thread, args=(device['player_class'],)))
                    stream_only_thread_list.append(threading.Thread(target=self.stream_only_thread, args=(device['player_class'],)))
                    countdown_only_thread_list.append(threading.Thread(target=self.countdown_file_thread, args=(device['device_class'],)))
                elif name == self.playlist_countdown_only_id:
                    countdown_thread_list.append(threading.Thread(target=self.countdown_thread, args=(device['device_class'],)))
                    countdown_only_thread_list.append(threading.Thread(target=self.countdown_file_thread, args=(device['device_class'],)))
        self.stream_thread_list = stream_thread_list
        self.countdown_thread_list = countdown_thread_list
        self.stream_only_thread_list = stream_only_thread_list
        self.countdown_only_thread_list = countdown_only_thread_list

    def start_countdown(self):
        thread_list = self.stream_thread_list + self.countdown_thread_list
        for thread in thread_list:
            thread.start()

    def play_stream_only(self):
        for thread in self.stream_only_thread_list:
            thread.start()

    def play_countdown_only(self):
        for thread in self.countdown_only_thread_list:
            thread.start()

    def end_stream(self):
        for group in self.group_dict.values():
            playlists = self.return_group_playlist_names(group.group_id)
            if self.playlist_countdown_and_stream_id in playlists:
                self.deploy(group)

    def get_screens(self):
        return self.get_call("/players")

    def return_scheduled_playlist(self):
        return self.playlists


pysignageserver = PySignageServer(host, "pi", "pi")

#pysignageserver.deploy_all_groups()
#pysignageserver.start_countdown()
#pysignageserver.play_stream_only()
#pysignageserver.end_stream()
pysignageserver.play_countdown_only()