import json
from datetime import datetime
import traceback
from utils import (
    server_conn
)

base_path = '/opt/data/company_announcement_pdf/json/'

def get_announcement_info(year):
    query_str = "select * from cninfo_companyreport where publishtime>='{}-01-01' and publishtime<='{}-01-01';"
    query_str = query_str.format(year, year+1)
    announcements = server_conn.query(query_str)
    return announcements

def fill_json(announcement):
    publishtime = announcement['publishtime']
    companycode = announcement['companycode']
    title = announcement['title']
    url = announcement['url']
    report_type = announcement['report_type']
    market_type = announcement['market_type']
    meta = json.loads(announcement['meta'])
    publishtime = publishtime.strftime('%Y-%m-%d')
    print(publishtime)
    print(title)
    print(meta['secName'])
    file_name = '[{}][{}][{}]'.format(
                    publishtime,
                    meta['secName'],
                    title
                )
    json_file_name = '{}{}/{}.json'.format(base_path,publishtime,file_name)
    flag=False
    try:
        with open(json_file_name) as json_file:
            data = json.load(json_file)
        data['url'] = url
        data['title'] = title
        data['meta'] = meta
        data['martket_type'] = market_type
        data['companycode'] = companycode
        with open(json_file_name, 'w') as f:
            json.dump(data, f)
        flag=True
    except:
        traceback.print_exc()
    return flag


def fill_json_data_by_year(year):
    announcements = get_announcement_info(year)
    for announcement in announcements:
        flag = fill_json(announcement)

if __name__ == "__main__":
    fill_json_data_by_year(2019)
