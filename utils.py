import pgdb
import os
import yaml
import requests
import time
from requests.adapters import HTTPAdapter
import traceback


class Config:
    print("Load config.yaml.")
    filename = os.path.realpath(__file__)
    dirname = os.path.dirname(filename)
    config_filename = os.path.join(dirname, "config.yaml")
    with open(config_filename) as fp:
        data = yaml.load(fp, Loader=yaml.FullLoader)

    @classmethod
    def get_config(cls):
        return cls.data


config = Config.get_config()

server_config = config['pgdb']['server']
server_conn = pgdb.Connection(
    user=server_config["user"],
    host=server_config["host"],
    port=int(server_config["port"]),
    password=server_config["password"],
    database=server_config["database"],
)

def upload_announcement_to_es(data):
    base_url = config['es_url']
    url = base_url + '/api/announcement/save'
    print(url)
    s = requests.Session()
    s.mount(base_url, HTTPAdapter(max_retries=10))
    while True:
        try:
            response = s.post(url=url, timeout=10, data=data)
            break
        except:
            traceback.print_exc()
            print(data)
            time.sleep(5)
    return response
    