import json
from utils import (
    server_conn
)

base_path = ''

def get_announcement_info(year):
    query_str = "select * from cninfo_companyreport where publishtime >　'{}-01-01' and publishtime < {}-01-01;"
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

    print(publishtime)

    file_name = '[{}][{}][{}]'.format(
                    publishtime,
                    meta['secName'],
                    title
                )


def fill_json_data_by_year(year):
    announcements = get_announcement_info(year)
    for announcement in announcements:
        fill_json(announcement)
        break

if __name__ == "__main__":