# MonstercatDownloader

Script to easily download all creator friendly tracks using your Monstercat gold account. You must have Monstercat gold for this to work.

You will need your Monstercat SID to use this script. You can get it in chrome by visiting the following URL. Copy the sid which should start with "s%3A".
```
chrome://settings/cookies/detail?site=connect.monstercat.com
```

```
usage: MonstercatDownloader.py [-h] -s SID -d DIRECTORY [-f FORMAT]
                               [--creatorunfriendly]

Download Monsertcat Library
To access SID on chrome:
chrome://settings/cookies/detail?site=connect.monstercat.com

optional arguments:
  -h, --help            show this help message and exit
  -s SID, --sid SID     sid for downloading using Monstercat Gold account
  -d DIRECTORY, --directory DIRECTORY
                        Output directory to save mp3's
  -f FORMAT, --format FORMAT
                        Download format as specified by Monstercat API
  --creatorunfriendly   Include tracks that are creator unfriendly
```

## Example
```
MonstercatDownloader.py -s <sid> -d C:\Monstercat\
```
