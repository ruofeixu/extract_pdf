import json
from datetime import datetime
import traceback
from utils import (
    server_conn,
    upload_regulation_announcement_to_es
)

base_path = '/opt/data01/regulation_announcement_pdf/json/'

def get_announcement_info(year):
    query_str = "select * from ssespider_szsesupervision where publishtime>='{}-01-01' and publishtime<='{}-01-01';"
    query_str = query_str.format(year, year+1)
    announcements = server_conn.query(query_str)
    print(announcements)
    return announcements

def fill_json(announcement):
    publishtime = announcement['publishtime']
    companycode = announcement['companycode']
    companyname = announcement['companyname']
    title = announcement['title']
    url = announcement['url']
    category = announcement['category']
    publishtime = publishtime.strftime('%Y-%m-%d')
    print(publishtime)
    print(title)
    file_name = '{}'.format(
                    title
                )
    json_file_name = '{}{}/{}/{}.json'.format(base_path,publishtime[:4], publishtime[5:],file_name)
    try:
        with open(json_file_name) as json_file:
            data = json.load(json_file)
        data['url'] = url
        data['title'] = title
        data['companycode'] = companycode
        data['category'] = category
        data['publishtime'] = publishtime
        data['companyname'] = companyname
        with open(json_file_name, 'w') as f:
            json.dump(data, f)
        save_es_obj = {
            'companycode': companycode,
            'title': title,
            'url': url,
            'content_json': data['paragraphs'],
            'table_json': data['tables'],
            'publishtime': publishtime,
            'category': category,
            'companyname': companyname
        }
        print('==========')
        print(save_es_obj)
        upload_regulation_announcement_to_es(save_es_obj)
    except:
        traceback.print_exc()
        return False
    return True


def fill_json_data_by_year(year):
    announcements = get_announcement_info(year)
    for announcement in announcements:
        res = fill_json(announcement)

if __name__ == "__main__":
    fill_json_data_by_year(2019)
