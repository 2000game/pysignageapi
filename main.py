import requests
import json
host = "http://pi:pi@10.10.1.121:3000/api"


def getcall(datapoint):
    r = requests.get(host + datapoint)
    if r.status_code == 200:
        return convert_string_to_json(r.text)
    else:
        return

def postcall(datapoint, body=None):
    r = requests.post(host + datapoint, data=body)
    if r.status_code == 200:
        return True
    else:
        raise TypeError

def convert_string_to_json(string):
    return json.loads(string)

def set_tv_status(id, state):
    if state == 'false':
        postcall("/pitv/"+ id, {"status": state})
    else:
        postcall("/pitv/" + id, json.dumps({"status": state}))

tvlist = []

def update_tv_list():
    reply = getcall("/players")


    for i in reply['data']['objects']:
        id = i['_id']
        name = i['name']
        status = i['tvStatus']
        tvlist.append({"id": id, "name": name, "status": status})


def update_tv(id):
    reply = getcall(f"/players/{id}")
    for i in tvlist:
        if i['id'] == id:
            index = tvlist.index(i)
    id = reply['data']['_id']
    name = reply['data']['name']
    status = reply['data']['tvStatus']
    dic = {"id": id, "name": name, "status": status}
    tvlist[index] = dic
    return dic


def turnalloff(tvlist):
    for i in tvlist:
        set_tv_status(i['id'], 'false')

def turnallon(tvlist):
    for i in tvlist:
        set_tv_status(i['id'], 'true')
update_tv_list()

#turnalloff(tvlist)
#turnallon(tvlist)
update_tv('5f52a141926b040819e9e037')
#update_tv_list()
print("Z")
