'''
This script implements HTML rewrite for image optimization. The
high-level idea of the optimization is that some images from the
same domain and similar caching policy can be grouped together
similar to the CSS sprite technique.

Input to script:
    - HTML source file
    - Mapping between resource to the group
    - Mapping from URLs to sizes

Output:
    - Modified HTML that contains the groupped image
    - Dummy image in which the size equals the sum of groupped resources (in Mahimahi format)
'''

from argparse import ArgumentParser
from bs4 import BeautifulSoup
from collections import defaultdict

import common_module
import http_record_pb2
import json
import shutil

# Extension for the dummy output images.
EXTENSION = '.jpg'

def Main():
    if os.path.exists(args.output_dir):
        shutil.rmtree(args.output_dir)
    os.mkdir(args.output_dir)

    # These are already aggregated by pages.
    img_mapping, size_mapping, group_hashes, group_to_ip_port_hostname = ParseMappingFile(args.grouping_file)
    pages = GetPages(args.page_list)
    
    for page in pages:
        page_output_dir = os.path.join(args.output_dir, p)
        os.mkdir(page_output_dir)

        # Get all the data necessary for constructing the images.
        page_img_mapping = img_mapping[page]
        page_size_mapping = size_mapping[page]
        pagee_group_hashes = group_hashes[page]
        page_group_to_ip_port_hostname = group_to_ip_port_hostname[page]
        dimensions_file = os.path.join(args.experiment_dir, page, 'console_' + page)
        page_dimensions = ParseDimensionsFile(dimensions_file)

        # First, rewrite HTML.
        page_record_dir = os.path.join(args.record_dir, page)
        all_root_htmls = GetRootHtmls(page, page_record_dir)
        for root_html in all_root_htmls:
            src = os.path.join(page_record_dir, root_html)
            dst = os.path.join(page_output_dir, root_html)
            shutil.copy2(src, dst)
            # RewriteMahimahiHtml(dst, page_img_mapping, page_group_hashes, page_dimensions)

        # Generate the dummy image files.
        dummy_images_output_dir = os.path.join(args.output_dir, page, 'images')
        os.mkdir(dummy_images_output_dir)
        GenerateMahimahiImages(page_size_mapping, page_group_hashes, page_group_to_ip_port_hostname, dummy_images_output_dir)


def GetPages(page_list):
    '''
    Returns a list of pages.
    '''
    pages = []
    with open(page_list, 'r') as input_file:
        for l in input_file:
            if len(l.strip()) == 0 or l.startswith('#'):
                continue
            pages.append(common_module.escape_page(l.strip()))
    return pages


def RewriteMahimahiHtml(root_html_filename, page_img_mapping, page_group_hashes, dimensions):
    cmd = './protototext {0} temp_root_html'.format(root_html_filename)
    output = subprocess.check_output(cmd.split())
    res_type = output.split('*')[0].split('=')[1]
    gzip = output.split('*')[2].split('=')[1]
    chunked = output.split('*')[1].split('=')[1]
    if 'true' in chunked:
        # If the content is chunked, 3 steps:
        #   1: unchunk the response
        #   2: replace unchunked the response
        #   3: remove the chunk in the response header
        cmd = 'python unchunk.py {0} {1}'.format('temp_root_html', 'temp_root_html_unchunked')
        subprocess.call(cmd.split())
        cmd = 'mv {0} {1}'.format('temp_root_html_unchunked', 'temp_root_html')
        subprocess.call(cmd.split())
        cmd = './removeheader {0} Transfer-Encoding'.fomrat(root_html_filename)
        subprocess.call(cmd.split())

        # Remove the unchunked file.
        os.remove('temp_root_html_unchunked')

    # Uncompress, if necessary and put it in a file called final_html_response
    if 'true' in gzip:
        cmd = 'gzip -d -c {0} > final_html_response'.format('temp_root_html')
    else:
        cmd = 'cp {0} {1}'.format('temp_root_html', 'final_html_repsonse')
    subprocess.call(cmd, shell=True)
    rewritten_html = RewriteHtml('final_html_response', page_img_mapping, page_group_hashes, dimensions)

    # Write the rewritten HTML to a temp file and compress it, if necessary.
    with tempfile.NamedTemporaryFile() as temp:
        temp.write(rewritten_html)
        temp.flush()

        if 'true' in gzip:
            cmd = 'gzip -c {0} > finalfile'.format(temp.name())
        else:
            cmd = 'cp {0} {1}'.format(temp.name(), 'finalfile')
        subprocess.call(cmd, shell=True)

    # Write the file back to the initial file.
    cmd = './texttoproto finalfile {1}'.format(root_html_filename)
    subprocess.call(cmd.split())
    
    size = os.path.getsize('finalfile')
    cmd = './changeheader {0} Content-Length {1}'.format(root_html_filename, size)

    os.remove('finalfile')
    os.remove('temp_root_html')
    os.remove('final_html_response')


