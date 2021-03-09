import requests
import json
import re
import os
import argparse
import datetime
import zipfile
import gzip
import shutil

from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

COMPRESSED_DATA_PATH = "./compressed"
UNCOMPRESSED_DATA_PATH = "./data"

PUBLISH_PRICES_INTEGRATION_TEMPLATE = {
    'username': 'RamiLevi',
    'password': '',
    'online_store_id':39,
    'url': 'https://url.retail.publishedprices.co.il/file',
    'login_post_url': 'https://url.retail.publishedprices.co.il/login/user',
    'files_directory_url': 'https://url.retail.publishedprices.co.il/file/d',
    'files_search_url': 'https://url.retail.publishedprices.co.il/file/ajax_dir',
    'files_search_request_data': {'sEcho': 6,
        'sColumns': ',,,,', 
        'iDisplayLength': 100000,
        'mDataProp_0': 'fname', 
        'sSearch_0': '',
        'bRegex_0': 'false',
        'bSearchable_0': 'true', 
        'bSortable_0': 'true',
        'mDataProp_1': 'type',
        'sSearch_1': '',
        'bRegex_1': 'false',
        'bSearchable_1': 'true',
        'bSortable_1': 'false',  
        'mDataProp_2': 'size',
        'sSearch_2': '',    
        'bRegex_2': 'false',       
        'bSearchable_2': 'true',
        'bSortable_2': 'true',
        'mDataProp_3': 'ftime',
        'sSearch_3': '',
        'bRegex_3': 'false',
        'bSearchable_3': 'true',
        'bSortable_3': 'true',  
        'mDataProp_4': '',
        'sSearch_4': '',
        'bRegex_4': 'false',
        'bSearchable_4': 'true',
        'bSortable_4': 'false',
        'sSearch': '',
        'bRegex': 'false',
        'iSortingCols': 0,
        'cd': '/'}
}

CHAIN_DATA = {'rami_levi': {**PUBLISH_PRICES_INTEGRATION_TEMPLATE,
    'username': 'RamiLevi',
    'online_store_id':39,
    },
    'keshet_teamim': {**PUBLISH_PRICES_INTEGRATION_TEMPLATE,
        'username': 'Keshet',
        'online_store_id': 518
    },
    'osher_ad': {**PUBLISH_PRICES_INTEGRATION_TEMPLATE,
    'username': 'osherad',
    'online_store_id': 10,
    },
    'shufersal': {
        'files_search_url': 'http://prices.shufersal.co.il/FileObject/UpdateCategory?catID=2&storeId=',
        'online_store_id': 413 
    },
    'victory': {
        'files_search_url': 'http://matrixcatalog.co.il/NBCompetitionRegulations.aspx?fileType=pricefull&code=%s',
        'files_directory_url': 'http://matrixcatalog.co.il',
        'files_search_post_request': {
            'ctl00$MainContent$fileType': 'pricefull',
            'ctl00$MainContent$chain': '7290696200003',
            'ctl00$MainContent$subChain': '-1',
            'ctl00$MainContent$txtDate': datetime.datetime.now().strftime('%d/%m/%Y'),
            'ctl00$MainContent$branch' : '7290696200003001097',
            'ctl00$MainContent$btnSearch': 'חיפוש',
            'ctl00$TextArea': '',
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': ''
            },
        'chain_id': '7290696200003',
        'online_store_id': '7290696200003001097',
        'file_type': 'pricefull'
    },
    'mega': {
            'files_search_url': 'http://publishprice.mega.co.il',
            'files_directory_url': 'http://publishprice.mega.co.il',
            'online_store_id': '9090'
    }
}


def new_session(auth=False, chain_data=None):
    session = requests.session()
    
    if auth:
        authenticate_cerberus_web_client(session, chain_data['url'], chain_data['login_post_url'], chain_data['username'], chain_data["password"])
    return session

def authenticate_cerberus_web_client(session, url, post_login_url, username, password="", verify=False):
    login_html = session.get(url, verify=verify)
    auth_payload = {"username": username, "password": password,"Sumbit": "Sign in"}
    soup = BeautifulSoup(login_html.content, "html.parser")

    try:		
        csrf_value = soup.find('input', {'id': 'csrftoken'}).get('value')
    except:
        print("[!] Error while trying to grab csrftoker hidden input")
    auth_payload["csrf_token"] = csrf_value

    login_html = session.post(post_login_url, verify=False, data=auth_payload)
    return session


def get_full_price_file_name(session, chain_data, store_id=None):
    chain_data['files_search_request_data']['sSearch'] = store_id if store_id else chain_data['online_store_id']
    req_data = session.post(chain_data['files_search_url'], verify=False, data=chain_data['files_search_request_data'])

    files = json.loads(req_data.content)
    for f in files['aaData']:
        if re.search('pricefull', f['DT_RowId'], re.IGNORECASE):
            return f['DT_RowId']
    

    raise 'full price file name not detected'


def download_file(download_link, file_name, session):
    path = '%s/%s' % (COMPRESSED_DATA_PATH, file_name) 
    r = session.get(download_link)
    open(path, 'wb').write(r.content)


