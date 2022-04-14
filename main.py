import requests
import json

host = "http://pi:pi@10.10.1.121:3000/api"


class PySignage():
    def __init__(self, host):
        self.host = host
        self.playerList = []
        self.update_playerList()

    def update_playerList(self):
        reply = self.get_call("/players")
        for i in reply['data']['objects']:
            id = i['_id']
            name = i['name']
            tvStatus = i['tvStatus']
            attributes = i
            device = _device(id, name, tvStatus, attributes)
            self.playerList.append(device)


    def update_tv_list(self):
        reply = self.get_call("/players")

        for i in reply['data']['objects']:
            id = i['_id']
            name = i['name']
            status = i['tvStatus']
            self.playerList.append({"id": id, "name": name, "status": status})

    def get_call(self, datapoint):
        r = requests.get(host + datapoint)
        if r.status_code == 200:
            return self.string_to_json(r.text)
        else:
            return


    def post_call(self, datapoint, body=None):
        r = requests.post(host + datapoint, data=body)
        if r.status_code == 200:
            return True
        else:
            raise TypeError


    def string_to_json(self, string):
        return json.loads(string)


class _device():
    def __init__(self, id, name, tvStatus, attributes):
        self.id = id
        self.name = name
        self.tvStatus = tvStatus
        self.attributes = attributes










# def update_tv(id):
#     reply = getcall(f"/players/{id}")
#     for i in tvlist:
#         if i['id'] == id:
#             index = tvlist.index(i)
#     id = reply['data']['_id']
#     name = reply['data']['name']
#     status = reply['data']['tvStatus']
#     dic = {"id": id, "name": name, "status": status}
#     tvlist[index] = dic
#     return dic
#
#
# def turnalloff(tvlist):
#     for i in tvlist:
#         set_tv_status(i['id'], 'false')
#
#
# def turnallon(tvlist):
#     for i in tvlist:
#         set_tv_status(i['id'], 'true')

PySignage = PySignage(host)
print("Test")