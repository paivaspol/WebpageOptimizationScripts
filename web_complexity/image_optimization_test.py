from bs4 import BeautifulSoup

import os
import unittest

import image_optimization

class TestImageOptimizations(unittest.TestCase):

    def test_parse_dimensions_file(self):
        expected = {
                '/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png': ('272', '92')
        }
        testcase_filename = os.path.join('test_resources', 'dimensions_testcases')
        got = image_optimization.ParseDimensionsFile(testcase_filename)
        self.assertEqual(got, expected)


    def test_rewrite_html(self):
        expected = '''
        <html><head></head><body><img src="123456.jpg" width="1" height="1"/></body></html>
        '''
        soup = BeautifulSoup(expected, 'html5lib')
        testcase_filename = os.path.join('test_resources', 'html_testcase')
        page_img_mapping = { '1.jpg': '1' }
        page_group_hashes = { '1': '123456' }
        dimensions = { '1.jpg': ('1', '1') }
        got = image_optimization.RewriteHtml(testcase_filename, page_img_mapping, page_group_hashes, dimensions)
        self.assertEqual(got, str(soup))


    def test_create_img_record_file(self):
        def get_header(headers, key):
            for h in headers:
                if h.key == key:
                    return h.value
            return None

        img_file = image_optimization.CreateImageRecordFile('1.jpg', '8.8.8.8', '443', 'www.google.com', 100)
        self.assertEqual(img_file.request.first_line, 'GET 1.jpg HTTP/1.1')
        self.assertEqual(get_header(img_file.request.header, 'Host'), 'www.google.com')
        self.assertEqual(get_header(img_file.response.header, 'Content-Length'), '100')
        self.assertEqual(''.join([ 'A' for i in xrange(0, 100) ]), img_file.response.body)


if __name__ == '__main__':
    unittest.main()
