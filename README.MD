# Iteration 1:
# installation
#git clone repo   
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