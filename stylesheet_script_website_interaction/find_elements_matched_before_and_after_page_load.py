from argparse import ArgumentParser
from bs4 import BeautifulSoup
from multiprocessing import Pool, freeze_support
from urlparse import urlparse
from collections import defaultdict

import common_module
import itertools
import os
import tinycss

NUM_PROCESSES = 4

def find_matched_difference_in_directory(root_dir, output_dir):
    common_module.create_directory_if_not_exists(output_dir)
    pages = os.listdir(root_dir)
    worker_pool = Pool(NUM_PROCESSES)
    worker_pool.map(find_matched_difference_wrapper, itertools.izip(itertools.repeat(root_dir), \
                                              pages, itertools.repeat(output_dir)))

def find_matched_difference(root_dir, directory, output_dir):
    print 'Processing: ' + directory
    common_module.create_directory_if_not_exists(os.path.join(output_dir, directory))
    html_before_page_load = os.path.join(root_dir, directory, 'before_page_load.html')
    html_after_page_load = os.path.join(root_dir, directory, 'after_page_load.html')
    request_id_to_url_mapping_filename = os.path.join(root_dir, directory, 'request_id_to_url.txt')
    if not (os.path.exists(html_before_page_load) and \
            os.path.exists(html_after_page_load) and \
            os.path.exists(request_id_to_url_mapping_filename)):
        return;
    # before_page_load_html_str = get_html_string(html_before_page_load)
    before_page_load_html = BeautifulSoup(open(html_before_page_load), 'html.parser')
    # after_page_load_html_str = get_html_string(html_after_page_load)
    after_page_load_html = BeautifulSoup(open(html_after_page_load), 'html.parser')
    css_files = get_css_files(request_id_to_url_mapping_filename)
    summary_dict = dict()
    union_css_to_children_count = dict()
    before_page_load_css_to_children_count = dict()
    after_page_load_css_to_children_count = dict()
    difference_page_load_css_to_children_count = dict()
    before_page_load_children_url = dict()
    after_page_load_children_url = dict()
    for css_file in css_files:
        css_full_path = os.path.join(root_dir, directory, css_file)
        if not os.path.exists(css_full_path):
            continue
        selectors, selector_to_url_count = parse_css(css_full_path)
        if selectors is None and selector_to_url_count is None:
            continue
        # print 'css_file: ' + css_file + ' selector len: ' + str(len(selectors))
        before_page_load_matched = find_elements_matched_by_selectors(before_page_load_html, \
                                                                      selectors)
        write_elements_matched_by_selectors(output_dir, directory, before_page_load_matched, 'before_page_load_elements_matched.txt')
        after_page_load_matched = find_elements_matched_by_selectors(after_page_load_html, \
                                                                     selectors)
        write_elements_matched_by_selectors(output_dir, directory, after_page_load_matched, 'after_page_load_elements_matched.txt')
        summary_dict[css_file] = (sum([ len(x) for x in before_page_load_matched.values() ]), sum([ len(x) for x in after_page_load_matched.values() ]))

        # Counting children related.
        union_of_selectors = generate_union_of_two_selector_lists({ key for (key, value) in before_page_load_matched.iteritems() if len(value) > 0 }, \
                                                                  { key for (key, value) in after_page_load_matched.iteritems() if len(value) > 0 })
        children_count_of_matched_selectors = filter_non_matching_selectors(union_of_selectors, selector_to_url_count)
        urls_for_union = get_urls_for_page(children_count_of_matched_selectors)
        union_css_to_children_count[css_file] = len(urls_for_union)

        children_count_of_matched_selectors_before_page_load = filter_non_matching_selectors({ key for (key, value) in before_page_load_matched.iteritems() if len(value) > 0 }, selector_to_url_count)
        before_page_load_children_url[css_file] = get_urls_for_page(children_count_of_matched_selectors_before_page_load)
        before_page_load_css_to_children_count[css_file] = len(before_page_load_children_url[css_file])

        children_count_of_matched_selectors_after_page_load = filter_non_matching_selectors({ key for (key, value) in after_page_load_matched.iteritems() if len(value) > 0 }, selector_to_url_count)
        after_page_load_children_url[css_file] = get_urls_for_page(children_count_of_matched_selectors_after_page_load)
        after_page_load_css_to_children_count[css_file] = len(after_page_load_children_url[css_file])
        difference_page_load_css_to_children_count[css_file] = find_difference_in_matched_children(children_count_of_matched_selectors_before_page_load, children_count_of_matched_selectors_after_page_load)

        # write the results
        write_result_detailed(output_dir, directory, css_file, before_page_load_matched, after_page_load_matched)
    write_result_summary(output_dir, directory, summary_dict)
    write_css_children(output_dir, directory, union_css_to_children_count, before_page_load_css_to_children_count, after_page_load_css_to_children_count, difference_page_load_css_to_children_count)
    write_children_url(output_dir, directory, before_page_load_children_url, 'children_url_before_page_load.txt')
    write_children_url(output_dir, directory, after_page_load_children_url, 'children_url_after_page_load.txt')

def get_urls_for_page(children_count_of_matched_selectors):
    result = set()
    for key, values in children_count_of_matched_selectors.iteritems():
        for value in values:
            result.add(value)
    return result

def write_children_url(output_dir, directory, css_children, filename):
    output_filename = os.path.join(output_dir, directory, filename)
    with open(output_filename, 'wb') as output_file:
        for key, children_urls in css_children.iteritems():
            output_file.write(key + '\n')
            for child in children_urls:
                output_file.write('\t' + child + '\n')

