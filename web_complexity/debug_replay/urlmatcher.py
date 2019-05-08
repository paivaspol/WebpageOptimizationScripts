from urllib.parse import urlparse

import numpy as np

NO_MATCH = '[NO_MATCH]'
EDIT_FRAC_THRESHOLD = 0.3
DEFAULT_EDIT_DISTANCE = 10000000

class RoughUrlMatcher:
    '''Implements an approximate URL matcher with various algorithms.'''

    def __init__(self):
        self.MAHIMAHI = 'mahimahi'
        self.LEVENSHTEIN = 'levenshtein'
        self.SIFT4 = 'sift4'
        self.MATCH_LAST_PATH_TOKEN = 'last_path_token'
        self.NO_MATCH = '[NO_MATCH]'

    def Match(self, url, matching_urls, match_algorithm):
        '''
        Returns the closest URL match to the given url
        '''
        # print('Matching: ' + url + ' algorithm: ' + match_algorithm)
        if match_algorithm == self.MAHIMAHI:
            return self.mahimahi_(url, matching_urls)
        elif match_algorithm == self.LEVENSHTEIN:
            return self.levenshtein_(url, matching_urls)
        elif match_algorithm == self.SIFT4:
            return self.sift4_(url, matching_urls)
        elif match_algorithm == self.MATCH_LAST_PATH_TOKEN:
            return self.match_last_path_token_(url, matching_urls)
        else:
            raise RuntimeError('Undefined matching algorithm')

    def GetMatchingScores(self, url, matching_urls, match_algorithm):
        '''Returns a dictionary mapping each matching url to the match score.'''
        if match_algorithm == self.SIFT4:
            return self.get_all_sift4_scores_(url, matching_urls)
        else:
            raise RuntimeError('Undefined matching algorithm')


    def match_last_path_token_(self, url, matching_urls):
        '''This is a variant of Mahimahi matching, but is a bit more lenient.

        Mahimahi checks whether the path and the parameter of the two
        URL match. This algorithm only matches the last token of the path.'''
        parsed_url_to_match = urlparse(url)
        url_to_match_without_query = '{scheme}://{netloc}{path}'.format(
                scheme=parsed_url_to_match.scheme,
                netloc=parsed_url_to_match.netloc,
                path=parsed_url_to_match.path)

        best_match = NO_MATCH
        best_match_score = -1
        for _, u in enumerate(matching_urls):
            parsed_u = urlparse(u)
            if parsed_u.scheme != parsed_url_to_match.scheme:
                continue

            # Try to only match the last token of the path.
            if not last_path_token_match_(parsed_url_to_match, parsed_u):
                continue

            score = min(len(parsed_url_to_match.params + ';' +
                parsed_url_to_match.query), len(parsed_u.params + ';' + parsed_u.query))
            for i in range(score):
                if url[i] != u[i]:
                    if i > best_match_score:
                        best_match = u
                        best_match_score = i

            if score > best_match_score:
                best_match = u
                best_match_score = score
        return best_match, best_match_score


    def levenshtein_(self, url, matching_urls):
        '''This is based on Levenshtein matching algorithm.'''
        parsed_url_to_match = urlparse(url)

        best_match = NO_MATCH
        best_match_score = 10000000
        for _, u in enumerate(matching_urls):
            parsed_u = urlparse(u)
            if parsed_u.scheme != parsed_url_to_match.scheme:
                continue

            url_path = get_path_(parsed_url_to_match)
            u_path = get_path_(parsed_u)

            if not should_use_matched_(url, u):
                continue

            score = compute_levenshtein_(url_path, u_path)

            # Levenshtein edit distance is the number of edits between the two
            # string. Thus, the smaller the better.
            if score < best_match_score:
                best_match = u
                best_match_score = score
        # Do a final sanity check that the match make sense.
        if best_match == NO_MATCH:
            return best_match, best_match_score
        return best_match, best_match_score


    def get_all_sift4_scores_(self, url, matching_urls):
        '''Get all matching scores for the given URL.'''
        parsed_url_to_match = urlparse(url)
        result = {}
        for _, u in enumerate(matching_urls):
            parsed_u = urlparse(u)
            if parsed_u.scheme != parsed_url_to_match.scheme:
                result[u] = DEFAULT_EDIT_DISTANCE
                continue

            if not should_use_matched_(url, u):
                result[u] = DEFAULT_EDIT_DISTANCE
                continue

            url_path = get_path_(parsed_url_to_match)
            u_path = get_path_(parsed_u)

            # Search for 500 tokens with a maximum of 200 distance.
            score = compute_sift4_(url_path, u_path, 5)
            result[u] = score
        return result


    def sift4_(self, url, matching_urls):
        '''This is based on Sift4 matching algorithm.'''
        best_match = NO_MATCH
        best_match_score = DEFAULT_EDIT_DISTANCE
        all_sift4_scores = self.get_all_sift4_scores_(url, matching_urls)
        for matching_url, score in all_sift4_scores.items():
            # Levenshtein edit distance is the number of edits between the two
            # string. Thus, the smaller the better.
            if not should_use_matched_(url, matching_url):
                continue

            parsed_matching_url = urlparse(matching_url)
            matching_url_path = get_path_(parsed_matching_url)

            if score < best_match_score:
                best_match = matching_url
                best_match_score = score
        return best_match, best_match_score


    def mahimahi_(self, url, matching_urls):
        '''This is based on Mahimahi's matching function.'''
        parsed_url_to_match = urlparse(url)
        url_to_match_without_query = '{scheme}://{netloc}{path}'.format(
                scheme=parsed_url_to_match.scheme,
                netloc=parsed_url_to_match.netloc,
                path=parsed_url_to_match.path)

        best_match = NO_MATCH
        best_match_score = -1
        for _, u in enumerate(matching_urls):
            parsed_u = urlparse(u)
            if parsed_u.scheme != parsed_url_to_match.scheme:
                continue

            if remove_query_(parsed_url_to_match) != remove_query_(parsed_u):
                continue

            score = min(len(url), len(u))
            for i in range(score):
                if url[i] != u[i]:
                    if i > best_match_score:
                        best_match = u
                        best_match_score = i
                        break

            if score > best_match_score:
                best_match = u
                best_match_score = score
        return best_match, best_match_score


