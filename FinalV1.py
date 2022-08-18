import logging
import argparse
import requests
import xml.etree.ElementTree as ET
import json

def checkIfRss(responce):
    ''' Checks if feeded data contains valid rss tags '''
    try:
        tree = ET.ElementTree(ET.fromstring(responce))
        root = tree.getroot()
        if root.tag == 'rss': 
            logging.info('Valid RSS')
            return True
        else: 
            logging.error('Maybe XML, Invalid RSS')
            return False
    except ET.ParseError as err:
        logging.critical(f'RSS parsing error: {err}, source not valid rss')
        return False

def httpGetFeed(url: str):
    ''' Makes http request to specified url to get rss feed'''
    try:
        responce = requests.get(url)
        responce.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        logging.error(f'HTTP error: {http_err}')
        return False
    except Exception as err:
        logging.error(f'Unknown error: {err}')
        return False
    else:
        # logging.info(f'HTTP request OK {responce.status_code}')
        # already logged by lib
        pass
    responce.encoding = 'utf-8'
    return responce.text

def parseRSS(xmlstring: str, limit: int = 0):
    ''' Parses xml structure to build python dictionary containing channels, channel topics (news), and all metainformation'''
    chaninfo = {}
    tree = ET.ElementTree(ET.fromstring(xmlstring))
    root = tree.getroot()
    channumber = 0
    for channel in root.iter('channel'):
        logging.info(f"Iterating on channel: {channumber} [{channel.find('link').text}]")
        chaninfo[channumber] = {'title': channel.find('title').text,
                    'description': channel.find('description').text,
                    'language':channel.find('language').text,
                    'link':channel.find('link').text}
        itemcounter = 0 
        itemlist = []
        for item in channel.iter('item'):
            if not limit: itemcounter = 0; itemlimit = 1 # don't limit items if limit not set 
            else: itemlimit = limit
            if itemcounter < itemlimit:
                logging.info(f"Iterating on channel item: {itemcounter} [{item.find('link').text}]")
                itemlist.append({
                'title':item.find('title').text,
                'link':item.find('link').text,
                'description':item.find('description').text,
                'pubDate':item.find('pubDate').text})
                chaninfo[channumber]['items'] = itemlist
                itemcounter += 1
            else: pass
        channumber += 1
    return chaninfo

def jsonPresentation(data: dict):
    '''In case of using `--json` argument your utility should convert the news into [JSON]format.'''
    # print('json')
    return json.dumps(data)

def userPresentation(data: dict):
    ''' Composes data as human readable cli output '''
    out = []
    for i in data:
        out.append(f"{'='*8}\nSource: {data[i]['title']} [{data[i]['language']}]\n{data[i]['description']} {data[i]['link']}")
        # print(f"{'='*8}\nSource: {data[i]['title']} [{data[i]['language']}]\n{data[i]['description']} {data[i]['link']}")
        for item in data[i]['items']:
            # print(f"{'-'*16}\nTitle: {item['title']}\
            #     \nContent:\n{item['description']}\
            #     \nTime: {item['pubDate']}\nLink: {item['link']}\n{'-'*16}\n")
            out.append(f"{'-'*16}\nTitle: {item['title']}\
                \nContent:\n{item['description']}\
                \nTime: {item['pubDate']}\nLink: {item['link']}\n{'-'*16}\n")
        # print(f"{'='*8}")
        out.append(f"{'='*8}")
    return out

def main():
    argparser = argparse.ArgumentParser(description='RSS reader')
    version = '0.1'
    argparser.version = ('{} version: {}').format(argparser.description, version)
    argparser.add_argument('source', metavar='[RSS URL]', type=str,
                            help='url of rss feed')
    argparser.add_argument('-l', '--limit', metavar='LIMIT', action='store', type=int,
                            help='limits output number of articles from feed')
    argparser.add_argument('-v', '--version', action='version', 
                            help='Print version info')
    argparser.add_argument('-j', '--json', action='store_true', 
                            help='Print result as JSON in stdout')
    argparser.add_argument('--verbose', action='store_true', 
                            help='Outputs verbose status messages')
    args = argparser.parse_args()
    if args.verbose: 
        logging.basicConfig(level=logging.DEBUG)
        logging.debug('verbose logging enabled')
    text = httpGetFeed(args.source)
    if text:
        if checkIfRss(text):
            data = parseRSS(text, args.limit)
            if args.json: print(jsonPresentation(data))
            else: print(''.join(userPresentation(data)))

if __name__ == '__main__':
    main()