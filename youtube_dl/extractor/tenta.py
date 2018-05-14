# coding: utf-8
from __future__ import unicode_literals

from .common import InfoExtractor
from ..compat import (
    compat_urlparse
)


class TentaIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?tenta\.com/how-to-download-videos'
    _TESTS = [{
        'url': 'https://tenta.com/how-to-download-videos',
        'md5': '815a64f01f7ebfb1607220396f3ffa7d',
        'info_dict': {
            'id': 'howto',
            'ext': 'mp4',
            'title': 'How To Download Videos & Save Securely | Tenta VPN Browser'
        }
    }]

    def _real_extract(self, url):
        video_id = 'howto'

        webpage = self._download_webpage(url, video_id)

        title = self._og_search_title(webpage, default=None)

        video_url = self._search_regex(r'<source[^>]+src=["\'](.+?)["\'][^>]+type=["\']video/mp4["\'][^>]*/>', webpage, 'video_url')
        video_url = compat_urlparse.urljoin(url, video_url)

        return {
            'id': video_id,
            'title': title,
            'url': video_url
        }
