import mp3_slicer
import argparse
import os


def get_parser():
    parser = argparse.ArgumentParser(description='bandcamp sniffer/download brain')

    parser.add_argument('bc_get_folder', metavar='BC_GET_FOLDER', type=str,
                        help='absolute path to bandcamp get folder with artist directories', nargs='?')
    parser.add_argument('samples_folder', metavar='SAMPLES_FOLDER', type=str,
                        help='absolute path to folder to put samples in',
                        nargs='?')

    return parser


def file_runner_for_import(bc_get_folder, samples_folder):
    # parser = get_parser()
    # args = vars(parser.parse_args())

    args = vars()
    args['bc_get_folder'] = bc_get_folder
    args['samples_folder'] = samples_folder

    if not (args['bc_get_folder'] == 'None' or args['samples_folder'] == 'None'):

        bc_get_folder = args['bc_get_folder']
        samples_folder = args['samples_folder']

        for file in os.listdir(bc_get_folder):
            for file_inside in os.listdir(bc_get_folder + '/' + file):
                # take only firs one
                if file_inside.endswith('.zip'):
                    print('unziping')
                    prepared_command = 'unzip -n "' + bc_get_folder + '/' + file + '/' + file_inside + '" -d "' + bc_get_folder + '/' + file + '"'
                    # print(prepared_command)
                    os.system(prepared_command)

                    first_mp3 = 0

                    for file_mp3 in os.listdir(bc_get_folder + '/' + file):
                        if file_mp3.endswith('.mp3'):
                            if first_mp3 == 0:
                                print('lucky file')
                                mp3_slicer.slicer(bc_get_folder + '/' + file + '/' + file_mp3, samples_folder)
                                first_mp3 = 1

                            # print('removing')
                            os.remove(bc_get_folder + '/' + file + '/' + file_mp3)

                        if file_mp3.endswith('.jpg'):
                            os.remove(bc_get_folder + '/' + file + '/' + file_mp3)

                    break

            print('jogos')
    else:
        pass


