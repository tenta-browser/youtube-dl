# coding: utf-8
from __future__ import unicode_literals

import re

from .common import InfoExtractor
from ..compat import compat_urlparse
from ..utils import (
    ExtractorError
)


class VideosZIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.|m\.|)videosz\.com/[a-z]+/[a-z]+/(?P<id>[0-9]+)_'
    _TEST = {
        'url': 'http://www.videosz.com/us/scene/91296_i-want-to-be-a-dream-girl-66',
        'md5': '4fab13db1a962d421cc17c86b9f21830',
        'info_dict': {
            'id': '91296',
            'ext': 'mp4',
            'age_limit': 17,
            'title': 'I Want To Be A Dream Girl 66 Scene 1',
            'description': 'I Want To Be A Dream Girl 66 Scene 1'
        }
    }

    def _real_extract(self, url):
        url = re.sub(r'^(https?://(?:.+?\.)?)m\.', r'\1', url)

        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)

        if re.search('<form[^>]*id="login_form"[^>]*>', webpage):
            raise ExtractorError('LOGIN_REQUIRED', expected=True)

        title = self._html_search_meta('title', webpage, 'title')
        title = re.sub(r'([^:]+):.+', r'\1', title)

        formats_source = self._search_regex(
            r'<div[^>]*id="download_options_btn_content"[^>]*>(.+?)</div>',
            webpage, 'formats_source', flags=re.DOTALL)

        formats = []
        format_matches = re.findall(r'<a[^>]*href="(?P<url>[^"]+)"[^>]*>(?P<format>[^(]+) \([^)]+\)</a>', formats_source)
        for format_url, format in format_matches:
            formats.append({
                'format_id': format,
                'url': compat_urlparse.urljoin(url, format_url)
            })

        self._sort_formats(formats)

        return {
            'id': video_id,
            'title': title,
            'description': title,
            'age_limit': self._media_rating_search(webpage),
            'formats': formats
        }