def GenerateMahimahiImages(size_mapping, group_hashes, group_to_ip_port_hostname, group_to_mm_output_dir):
    '''
    3 Steps:
        - Iterates through all the groups,
        - Create the image group for the group,
        - Dump the file to the output dir
    '''
    for i, group in enumerate(size_mapping):
        group_hash = group_hashes[group]
        size = size_mapping[group]
        ip, port, hostname = group_to_ip_port_hostname[group]
        image_record_file = CreateImageRecordFile(group_hash + EXTENSION, ip, port, hostname)
        output_path = os.path.join(mm_output_dir)
        with open(os.path.join(output_path, 'save.{0}'.format(i)), 'w') as output_file:
            output_file.write(image_record_file.SerializeToString())

def CreateImageRecordFile(resource_filename, ip, port, host, size):
    '''
    Creates mahimahi format recording file.
    '''
    def add_request_header(img_file, key, value):
        header = img_file.request.header.add()
        header.key = key
        header.value = bytes(value)

    def add_response_header(img_file, key, value):
        header = img_file.response.header.add()
        header.key = key
        header.value = bytes(value)

    img_file = http_record_pb2.RequestResponse()

    # Populate Request Headers
    img_file.request.first_line = 'GET {0} HTTP/1.1'.format(resource_filename)
    add_request_header(img_file, 'Host', host)
    add_request_header(img_file, 'User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36')
    add_request_header(img_file, 'Accept-Encoding', 'gzip, deflate, br')
    add_request_header(img_file, 'Connection', 'keep-alive')
    add_request_header(img_file, 'Accept', 'image/webp,image/apng,image/*,*/*;q=0.8')

    # Populate Response Headers
    img_file.response.first_line = 'HTTP/1.1 200 OK'
    add_response_header(img_file, 'Accept-Ranges', 'bytes')
    add_response_header(img_file, 'Content-Type', 'image/jpg')
    add_response_header(img_file, 'Content-Length', size)
    add_response_header(img_file, 'Date', 'Thu, 17 May 2018 21:26:22 GMT')
    add_response_header(img_file, 'Cache-Control', 'max-age=31536000')
    add_response_header(img_file, 'Last-Modified', 'Wed, 14 Dec 2016 20:30:00 GMT')
    img_file.response.body = ''.join([ 'A' for i in xrange(0, size) ])
    return img_file


def GetRootHtmls(page, page_record_dir):
    '''
    Iterate the record directory to find the main HTML of the page.
    '''
    top_level_htmls = []
    for f in os.listdir(page_record_dir):
        cmd = './protototext {0} top_level_temp'.format(f)
        output = subprocess.check_output(top_cmd.split())
        output = output.strip()
        top_level_html = output.split('na--me=')[1]
        resource_type = output.split('*')[0].split('=')[1]
        if page == common_module.escape_page(top_level_html):
            top_level_htmls.append(f)
        os.remove('top_level_temp')
    return top_level_htmls


def RewriteHtml(original_html_filename, page_img_mapping, page_group_hashes, dimensions):
    '''
    This function uses the BeautifulSoup and rewrites the HTML with the image
    mapping information.
    '''
    with open(original_html_filename, 'r') as input_file:
        original_html = input_file.read()
    soup = BeautifulSoup(original_html, 'html5lib')

    # Get all images from the HTML
    all_imgs = soup.find_all('img')
    for dom_img in all_imgs:
        original_url = dom_img['src']
        for img in page_img_mapping:
            if original_url not in img:
                continue
            dom_img['width'] = dimensions[img][0]
            dom_img['height'] = dimensions[img][1]
            dom_img['src'] = page_group_hashes[page_img_mapping[img]] + '.jpg'
    return str(soup)


def ParseMappingFile(mapping_filename):
    '''
    Returns:
        - a mapping from URL to dictionary of resource URL to the grouping
        - a mapping of URL to dictionary of grouping to the sum of sizes
        - a mapping of grouping to its hash
    '''
    with open(mapping_filename, 'r') as input_file:
        raw_mapping = json.loads(input_file.read())

    img_mapping = defaultdict(dict)
    size_mapping = {}
    group_to_hash = defaultdict(dict)
    group_to_ip_port_hostname = defaultdict(dict)
    for page_grouping in raw_mapping:
        url = common_module.escape_page(page_grouping['url'])
        images = page_grouping['images']
        for img in images:
            original = img['src']
            grouping = img['dst']
            group_to_hash[grouping] = hash(grouping)
            img_mapping['url'][original] = grouping
            group_to_ip_port_hostname[url][grouping] = (img['ip'], img['port'], img['hostname'])

        sizes = page_grouping['size']
        for size in sizes:
            size_mapping[url][size['src']] = size['dst']

    return img_mapping, size_mapping, group_to_hash, group_to_ip_port_hostname


def ParseDimensionsFile(dimensions_filename):
    '''
    Parses the console log that contains the DOM content of image nodes 
    with their sizes.
    '''
    dimensions_mapping = {}
    with open(dimensions_filename, 'r') as input_file:
        for l in input_file:
            message = json.loads(l.strip())
            img_outer_html = message['params']['message']['text']
            img_obj = BeautifulSoup(img_outer_html, 'html5lib').find('img')
            dimensions_mapping[img_obj['src']] = (img_obj['width'], img_obj['height'])
    return dimensions_mapping


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('experiment_dir')
    parser.add_argument('record_dir')
    parser.add_argument('page_list')
    parser.add_argument('grouping_filename')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    Main()