def find_difference_in_matched_children(before_page_load, after_page_load):
    after_page_load_urls = set(after_page_load)
    before_page_load_urls = set(before_page_load)
    difference = after_page_load_urls - before_page_load_urls
    return len(difference)

def generate_union_of_two_selector_lists(first_selector_list, second_selector_list):
    first_set = set(first_selector_list)
    second_set = set(second_selector_list)
    return first_set.union(second_set)

def find_matched_difference_wrapper(args):
    try:
        return find_matched_difference(*args)
    except Exception as e:
        print e
        return None

def filter_non_matching_selectors(base, dict_to_remove):
    result = dict(dict_to_remove)
    keys_to_remove = []
    for key in result:
        if key not in base and not key.startswith('@import'):
            # Always include @import
            keys_to_remove.append(key)
    for key in keys_to_remove:
        del result[key]
    return result

def write_elements_matched_by_selectors(output_dir, directory, elements_matched, filename):
    output_filename = os.path.join(output_dir, directory, filename)
    with open(output_filename, 'wb') as output_file:
        for key, elements in elements_matched.iteritems():
            if len(elements) > 0:
                output_file.write('{0}\n'.format(key))
                for element in elements:
                    if element is not None:
                        # print type(element)
                        first_line = str(element).split('\n')[0]
                        output_file.write('\t{0}\n'.format(first_line))
                output_file.write('\n')

def write_css_children(output_dir, directory, css_to_children_count, before_page_load_css_to_children_count, after_page_load_css_to_children_count, difference_page_load_css_to_children_count):
    output_filename = os.path.join(output_dir, directory, 'css_children_count.txt')
    with open(output_filename, 'wb') as output_file:
        output_file.write('# css_file children_of_all_selector_matched children_before_page_load children_after_page_load diff\n')
        for css_file in css_to_children_count:
            num_children_before_page_load = before_page_load_css_to_children_count[css_file] if css_file in before_page_load_css_to_children_count else 0
            num_children_after_page_load = after_page_load_css_to_children_count[css_file] if css_file in after_page_load_css_to_children_count else 0
            difference = difference_page_load_css_to_children_count[css_file] if css_file in difference_page_load_css_to_children_count else 0
            output_file.write('{0} {1} {2} {3} {4}\n'.format(css_file, css_to_children_count[css_file], num_children_before_page_load, num_children_after_page_load, difference))

def write_result_detailed(output_dir, directory, css_file, before_page_load_matched, after_page_load_matched):
    output_filename = os.path.join(output_dir, directory, css_file)
    selector_map_filename = os.path.join(output_dir, directory, 'selector_map.txt')
    with open(output_filename, 'wb') as output_file, open(selector_map_filename, 'wb') as selector_map_file:
        counter = 0
        for selector in before_page_load_matched:
            matched_after_page_load = 0
            if selector in after_page_load_matched:
                matched_after_page_load = after_page_load_matched[selector]
                del after_page_load_matched[selector]
            output_file.write('{0} {1} {2}\n'.format(counter, before_page_load_matched[selector], matched_after_page_load))
            selector_map_file.write('{0} {1}\n'.format(counter, selector))
            counter += 1

        # At this point, there isn't any selector in the before page load that we haven't covered.
        for selector in after_page_load_matched:
            output_file.write('{0} {1} {2}\n'.format(counter, 0, matched_after_page_load))
            selector_map_file.write('{0} {1}\n'.format(counter, selector))
            counter += 1

def write_result_summary(output_dir, directory, matched_summary):
    output_filename = os.path.join(output_dir, directory, 'summary.txt')
    with open(output_filename, 'wb') as output_file:
        for css_file in matched_summary:
            output_file.write('{0} {1} {2}\n'.format(css_file, matched_summary[css_file][0], matched_summary[css_file][1]))

def parse_css(css_filename):
    selectors = set()
    selector_to_url = defaultdict(set)
    try:
        stylesheet = tinycss.make_parser().parse_stylesheet_file(css_filename)
    except Exception as e:
        return None, None
    for rule in stylesheet.rules:
        if rule.at_keyword is None:
            selector = rule.selector.as_css()
            selectors.add(selector)
            # Extract URLs from this RuleSet
            for declaration in rule.declarations:
                for token in declaration.value:
                    if not token.is_container and token.type == 'URI':
                        selector_to_url[selector].add(str(token.value.encode('utf-8', 'ignore')))
        elif rule.at_keyword == '@import':
            selector_to_url['@import'].add(str(rule.uri.encode('utf-8', 'ignore')))
    return selectors, selector_to_url

def find_elements_matched_by_selectors(html, selectors):
    result_dict = dict()
    for selector in selectors:
        try:
            result_dict[selector] = html.select(selector)
        except Exception as e:
            pass
    return result_dict

def get_html_string(html_filename):
    html_str = ''
    with open(html_filename, 'rb') as input_file:
        for raw_line in input_file:
            html_str += raw_line
    return html_str

def get_css_files(request_id_to_url_mapping_filename):
    css_files = []
    with open(request_id_to_url_mapping_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            parsed_url = urlparse(line[1])
            if parsed_url.path.endswith('.css') or line[1].endswith('.css'):
                css_files.append(line[0] + '.beautified')
    return css_files

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    freeze_support()
    find_matched_difference_in_directory(args.root_dir, args.output_dir)