def unzip_zip(file_name):
    with zipfile.ZipFile("%s/%s" % (COMPRESSED_DATA_PATH, file_name), 'r') as zipf:
        zipf.extractall(UNCOMPRESSED_DATA_PATH)

def unzip_gzip(file_name):     
    with gzip.open('%s/%s' % (COMPRESSED_DATA_PATH, file_name), 'rb') as f_in:
        with open('%s/%s' % (UNCOMPRESSED_DATA_PATH, re.subn('.gz','.xml', file_name)[0]), 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


def check_data_is_up_to_date(file_name):
    if file_name in os.listdir(COMPRESSED_DATA_PATH):
        return True
    return False


def get_data_osher_ad(force=False):
    cd = CHAIN_DATA['osher_ad']

    with new_session(auth=True, chain_data=cd) as session:
        file_name = get_full_price_file_name(session, chain_data=cd)
        download_link = '%s/%s' % (cd['files_directory_url'], file_name)

        download_data_process(session, download_link, file_name, unzip_gzip, force=force)


def get_data_keshet_teamim(force=False):
    cd = CHAIN_DATA['keshet_teamim']

    with new_session(auth=True, chain_data=cd) as session:
        file_name = get_full_price_file_name(session, chain_data=cd)
        download_link = '%s/%s' % (cd['files_directory_url'], file_name)

        download_data_process(session, download_link, file_name, unzip_gzip, force=force)


def get_data_rami_levi(force=False):
    cd = CHAIN_DATA['rami_levi']
    
    with new_session(auth=True, chain_data=cd) as session:
        file_name = get_full_price_file_name(session, chain_data=cd)
        download_link = '%s/%s' % (cd['files_directory_url'], file_name)

        download_data_process(session, download_link, file_name, unzip_zip, force=force)
        

def get_data_shufersal(force=False):
    cd = CHAIN_DATA['shufersal']

    with new_session() as session:
        search_page = session.get('%s%s' % (cd['files_search_url'], cd['online_store_id']))
        soup = BeautifulSoup(search_page.content, "html.parser")
        
        download_link = soup.find('tr', {'class': 'webgrid-row-style'}).find('a').get('href')
        file_name = re.search('/([\w-]+\.gz)', download_link).group(1).lower()
        
        download_data_process(session, download_link, file_name, force=force)


def get_data_victory(force=False):
    cd = CHAIN_DATA['victory']

    with new_session() as session:
        search_page = session.get(cd['files_search_url'] % cd['online_store_id'])
        soup = BeautifulSoup(search_page.content, 'html.parser')        
        
        download_link = '%s/%s' % (cd['files_directory_url'], soup.select('#download_content td a')[0].get('href'))
        file_name = re.search('/([\w-]+\.xml.gz)', download_link).group(1).lower()
        
        download_data_process(session, download_link, file_name, force=force)


def get_data_mega(force=True):
    cd = CHAIN_DATA['mega']
    with new_session() as session:

        main_page = session.get(cd['files_search_url'])
        soup = BeautifulSoup(main_page.content, 'html.parser')
        dir_name = soup.select('td a')[2].get('href').strip('/')

        search_page = session.get('%s/%s' % (cd['files_search_url'], dir_name))
        soup = BeautifulSoup(search_page.content, 'html.parser')
        
        file_name = soup.find(text=re.compile('Price.+9090'))
        download_link = "%s/%s/%s" % (cd['files_search_url'], dir_name, file_name)

        download_data_process(session, download_link, file_name, force=force)


def download_data_process(session, download_link, file_name,unzip=unzip_gzip, force=False):
    if not force and check_data_is_up_to_date(file_name):
        if input('Your data is up to date, force update?[Y/N]\n').lower() == 'n':
            return

    print('Download file...')
    download_file(download_link, file_name, session)

    print('Extracting data...')
    unzip(file_name)
        

def get_all_data(**kwargs):
    get_data_victory(**kwargs)
    get_data_rami_levi(**kwargs)
    get_data_shufersal(**kwargs)
    get_data_mega(**kwargs)
    get_data_osher_ad(**kwargs)
    get_data_keshet_teamim(**kwargs)


def main():
    parser = argparse.ArgumentParser(description='Open-Source tool to download israeli food chains prices data.')
    parser.add_argument('-c','--chain_name', default='all',
            help='chain name to get data from, options: (ramilevi, shufersal, victory, keshet-teamim, mega, all)')
    parser.add_argument('-f', '--force', default=False, type=bool,
            help='Force downloding data` even if data is already up to date.')
    args= parser.parse_args()

    if not os.path.isdir('compressed'):
        os.mkdir('compressed')

    options = {
            'all': get_all_data,
            'ramilevi': get_data_rami_levi,
            'shufersal': get_data_shufersal,
            'victory': get_data_victory,
            'mega': get_data_mega,
            'osher_ad': get_data_osher_ad,
            'keshet_teamim': get_data_keshet_teamim
            }

    options[args.chain_name](force=args.force)

if __name__ == '__main__':
    main()

