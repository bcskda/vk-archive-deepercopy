import argparse
import logging
from extractor import supported_sources

KNOWN_ENCODINGS = 'windows-1251 utf-8'.split()

def parse_cmdline():
    parser = argparse.ArgumentParser(description='Download media refenced in vk.com data archive')
    parser.add_argument('archive_dir', type=str, help='Unpacked archive directory')
    parser.add_argument('--encoding', default='windows-1251', choices=KNOWN_ENCODINGS,
                        help='Encoding of files in archive (default: windows-1251)')
    source_subparsers = parser.add_subparsers(help='Archive section')
    
    for source in supported_sources.values():
        source_parser = source_subparsers.add_parser(source.title)
        source.init_parser(source_parser)

    return parser.parse_args()

def main(cmdline):
    logging.basicConfig(level=logging.INFO)
    source = supported_sources[cmdline.source]
    source.call(cmdline)

if __name__ == '__main__':
    main(parse_cmdline())
