import logging
import argparse
import requests
import xml.etree.ElementTree as ET
import json
import datetime
import re
from fpdf import FPDF, HTMLMixin

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def check_if_rss(responce):
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


def http_get_feed(url: str):
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


def parse_rss(xmlstring: str, limit: int = 0):
    ''' Parses xml structure to build python dictionary containing channels,
    channel topics (news), and all metainformation'''
    chaninfo = {}
    tree = ET.ElementTree(ET.fromstring(xmlstring))
    root = tree.getroot()
    channumber = 0
    for channel in root.iter('channel'):
        logging.info(f"Iterating on channel: {channumber} \
                    [{channel.find('link').text}]")
        chaninfo[channumber] = {'title': channel
                                .find('title').text,
                                'description': channel
                                .find('description').text,
                                'language': channel
                                .find('language').text,
                                'link': channel
                                .find('link').text}
        itemcounter = 0
        itemlist = []
        for item in channel.iter('item'):
            if not limit:
                itemcounter = 0
                itemlimit = 1  # don't limit items if limit not set
            else:
                itemlimit = limit
            if itemcounter < itemlimit:
                logging.info(f"Iterating on channel item: {itemcounter} \
                    [{item.find('link').text}]")
                itemlist.append({
                    'title': item.find('title').text,
                    'link': item.find('link').text,
                    'description': item.find('description').text,
                    'pubDate': item.find('pubDate').text})
                chaninfo[channumber]['items'] = itemlist
                itemcounter += 1
            else:
                pass
        channumber += 1
    return chaninfo


def json_presentation(data: dict):
    '''In case of using `--json` argument
    your utility should convert the news into [JSON]format.'''
    # print('json')
    return json.dumps(data)


def user_presentation(data: dict, colorize: bool):
    ''' Composes data as human readable cli output '''
    out = []
    for i in data:
        out.append(f"{'='*8}\nSource: {data[i]['title']} \
                    [{data[i]['language']}] \
                    \n{data[i]['description']} {data[i]['link']}")
        for item in data[i]['items']:
            # out.append(str(item.keys()))
            for key in item.keys():
                out.append(f'{key} -:- {item[key]}')
            # out.append(f"{'-'*16}\n \
                # {bcolors.WARNING if colorize else ''} \
                # Title: \
                # {bcolors.ENDC if colorize else ''} \
                # {item['title']} \
                # \n{bcolors.WARNING if colorize else ''}Content:\
                # {bcolors.ENDC if colorize else ''}\n{item['description']}\
                # \n{bcolors.WARNING if colorize else ''}Time: \
                # {bcolors.ENDC if colorize else ''}\
                # {item['pubDate']}\
                # \n{bcolors.WARNING if colorize else ''}Link: \
                # {bcolors.ENDC if colorize else ''}\
                # {item['link']}\n{'-'*16}\n")
        out.append(f"{'='*8}")
    return out


def make_filename(url: str, cachedir: str):
    ''' creates clean filename from url'''
    # taking url from source arg
    # replacing all special symbols to get clean string
    regexpatt = r'\W'
    cleanurl = (re.sub(regexpatt, '', url))
    # now cleanurl does not contain any special symbols (:,/)
    # can be used as filename
    filename = cachedir + cleanurl
    return filename


def cache_make(data: dict, filename: str):
    ''' gets python dict and saves it as filename'''
    with open(filename, 'w') as file:
        json.dump(data, file)

def cache_check_path(path):
    '''checks if cache path exists
    returns true or false
    '''
    try:
      with open(path, 'r'):
        logging.info(f'Opened cache file: {path}')
        return True
    except:
        logging.error(f'No valid cache found: {path}')
        return False

def validate_date(date: str):
    ''' Checks for correct data submition when --date flag is used,
        returns unixtime or False '''
    # stime = "22/01/23"
    try:
        unixtime = int(
            datetime.datetime.strptime(date, "%Y/%m/%d")
            .timestamp())
        print('input time',unixtime)
        return unixtime
    except (ValueError, TypeError) as e:
        logging.error(f'Time error: {e}')
        return False


def cache_find_by_date(filename: str, input_time: str):
    ''' Loads json cache file, searching for matching date in topics,
    creates python dict that is understandable by
    user_presentation() and json_presentation(),
    returns False if fails to find topic by specified date'''
    # load json file
    with open(filename, 'r') as file:
        data = json.load(file)
    chaninfo = {}
    chan_matching_topics = []
    itemscount = 0
    # create python dict
    for channel in data:
        for topic in data[channel]['items']:
            # convert item's pubDate to unix time
            topic_time = int(
                datetime.datetime.strptime(topic['pubDate'], "%a, %d %b \
                %Y %H:%M:%S %z").timestamp())
            # compare topic time with specified time
            # finds matches in range of 1 day (86400 seconds)
            print('topic time', topic_time)
            if topic_time <= input_time - 86400 and \
                    topic_time >= input_time + 86400:
                print(f"{'match'*8}")
                chan_matching_topics.append(topic)
                itemscount += 1
            else:
                print('no match')
                print('input:',input_time, 'input_time + 86400: ',input_time + 86400)
                print('topic:', topic_time, 'topic_time + 86400', topic_time + 86400, 'topic_time - 86400:', topic_time - 86400)
            chaninfo[channel] = {
                'title': data[channel]['title'],
                'description': data[channel]['description'],
                'language': data[channel]['language'],
                'link': data[channel]['link'],
                'items': chan_matching_topics
                }
    if itemscount == 0:
        return False
    else:
        return chaninfo


