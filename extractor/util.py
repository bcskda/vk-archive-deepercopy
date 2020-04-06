import functools
import glob
import itertools
import logging
import os
import re
import requests
from typing import List

class ValueSingleDispatch:
    def __init__(self):
        self._handlers = dict()

    def register(self, key):
        def decorator(fn: callable):
            if key in self._handlers:
                raise KeyError(key)
            self._handlers[key] = fn
            return fn

        return decorator

    def call(self, key, *args, **kwargs):
        if key not in self._handlers:
            raise KeyError(key)
        return self._handlers[key](*args, **kwargs)

    def valid_keys(self):
        return self._handlers.keys()

def alphanumeric_glob(pattern: str):
    """Glob and sort alpahnumerically. Limitations: exactly one `*', no `?', file names with single extention."""
    matches = glob.glob(pattern)
    asterisk_pos = pattern.find('*')
    matches.sort(key=lambda name: int(name[asterisk_pos:name.rfind('.')]))
    return matches

def findall_in_files(pattern: re.Pattern, filenames: List[str], encoding: str) -> re.Match:
    """Generator"""
    for filename in filenames:
        logging.debug('util.findall_in_files: input file %s', filename)
        with open(filename, 'rb') as ifile:
            for match in pattern.findall(ifile.read().decode(encoding)):
                logging.debug('util.findall_in_files(): match: file = %s, text = %s', filename, match)
                yield match

def make_pattern(url_regex: str, extentions: List[str]) -> re.Pattern:
    if extentions:
        ext_regex = '({})'.format('|'.join(extentions))
    else:
        ext_regex = '()'
    return re.compile(url_regex.format(extentions=ext_regex))

def download_by_pattern(url_regex: str, filenames: List[str], output_dir: str, *, extentions=[], encoding='windows-1251', limit=None):
    logging.debug('util.download_by_pattern(): pattern = %s, extentions = %s', url_regex, extentions)
    pattern = make_pattern(url_regex, extentions)
    matches = findall_in_files(pattern, filenames, encoding)
    if limit is not None:
        matches = itertools.islice(matches, limit)
    matches = list(matches)
    logging.info('util.download_by_pattern(): %d matches', len(matches))
    
    os.makedirs(output_dir, exist_ok=True)
    downloads = 0
    # TODO statistics by extention
    # TODO progressbar
    for idx, (url, ext) in enumerate(matches):
        local_name = '{:07d}'.format(idx) + '_' + os.path.basename(url)
        try:
            download(url, os.path.join(output_dir, local_name))
            downloads += 1
        except Exception as e:
            logging.warning('util.download_by_pattern(): unhandled exception: url = %s, e = %s', match_url, e)
    logging.info('util.download_by_pattern(): %d successful downloads', downloads)
    if downloads < len(matches):
        logging.warning('util.download_by_pattern(): %d downloads failed, see log for warnings', len(matches) - downloads)

def download(url: str, local_path: str) -> bool:
    logging.debug('util.download(): url = %s, local = %s', url, local_path)
    req = requests.get(url)
    with open(local_path, 'wb') as ofile:
        ofile.write(req.content)
