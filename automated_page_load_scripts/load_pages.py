from argparse import ArgumentParser
from browsermobproxy import Server
from selenium import webdriver

import time

capabilities = {
    'chromeOptions': {
        'androidPackage': 'com.android.chrome',
#        'androidDeviceSerial': '0b04d1340bfc51e7',
    },
    'applicationCacheEnabled': False
}

output_filename = 'page_start_end_time.txt'
page_with_last_modified = 'page_with_last_modified.txt'
last_modified_header_key = 'last-modified'

def load_pages(pages_filename):
    with open(pages_filename, 'rb') as input_file:
        header_count = dict()
        for raw_line in input_file:
            page = raw_line.rstrip()
            print 'Opening: ' + page
            load_page_helper(page, header_count)
        print 'Header count:'
        for key, count in header_count.iteritems():
            print str(key) + ' ' + str(count)

def load_page(page, header_count):
    with open(output_filename, 'ab') as output_file, \
        open(page_with_last_modified, 'ab') as page_with_last_modified_file:
        # Setup Browser proxy.
        start_time = str(int(round(time.time() * 1000)))
#        print 'started'
        driver = webdriver.Remote('http://localhost:9515', capabilities)
        driver.get(page)
        end_time = str(int(round(time.time() * 1000)))
        timings = driver.execute_script('return window.performance.timing')
        if check_header(driver, last_modified_header_key):
            page_with_last_modified_file.write(str(page) + '\n')
        driver.quit()
        load_time = timings['loadEventEnd'] - timings['navigationStart']
#        print 'start_time: ' + str(timings['navigationStart']) + ' end_time: ' + str(timings['loadEventEnd']) + ' load time: ' + str(load_time)
        output_file.write(page + ' ' + str(timings['navigationStart']) + ' ' + str(timings['loadEventEnd']) + '\n')
        time.sleep(1) # Sleep in second in between

def check_header(driver, header_name):
    headers = driver.execute_script('var req = new XMLHttpRequest(); \
            req.open(\'GET\', document.location, false); \
        req.send(null); \
        var headers = req.getAllResponseHeaders().toLowerCase(); \
        return headers')
    if header_name in headers:
        print headers
    return header_name in headers
    

def load_page_helper(page, header_count):
    try:
        load_page(page, header_count)
    except Exception as e:
        time.sleep(1)
        print 'Ignoring Exception: ' + str(e)
        load_page_helper(page, header_count)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('pages_filename')
    args = parser.parse_args()
    load_pages(args.pages_filename)
