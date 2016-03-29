from pydub import AudioSegment
import argparse
import ntpath

"""
# len() and slicing are in milliseconds
halfway_point = len(sound) / 2
second_half = sound[halfway_point:]

# Concatenation is just adding
second_half_3_times = second_half + second_half + second_half

# writing mp3 files is a one liner
second_half_3_times.export("tes1.mp3", format="mp3")
"""


def get_parser():
    parser = argparse.ArgumentParser(description='bandcamp sniffer/download brain')

    parser.add_argument('file', metavar='FILE', type=str, help='absolute path to mp3 file to slice', nargs='?')
    parser.add_argument('samples_folder', metavar='SAMPLES_FOLDER', type=str,
                        help='absolute path to folder to put samples in',
                        nargs='?')

    return parser


def slicer(file_mp3, samples_folder):
    sound = AudioSegment.from_mp3(file_mp3)
    twenty_seconds = 20000

    halfway_point = len(sound) / 2
    mp3_slice = sound[halfway_point:halfway_point + twenty_seconds]
    head, tail = ntpath.split(file_mp3)
    mp3_slice.export(samples_folder + '/' + tail + ".mp3", format='mp3')


def command_line_runner():
    parser = get_parser()
    args = vars(parser.parse_args())

    if not args['file'] == 'None':

        sound = AudioSegment.from_mp3(args['file'])
        twenty_seconds = 20000

        halfway_point = len(sound) / 2
        mp3_slice = sound[halfway_point:halfway_point + twenty_seconds]
        mp3_slice.export(args['samples_folder'] + '/' + "tes1.mp3", format='mp3')

    else:
        pass


if __name__ == '__main__':
    command_line_runner()
