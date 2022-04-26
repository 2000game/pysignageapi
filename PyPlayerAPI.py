from PySignageRequestAPI import PySignageAPI
class PySigngagePlayer(PySignageAPI):
    def __init__(self, ip, username, password, port=8000):
        super().__init__(ip, username, password, port)
        self.cd_file_name = "CD 5Min FINAL 20220414.mov"
        self.stream_file_name = "Stream.stream"
        self.stream_cd_playlist_name = 'Video Anzeigen Countdown'
        self.cd_playlist_name = 'Countdown'

        #self.status = self.get_status()

    def get_status(self):
        return self.get_call("/status")

    def play_playlist(self, playlist_id):
        body = {"play": True}
        self.post_call(f"/play/playlists/{playlist_id}", body)

    def play_file(self, file_id):
        self.post_call(f"/play/files/play?file={file_id}")

    def play_cd_stream(self):
        #self.play_file(self.stream_file_name)
        self.play_playlist(self.stream_cd_playlist_name)

    def play_stream_only(self):
        self.play_file(self.stream_file_name)

    def play_cd_only(self):
        self.play_file(self.cd_file_name)

    def play_countdown(self):
        #self.play_file(self.cd_file_name)
        self.play_playlist(self.cd_playlist_name)

    def forward(self):
        self.post_call("/playlistmedia/forward")