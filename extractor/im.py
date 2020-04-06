import argparse
import logging
import os
from typing import List
from .util import ValueSingleDispatch, alphanumeric_glob, download_by_pattern
from .config import *

class ImSource:
    title = 'im'

    _supported_media = ValueSingleDispatch()
    
    @_supported_media.register('photo')
    def photo(args):
        ImSource._fetch_attachments(args, 'photo', PHOTO_EXTENTIONS)

    @_supported_media.register('voice_message')
    def voice_message(args):
        ImSource._fetch_attachments(args, 'voice_message', VOICE_MESSAGE_EXTENTIONS)

    @staticmethod
    def init_parser(parser: argparse.ArgumentParser):
        parser.set_defaults(source=ImSource.title)
        parser.add_argument('peer_id', type=int)
        parser.add_argument('media_type', type=str, choices=ImSource._supported_media.valid_keys())
        parser.add_argument('--last-n', type=int, default=None, help='default: no limit')
    
    @staticmethod
    def call(cmdline):
        return ImSource._supported_media.call(cmdline.media_type, cmdline)

    @staticmethod
    def _fetch_attachments(args, media_type: str, extentions: List[str]):
        logging.debug('im._fetch_by_extention(): args = %s', args)
        input_glob = os.path.join(args.archive_dir, 'messages', str(args.peer_id), 'messages*.html')
        logging.debug('im._fetch_by_extention(): input filename mask = %s', input_glob)
        input_files = alphanumeric_glob(input_glob)
        regex = r"<a class='attachment__link' href='(\S+\.{extentions})'>"
        output_dir = os.path.join(args.archive_dir, OUTPUT_DIR, 'im', str(args.peer_id), media_type)
        download_by_pattern(regex, input_files, output_dir, extentions=extentions,
                            encoding=args.encoding, limit=args.last_n)

exported_source = ImSource
