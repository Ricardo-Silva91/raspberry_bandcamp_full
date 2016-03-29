import bandcamp_to_hdd
import bandcamp_sniffer
import file_runner
import argparse
import os


def get_parser():
    parser = argparse.ArgumentParser(description='mr brain')
    parser.add_argument('data_json', metavar='DATA_JSON', type=str, nargs='?', help='absolute path to json file to sniff to')
    parser.add_argument('download_folder', metavar='DOWNLOAD_FOLDER', type=str, nargs='?', help='folder in which to save albums')
    parser.add_argument('sample_folder', metavar='SAMPLE_FOLDER', type=str, nargs='?', help='folder in which to save samples')
    parser.add_argument('after_folder', metavar='AFTER_FOLDER', type=str, nargs='?',
                        help="folder in which to put albums after samples are taken")
    parser.add_argument('size', metavar='SIZE', type=int, nargs='?', help='maximum size of folder (in Mb)')
    parser.add_argument('time_to_sniff', metavar='TIME_TO_SNIFF', type=int, nargs='?', help='time to sniff')
    return parser


def command_line_runner():
    parser_j = get_parser()
    args = vars(parser_j.parse_args())

    # bandcamp_get.bandcamp_get_for_import('mrgloomy', '/home/rofler/D/ua\ local/py\ scripts/w', '1')
    # bandcamp_to_hdd.bandcamp_to_hdd_for_import('/home/rofler/D/ua\ local/py\ scripts/w', 100,
    #                                            '/home/rofler/data.json')
    # bandcamp_sniffer.bandcamp_sniffer_for_import('/home/rofler/data.json', 0, 'firefox', 10)
    # file_runner.file_runner_for_import('/home/rofler/D/links/test/',
    #                                    '/home/rofler/usb')

    # sniff for time inserted
    bandcamp_sniffer.bandcamp_sniffer_for_import(args['data_json'], 0, 'firefox', args['time_to_sniff'])

    # download some albums
    bandcamp_to_hdd.bandcamp_to_hdd_for_import(args['download_folder'], args['size'], args['data_json'])

    # get the samples
    file_runner.file_runner_for_import(args['download_folder'], args['sample_folder'])

    # move the folders to after_folder
    prepared_command = 'mv ' + args['download_folder'] + '/* ' + args['after_folder']
    # prepared_command = lucky_cunt['id']
    print(prepared_command)
    # call('', prepared_command)
    os.system(prepared_command)

    return


if __name__ == '__main__':
    command_line_runner()
