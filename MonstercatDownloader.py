#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from argparse import ArgumentParser, RawTextHelpFormatter
import os
import re
from pathlib import Path

def DownloadMonstercatLibrary(sid, output_dir, format="mp3_320", creator_friendly=True):
	skip = 0
	count = 0

	downloaded_count = 0
	exists_count = 0
	not_downloadable_count = 0
	while True:
		params = {
			'skip': skip
		}
		if creator_friendly:
			params['creatorfriendly'] = True

		r = requests.get(
			'https://connect.monstercat.com/v2/catalog/browse',
			params = params,
			cookies = {'connect.sid': sid}
		)
		resp = json.loads(r.text)

		for track in resp['results']:
			count += 1

			if not track['downloadable']:
				not_downloadable_count += 1
				continue

			if track['release']['type'] == 'Single':
				subdir = 'Singles'
			else:
				subdir = "{artist} - {release}".format(
					artist = track['release']['artistsTitle'],
					release = track['release']['title']
				).replace('|', '-').replace('/', '-').replace('\\', '-').replace(':', '')
				subdir = re.sub(r'[*?:"<>|]' ,'', subdir)

			if not os.path.exists("{parent}/{sub}".format(parent=output_dir, sub=subdir)):
				os.mkdir("{parent}/{sub}".format(parent=output_dir, sub=subdir))

			title_esc = re.sub(r'[*?:"<>|]' ,'', track['title'])
			full_path = "{parent}/{sub}/{artist} - {title}.mp3".format(
				parent = output_dir,
				sub = subdir,
				artist = track['artistsTitle'],
				title = title_esc.replace('/', '-').replace('\\', '-')
			).replace('//', '/')

			percent = '%0.2f' % ((float(count)/float(resp['total'])) * 100)
			status_str = "[{current}/{total} {percent}%]".format(
				current = count,
				total = resp['total'],
				percent = percent
			)
			print(status_str, end='\r', flush=True)

			if not os.path.exists(full_path):
				mp3 = requests.get(
					'https://connect.monstercat.com/v2/release/{release_id}/track-download/{track_id}'.format(
						release_id = track['release']['id'],
						track_id = track['id']
					),
					params = {'format': format},
					cookies = {'connect.sid': sid}
				)

				with open(full_path, 'wb') as f:
					f.write(mp3.content)
				downloaded_count += 1
			else:
				exists_count += 1

		if (resp['skip'] + resp['limit']) >= resp['total']:
			break

		skip += resp['limit']

	print('')
	print('Downloaded: {}'.format(downloaded_count))
	print('Existed: {}'.format(exists_count))
	print('Undownloadable: {}'.format(not_downloadable_count))

if __name__ == '__main__':
	parser = ArgumentParser(description='Download Monsertcat Library\nTo access SID on chrome:\nchrome://settings/cookies/detail?site=connect.monstercat.com\n', formatter_class=RawTextHelpFormatter)
	parser.add_argument('-s', '--sid', help="sid for downloading using Monstercat Gold account", required=True)
	parser.add_argument('-d', '--directory', help="Output directory to save mp3's", required=True)
	parser.add_argument('-f', '--format', help="Download format as specified by Monstercat API", default='mp3_320')
	parser.add_argument('--creatorunfriendly', help="Include tracks that are creator unfriendly", action="store_true")
	args = parser.parse_args()

	creator_friendly = True
	if args.creatorunfriendly:
		creator_friendly = False

	if not os.path.exists(args.directory):
		print('Directory does not exist: {}'.format(args.directory))
		exit()

	DownloadMonstercatLibrary(args.sid, args.directory, args.format, creator_friendly=creator_friendly)