def compute_levenshtein_(seq1, seq2):
    size_x = len(seq1) + 1
    size_y = len(seq2) + 1
    matrix = np.zeros ((size_x, size_y))
    for x in range(size_x):
        matrix [x, 0] = x
    for y in range(size_y):
        matrix [0, y] = y

    for x in range(1, size_x):
        for y in range(1, size_y):
            if seq1[x-1] == seq2[y-1]:
                matrix [x,y] = min(
                    matrix[x-1, y] + 1,
                    matrix[x-1, y-1],
                    matrix[x, y-1] + 1
                )
            else:
                matrix [x,y] = min(
                    matrix[x-1,y] + 1,
                    matrix[x-1,y-1] + 1,
                    matrix[x,y-1] + 1
                )
    return (matrix[size_x - 1, size_y - 1])


def compute_sift4_(seq1, seq2, max_offset, max_distance=0):
    '''
    Computes the distance between seq1 and seq2.

    Params:
        seq1: first string to compare
        seq2: second string to compare
        max_offset: number of positions of search for matching tokens
        max_distance: maximum distance between the two strings before giving up
    '''
    # Handle cases where seq1 or seq2 are invalid (None or empty)
    if seq1 is None or len(seq1) == 0:
        if seq2 is None:
            return 0
        return len(seq2)

    if seq2 is None or len(seq2) == 0:
        return len(seq1)

    # General case: both strings are valid and comparable.
    # var l1=s1.length;
    # var l2=s2.length;
    len_seq1 = len(seq1)
    len_seq2 = len(seq2)

    c_1 = 0
    c_2 = 0
    lcss = 0  # largest common subsequence
    local_cs = 0  # local common substring
    trans = 0  # number of transpositions ('ab' vs 'ba')
    offset_arr = []  # offset object: { "c1": c1, "c2": c2, "trans": trans }

    while (c_1 < len_seq1) and (c_2 < len_seq2):
        if seq1[c_1] == seq2[c_2]:
            local_cs += 1
            is_trans = False
            i = 0
            while i < len(offset_arr):  # see if current match is a transposition
                offset = offset_arr[i]
                if c_1 <= offset['c1'] or c_2 <= offset['c2']:
                    # when two matches cross, the one considered a transposition is the one with the largest difference in offsets
                    is_trans = abs(c_2 - c_1) >= abs(offset['c2'] - offset['c1'])
                    if is_trans:
                        trans += 1
                    else:
                        if not offset['trans']:
                            offset['trans'] = True
                            trans += 1;
                    break
                else:
                    if c_1 > offset['c2'] and c_2 > offset['c1']:
                        offset_arr.pop(0)
                    else:
                        i += 1
            offset_arr.append({
                'c1': c_1,
                'c2': c_2,
                'trans': is_trans,
            })
        else:
            lcss += local_cs
            local_cs = 0
            if c_1 != c_2:
                c_1 = min(c_1,c_2)
                c_2 = min(c_1,c_2)  # using min allows the computation of transposition

            # if matching characters are found, remove 1 from both cursors (they get incremented at the end of the loop)
            # so that we can have only one code block handling matches
            while i < max_offset and (c_1 + i < len_seq1 or c_2 + i < len_seq2):
                if (c_1 + i < len_seq1) and (seq1[c_1 + i] == seq2[c_2]):
                    c_1 += i - 1
                    c_2 -= 1
                    break
                if (c_2 + i < len_seq2) and (seq1[c_1] == seq2[c_2 + i]):
                    c_1 -= 1
                    c_2 += i - 1
                    break
                i += 1
        c_1 += 1
        c_2 += 1

        if max_distance > 0:
            temporary_dist = max(c_1,c_2) - (lcss - trans)
            if temporary_dist >= max_distance:
                return round(temporary_dist)
        # this covers the case where the last match is on the last token in list, so that it can compute transpositions correctly
        if (c_1 >= len_seq1) or (c_2 >= len_seq2):
            lcss += local_cs
            local_cs = 0
            c_1 = min(c_1, c_2)
            c_2 = min(c_1,c_2)
    lcss += local_cs
    return round(max(len_seq1, len_seq2) - (lcss - trans)) # remove half the number of transpositions from the lcss


