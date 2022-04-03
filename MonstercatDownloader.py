#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from argparse import ArgumentParser, RawTextHelpFormatter

import requests
from pathvalidate import sanitize_filename


def DownloadMonstercatLibrary(sid, output_dir, format="mp3_320", creator_friendly=True):
    offset = 0
    count = 0

    downloaded_count = 0
    exists_count = 0
    not_downloadable_count = 0
    skipped_count = 0

    while True:
        params = {
            'offset': offset
        }
        if creator_friendly:
            params['CreatorFriendly'] = True

        r = requests.get(
            'https://player.monstercat.app/api/catalog/browse',
            params=params,
            cookies={'cid': sid}
        )
        resp = json.loads(r.text)

        print(r.url)

        manual_limit = len(resp['Data'])

        for track in resp['Data']:
            count += 1

            if not track['Downloadable']:
                not_downloadable_count += 1
                print(track['Release']['Title'] + " not Downloadable")
                continue

            if track['Release']['Type'] == 'Podcast' or track['Release']['Type'] == 'Compilation':
                skipped_count += 1
                print("Skipped: " + track['Release']['Title'])
                continue

            if track['Release']['Type'] == 'Single':
                subdir = 'Singles'
            else:
                version = track['Release']['Version']
                if version != "":
                    version = " " + version
                subdir = "{artist} - {release}{version}".format(
                    artist=track['Release']['ArtistsTitle'],
                    release=track['Release']['Title'],
                    version=version
                ).replace('|', '-').replace('/', '-').replace('\\', '-').replace(':', '')
                # subdir = re.sub(r'[*?:"<>|]' ,'', subdir)
                subdir = sanitize_filename(subdir)

            if not os.path.exists("{parent}/{sub}".format(parent=output_dir, sub=subdir)):
                os.mkdir("{parent}/{sub}".format(parent=output_dir, sub=subdir))

            filetype = ""
            if format == "mp3_320":
                filetype = "mp3"
            else:
                filetype = format

            version = track['Version']
            if version != "":
                version = " " + version

            full_path = "{parent}/{sub}/{artist} - {title}{version}.{filetype}".format(
                parent=output_dir,
                sub=subdir,
                artist=sanitize_filename(track['ArtistsTitle']),
                title=sanitize_filename(track['Title']),
                filetype=filetype,
                version=version
            ).replace('//', '/')

            percent = '%0.2f' % ((float(count) / float(resp['Total'])) * 100)
            status_str = "[{current}/{total} {percent}% -- Skipped: {skipped_count}]".format(
                current=count,
                total=resp['Total'],
                percent=percent,
                skipped_count=skipped_count
            )
            print(status_str, end='\r', flush=True)

            if not os.path.exists(full_path):
                mp3 = requests.get(
                    'https://player.monstercat.app/api/release/{release_id}/track-download/{track_id}'.format(
                        release_id=track['Release']['Id'],
                        track_id=track['Id']
                    ),
                    params={'format': format},
                    cookies={'cid': sid}
                )

                if mp3.status_code != 200:
                    print('Failed to download {path}, request returned status code {status}. Skipping'.format(
                        path=full_path, status=mp3.status_code))
                    continue

                with open(full_path, 'wb') as f:
                    f.write(mp3.content)
                downloaded_count += 1
            else:
                print(track['Release']['Title'] + " ~ " + track['Title'] + " already exists")
                exists_count += 1

        if (resp['Offset'] + manual_limit) >= resp['Total']:
            break

        print("Next Request at " + str(count) + "/" + str(resp['Total']) + "              ")
        offset += manual_limit

    print('')
    print('Downloaded: {}'.format(downloaded_count))
    print('Existed: {}'.format(exists_count))
    print('Skipped: {}'.format(skipped_count))
    print('Undownloadable: {}'.format(not_downloadable_count))


if __name__ == '__main__':
    parser = ArgumentParser(
        description='Download Monsertcat Library\nTo access SID (cid) on chrome:\nchrome://settings/cookies/detail?site=connect.monstercat.com\n',
        formatter_class=RawTextHelpFormatter)
    parser.add_argument('-s', '--sid', help="sid for downloading using Monstercat Gold account", required=True)
    parser.add_argument('-d', '--directory', help="Output directory to save mp3's", required=True)
    parser.add_argument('-f', '--format', help="Download format as specified by Monstercat API - mp3_320 / flac / wav", default='mp3_320')
    parser.add_argument('--creatorunfriendly', help="Include tracks that are creator unfriendly", action="store_true")
    args = parser.parse_args()

    creator_friendly = True
    if args.creatorunfriendly:
        creator_friendly = False

    if not os.path.exists(args.directory):
        print('Directory does not exist: {}'.format(args.directory))
        exit()

    DownloadMonstercatLibrary(args.sid, args.directory, args.format, creator_friendly=creator_friendly)