def convert_to_html(data: str, filename: str):
    ''' Converts data as html file output '''
    out = []
    for i in data:
        out.append(f"<div id='header' style='background-color: blanchedalmond;'>\
            Source: {data[i]['title']} \
            Language: [{data[i]['language']}] \
                    </br>{data[i]['description']} {data[i]['link']}</div>")
        out.append('<div id="content">')
        for item in data[i]['items']:
            out.append(f"</br><container> \
                <div id='contenthead'> \
                Title: {item['title']} \
                </br>Time: {item['pubDate']}</br> \
                Link: <a href=\'{item['link']}\'>{item['link']}</a></div> \
                </br><div id='content' style='background-color: beige;'> \
                Content:</br>{item['description']}</div></container>")
        out.append('</div>')
    try:
        with open(filename, 'w') as f:
            f.writelines(out)
    except:
        logging.error('Failed to save html')



def convert_to_pdf(data: dict, filename: str):
    ''' Converts data as pdf file output '''
    class PDF(FPDF, HTMLMixin):
        def header(self):
            self.set_font("helvetica", "B", 12)
            title = []
            for i in data:
                title.append(data[i]['title'])
                title.append(data[i]['description'])
                title.append(data[i]['language'])
                title.append(data[i]['link'])
            for i in data:
                for item in data[i].keys():
                    if item != 'items':
                        self.multi_cell(0, 5, f'{data[i][item]}', border=1, align="C", new_x="LEFT",new_y="NEXT")
            self.ln(10)


        def footer(self):
            self.set_y(-15)
            self.set_font("helvetica", "I", 8)
            self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


    pdf = PDF()
    for i in data:
        pdf.add_page()
        pdf.set_font("helvetica", '', 10)
        for y in data[i]['items']:
            text = f"<p><b>{y['title']}</b>&nbsp;{y['pubDate']}</p></br>{y['description']}"
            pdf.write_html(text)  #y['pubDate'], y['description'], y['title']
            pdf.ln()
            # pdf.add_page()
    pdf.output(filename)



def main():
    cachedir = './testcache/'
    argparser = argparse.ArgumentParser(description='RSS reader')
    version = '0.1'
    argparser.version = ('{} version: {}').format(
            argparser.description, version)
    argparser.add_argument('source', metavar='[RSS URL]',
                           type=str,
                           help='url of rss feed')
    argparser.add_argument('-l', '--limit', metavar='LIMIT', action='store',
                           type=int,
                           help='limits output number of articles from feed')
    argparser.add_argument('-v', '--version', action='version',
                           help='Print version info')
    argparser.add_argument('-j', '--json', action='store_true',
                           help='Print result as JSON in stdout')
    argparser.add_argument('--date', action='store', type=str,
                           help='Specifies date in %%Y%%m%%d format \
                           to retrieve news from cache for specified date')
    argparser.add_argument('--verbose', action='store_true',
                           help='Outputs verbose status messages')
    argparser.add_argument('--to-html', action='store', type=str,
                           help='Outputs HTML file, file path must be supplied ("/tmp/file.html")')
    argparser.add_argument('--to-pdf', action='store', type=str,
                           help='Outputs PDF file, file path must be supplied ("/tmp/file.pdf")')
    argparser.add_argument('--colorize', action='store_true',
                           help='Adds colorization to outputs')
    args = argparser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug('verbose logging enabled')
    if args.date:
        unixtime = validate_date(args.date)
        if unixtime:
            logging.info(f'Date valid {args.date}')
            filename = make_filename(args.source, cachedir)
            if cache_check_path(filename):
                logging.info('Found cache')
                data = cache_find_by_date(filename, unixtime)
                if data:
                    print(''.join(user_presentation(data, args.colorize)))
                else:
                    logging.error(f'No topics found for {args.date}')
            else:
                text = http_get_feed(args.source)
                if check_if_rss(text):
                    cache_make(parse_rss(text), filename)
                    data = cache_find_by_date(filename, unixtime)
                    print(''.join(user_presentation(data, args.colorize)))
        else:
            # date format error
            logging.error('Invalid date format')
            pass
    else:
        text = http_get_feed(args.source)
        if check_if_rss(text):
            data = parse_rss(text, args.limit)
            if args.json:
                print(json_presentation(data))
            elif args.to_html:
                convert_to_html(data, args.to_html)
            elif args.to_pdf:
                convert_to_pdf(data, args.to_pdf)
            else:
                print(''.join(user_presentation(data, args.colorize)))


if __name__ == '__main__':
    main()