def should_use_matched_(url1, url2):
    '''Checks if the given URLs have the same netloc.'''
    parsed_url1 = urlparse(url1)
    parsed_url2 = urlparse(url2)
    url1_path = parsed_url1.path
    url1_tokens = url1_path.split('/')
    num_url1_tokens = len(url1_tokens)
    url2_path = parsed_url2.path
    url2_tokens = url2_path.split('/')
    num_url2_tokens = len(url2_tokens)
    # return parsed_url1.netloc == parsed_url2.netloc and \
    #         num_url1_tokens == num_url2_tokens and \
    #         abs(len(url1_tokens[-1]) - len(url2_tokens[-1])) <= 2
    return parsed_url1.netloc == parsed_url2.netloc and \
            num_url1_tokens == num_url2_tokens


def remove_query_(parsed_url):
    '''Removes the query from the URL.'''
    retval = '{scheme}://{netloc}{path}'.format(
            scheme=parsed_url.scheme,
            netloc=parsed_url.netloc,
            path=get_path_(parsed_url))
    return retval


def get_path_(parsed_url):
    '''Returns the path and parameter.'''
    retval = parsed_url.path
    if parsed_url.params != '':
        retval += ';' + parsed_url.params
    return retval


def last_path_token_match_(parsed_u, parsed_url_to_match):
    '''Checks whether the last token of the path (ignoring the params) match.'''
    parsed_url_to_match_last_path_token = parsed_url_to_match.path.split('/')[-1]
    parsed_u_last_path_token = parsed_u.path.split('/')[-1]
    return parsed_url_to_match_last_path_token == parsed_u_last_path_token
