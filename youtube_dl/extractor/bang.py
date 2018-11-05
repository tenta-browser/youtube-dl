# coding: utf-8
from __future__ import unicode_literals

import base64
import binascii
import json

from .common import InfoExtractor
from ..compat import compat_urlparse
from ..utils import (
    ExtractorError,
    int_or_none
)


class BangIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?bang\.com/video/(?P<id>[0-9a-zA-Z_-]+)'
    _TEST = {
        'url': 'https://www.bang.com/video/WUGl51yzxV9da2of/madison-hart-is-a-tiny-blonde-teen-taking-a-big-dick-and-thick-creampie',
        'md5': 'e0a3397c4b93c97f1b7dc5c1d12e3b86',
        'info_dict': {
            'id': 'WUGl51yzxV9da2of',
            'ext': 'mp4',
            'title': 'Madison Hart is a tiny blonde teen taking a big dick and thick creampie',
            'description': 'md5:e7a8449f567d6be346a8299856ff0ccf',
            'age_limit': 18
        }
    }
    _LOGIN_URL = 'https://www.bang.com/login_check'
    _NETRC_MACHINE = 'bang'

    def _login(self, video_id):
        username, password = self._get_login_info()
        if not username:
                raise ExtractorError('LOGIN_REQUIRED', expected=True)

        login_data = json.dumps({
            "_username": username,
            "_password": password,
            "_remember_me": False}
        ).encode('utf-8')

        res = self._download_json(self._LOGIN_URL, video_id, 'Logging in', data=login_data)

        if not res.get('success'):
            raise ExtractorError('Invalid credentials', expected=True)

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)

        def get_api_key():
            return self._search_regex(
                r'apiKey\s*:\s*["\']([^"\']+)["\']',
                webpage,
                'api_key',
                default=None
            )
        api_key = get_api_key()
        if not api_key:
            self._login(video_id)
            webpage = self._download_webpage(url, video_id)
            api_key = get_api_key()

        mainjs_url = self._search_regex(
            r'<script[^>]+?src=["\'](?P<mainjs_url>/assets/js/main.[a-z0-9]+.js)',
            webpage,
            'main.js url')
        mainjs_url = compat_urlparse.urljoin(url, mainjs_url)
        mainjs = self._download_webpage(mainjs_url, video_id, 'Downloading main.js')

        elasticsearch_url = self._search_regex(
            r'"elasticsearch.url"\s*:\s*"([^"]+)"',
            mainjs,
            'Elasticsearch url'
        )

        elasticsearch_auth = self._search_regex(
            r'"elasticsearch.auth"\s*:\s*"([^"]+)"',
            mainjs,
            'Elasticsearch auth'
        )

        video_id_hex = binascii.hexlify(base64.urlsafe_b64decode(video_id)).decode('utf-8')

        metadata_url = compat_urlparse.urljoin(elasticsearch_url, "/videos/video/%s" % video_id_hex)
        metadata = self._download_json(metadata_url, video_id, headers={'Authorization': 'Basic ' + elasticsearch_auth})
        metadata_source = metadata['_source']

        identifier = metadata_source['identifier']
        title = metadata_source['name']
        description = metadata_source['description']

        links_url = 'https://links.bang.com/video/%s' % identifier
        links = self._download_json(links_url, video_id, note='Downloading links')

        formats = []
        for link in links:
            formats.append({
                'format_id': link['FormatName'],
                'filesize': int_or_none(link['Size']),
                'url': compat_urlparse.urljoin(links_url, link['Url']) + '?apiKey=' + api_key
            })

        self._sort_formats(formats)

        age_limit = self._rta_search(webpage)

        return {
            'id': video_id,
            'title': title,
            'description': description,
            'formats': formats,
            'age_limit': age_limit
        }
