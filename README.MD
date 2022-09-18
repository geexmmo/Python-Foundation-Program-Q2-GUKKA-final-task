# Iteration 1:
## installation
clone repo   
```pip install -r requirements.txt```
## usage
### get feed
```python3 FinalV1.py http://feeds.rssboard.org/rssboard```
### get help
```python3 FinalV1.py -h```
## JSON output
### JSON example with validation
```python3 FinalV1.py http://feeds.rssboard.org/rssboard -l 1 -j | jq```
### JSON structure
```json
{
  "0 - channel number": {
    "title": "channel title",
    "description": "channel description",
    "language": "en-us",
    "link": "https://channel-url",
    "items": [
      {
        "title": "item title",
        "link": "https://item-url",
        "description": "item text",
        "pubDate": "Wed, 02 Apr 2014 11:12:53 -0400 - item publication date"
      }
    ]
  }
}
```
## tests
### unit testing Iteration 1
```bash
python FinalV1-test.py
```   
# Iteration 2
Without entering virtual environement installaton will be performed to the Python user install directory for your platform.   
Typically ~/.local/, or %APPDATA%\Python on Windows.

Example above performs confined installation in virtual enviroment.   
Installed package vill be available as long as enviroment is activated (or correct PATH is set)

## Installing
While this project is hosted on test index of pypi - some dependencies can't be resolved by package manager.  
Dependencies from normal index shoud be installed before the main package from test index to bypass this.   
```bash
cd /tmp
#ensure clean and isolated python environemnt, you dont want THIS in your system
python3 -m venv rssreadertest
cd rssreadertest
source bin/activate

# requirements bypass
curl https://github.com/geexmmo/Python-Foundation-Program-Q2-GUKKA-final-task/raw/main/requirements.txt -kL -o requirements.txt
pip install -r requirements.txt

python3 -m pip install --index-url https://test.pypi.org/simple/ rssreader-arthur
```

## running
As script provided by pip
```bash
rss-reader -v
# RSS reader version: 0.1

# geexmmo@pc /tmp/rssreadertest % whereis rss-reader
# rss-reader: /tmp/rssreadertest/bin/rss-reader
```
Or extracted from package
```
python lib/python3.10/site-packages/rssreader_arthur/rssreader.py
```

## building example
```bash
git clone https://github.com/geexmmo/Python-Foundation-Program-Q2-GUKKA-final-task.git
cd Python-Foundation-Program-Q2-GUKKA-final-task/packaging/
# build
python3 -m pip install --upgrade build
python3 -m build
# upload
python3 -m pip install --upgrade twine
python3 -m twine upload --repository testpypi dist/*
```

# Iteration 3:
Script will cache feed when fetches feed.
```bash
# this query will cache result of http://feeds.rssboard.org/rssboard in cachedir with file name of 'httpfeedsrssboardorgrssboard'
python3 FinalV1.py http://feeds.rssboard.org/rssboard
# when --date argument in format %Y%m%d is passed - search by date from cache is performed
python3 FinalV1.py http://feeds.rssboard.org/rssboard --date 2014/04/02
# --limit also works
python3 FinalV1.py http://feeds.rssboard.org/rssboard --limit 1
```

# Iteration 4:
Format convertsion
Supported formats: html, pdf
## usage
```bash
python3 FinalV1.py http://feeds.rssboard.org/rssboard --to-html /tmp/file.html
python3 FinalV1.py http://feeds.rssboard.org/rssboard --to-pdf /tmp/file.pdf
```
# iteration 5:
Colorization
Outputs colorized text (yellow ;D) to cli
```bash
python3 FinalV1.py http://feeds.rssboard.org/rssboard --colorize
python3 FinalV1.py http://feeds.rssboard.org/rssboard --colorize -l 2
python3 FinalV1.py http://feeds.rssboard.org/rssboard --date 2008/01/17 --colorize
```
# iteration 6
## Running docker
```bash
docker-compose up
```
## register user
```bash
curl -i -X POST -H "Content-Type: application/json" -d '{"username":"user","password":"password"}' http://127.0.0.1:5000/api/users
```
## get token
not required but there it is:
```bash
curl -i -H "Content-Type: application/json"  http://127.0.0.1:5000/api/token -u user
```
## get feed
Limit items and json/cli output
```bash
curl 'http://127.0.0.1:5000/api/req' -H "Content-Type: application/json" -d '{"source":"http://feeds.rssboard.org/rssboard","json":"ok","limit":"2"}' -u TOKEN/ORUSERNAME:x
```

## database caching
endpoint fetches full rss feed, caches feed if not cached already into database
```bash
curl 'http://127.0.0.1:5000/api/cache' -H "Content-Type: application/json" -d '{"source":"http://feeds.rssboard.org/rssboard"}' -u TOKEN/ORUSERNAME:x
```
## query cache by date
```bash
curl 'http://127.0.0.1:5000/api/cache' -H "Content-Type: application/json" -d '{"source":"http://feeds.rssboard.org/rssboard","date":"2014/04/02"}' -u TOKEN/ORUSERNAME:x
```