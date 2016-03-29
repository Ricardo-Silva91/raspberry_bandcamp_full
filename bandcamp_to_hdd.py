import json
import os

import calc_size
import argparse


def get_parser():
    parser = argparse.ArgumentParser(description='bandcamp sniffer')
    parser.add_argument('file', metavar='FILE', type=str, nargs='?', help='absolute path to json file to sniff to')
    parser.add_argument('folder', metavar='FILE', type=str, nargs='?', help='folder in which to save albums')
    parser.add_argument('size', metavar='FILE', type=str, nargs='?', help='maximum size of folder (in Mb)')
    return parser


def brain(download_folder, json_file, data):

    # get artist username
    lucky_cunt = data['bc-get'][0]

    # remove it from array
    data['bc-get'] = data['bc-get'][1:]

    # add it to 'used' list
    data['used'].append(lucky_cunt)

    # update json file
    with open(json_file, 'w') as f:
        json.dump(data, f)

    # print(str(len(data['bc-get'])))

    # print(lucky_cunt['id'])

    prepared_command = 'bandcamp-get -f ' + download_folder + ' ' + lucky_cunt['id']
    # prepared_command = lucky_cunt['id']
    print(prepared_command)
    # call('', prepared_command)
    os.system(prepared_command)

    # print(data)
    # print(str(len(data['bc-get'])))

    return


def command_line_runner():
    parser_j = get_parser()
    args = vars(parser_j.parse_args())
    folder = args['folder']
    size = int(args['size'])

    try:
        with open(args['file'], 'r') as data_file:
            data = json.load(data_file)
    except Exception:
        print('please insert working json file path')
        return

    dir_size = calc_size.get_size(folder)
    initial_size = dir_size

    print(calc_size.get_size(args['folder']))

    while dir_size < initial_size + size*1000000:
        brain(folder, args['file'], data)

        dir_size = calc_size.get_size(folder)
        print(dir_size)

    print('end of jogos')


if __name__ == '__main__':
    command_line_runner()
