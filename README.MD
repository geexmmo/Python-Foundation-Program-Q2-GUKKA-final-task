# Iteration 1:
# installation
clone repo   
```pip install -r requirements.txt```
# usage
## get feed
```python3 FinalV1.py http://feeds.rssboard.org/rssboard```
## get help
```python3 FinalV1.py -h```
# JSON output
## JSON example with validation
```python3 FinalV1.py http://feeds.rssboard.org/rssboard -l 1 -j | jq```
## JSON structure
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
# TEST
## unit testing Iteration 1
```bash
python FinalV1-test.py
```
# Iteration 2:
## building
```bash
#build
python3 -m pip install --upgrade build
python3 -m build
#upload
python3 -m pip install --upgrade twine
python3 -m twine upload --repository testpypi dist/*
```
## installing
```bash
python3 -m venv rssreadertest #ensure clean and isolated python environemnt, you dont want THIS in your system
cd rssreadertest
python3 -m pip install --index-url https://test.pypi.org/simple/ rssreader-arthur
```

## running
```
python lib/python3.10/site-packages/rssreader_arthur/rssreader.py
```
or as script provided by pip
```
rss-reader -v
#RSS reader version: 0.1
```