from argparse import ArgumentParser

from scrapy.selector import Selector

def parse_css(css_filename):
    selectors = set()
    with open(css_filename, 'rb') as input_file:
        raw_line = input_file.readline()
        found_selector = False
        selector = ''
        while raw_line != '':
            line = raw_line.rstrip()
            if line.startswith('.') or line[:1].isalpha() or line.startswith('#'):
                found_selector = True   # We have found a selector start it here.
                for c in line:
                    if c != '{':
                        selector += c
                    else:
                        # We have complete the discovering a selector
                        found_selector = False
                        if not selector.startswith('only screen'):
                            # print selector
                            selectors.add(selector)
                        selector = ''
                        break
            raw_line = input_file.readline()
    return selectors

def find_elements_matched_by_selectors(html_str, selector):
    try:
        result = Selector(text=html_str).css(selector).extract()
        print 'selector: ' + selector + ' ' + str(len(result))
    except Exception as e:
        pass

def get_html_string(html_filename):
    html_str = ''
    with open(html_filename, 'rb') as input_file:
        for raw_line in input_file:
            html_str += raw_line
    return html_str

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('css_filename')
    parser.add_argument('html_filename')
    args = parser.parse_args()
    selectors = parse_css(args.css_filename)
    html_str = get_html_string(args.html_filename)
    for selector in selectors:
        find_elements_matched_by_selectors(html_str, selector)
