from nose.tools import eq_

from pylcp.url import url_path_join


class TestUrlPathJoin(object):
    def setup(self):
        self.url = 'http://localhost/path'
        self.part = 'part'

    def test_url_with_trailing_slash_and_part_with_leading_slash(self):
        eq_(
            url_path_join(self.url + '/', '/' + self.part),
            'http://localhost/path/part'
        )

    def test_url_with_trailing_slash_and_part_without_leading_slash(self):
        eq_(
            url_path_join(self.url + '/', self.part),
            'http://localhost/path/part'
        )

    def test_url_without_trailing_slash_and_part_with_leading_slash(self):
        eq_(
            url_path_join(self.url, '/' + self.part),
            'http://localhost/path/part'
        )

    def test_url_without_trailing_slash_and_part_without_leading_slash(self):
        eq_(
            url_path_join(self.url, self.part),
            'http://localhost/path/part'
        )
