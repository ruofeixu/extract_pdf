import pgdb
import os
import yaml

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
