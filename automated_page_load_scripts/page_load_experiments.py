from argparse import ArgumentParser
# from browsermobproxy import Server
from selenium import webdriver

import time
import os

capabilities = {
    'chromeOptions': {
        'androidPackage': 'com.android.chrome',
#        'androidDeviceSerial': '0b04d1340bfc51e7',
    },
    'applicationCacheEnabled': False
}

output_filename = 'page_load_experiment.txt'
last_modified_header_key = 'last-modified'

NUM_ITERATIONS = 5

def load_pages(pages_filename):
    with open(pages_filename, 'rb') as input_file:
        header_count = dict()
        for raw_line in input_file:
            page = raw_line.rstrip()
            print 'Opening: ' + page
            load_page_helper(page, header_count, 0)

def load_page(page, header_count):
    with open(output_filename, 'ab') as output_file:
        # Setup Browser proxy.
        output_file.write('Page: ' + str(page) + '\n')
        driver = webdriver.Remote('http://localhost:9515', capabilities)
        driver.get(page)
        end_time = str(int(round(time.time() * 1000)))
        timings = driver.execute_script('return window.performance.timing')
        driver.quit()
        load_time = timings['loadEventEnd'] - timings['navigationStart']
        output_file.write(str(load_time) + '\n')
        time.sleep(1) # Sleep in second in between
        return 1

def load_page_helper(page, header_count, counter):
    print 'Page: ' + page + ' ' + str(counter)
    try:
        counter += load_page(page, header_count)
    except Exception as e:
        time.sleep(1)
        print 'Ignoring Exception: ' + str(e)
        counter = load_page_helper(page, header_count, counter)

    if counter < NUM_ITERATIONS:
        counter = load_page_helper(page, header_count, counter)
    return counter

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('pages_filename')
    args = parser.parse_args()
    if os.path.exists(output_filename):
        os.remove(output_filename)
    load_pages(args.pages_filename)
