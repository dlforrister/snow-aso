import argparse
import csv
import glob
import os
import shutil

parser = argparse.ArgumentParser()
parser.add_argument(
    '--image-path',
    type=str,
    help='Root directory of the basin',
    required=True
)
parser.add_argument(
    '--file-csv',
    type=str,
    help='Change image file names to given type. Default: tif',
    default='tif',
)

if __name__ == '__main__':
    arguments = parser.parse_args()
    file_list = []

    with open(arguments.file_csv, 'r', newline='') as csv_file:
        files = csv.reader(csv_file)
        [file_list.append(file[0]) for file in files]

    images = glob.glob(os.path.join(arguments.image_path, '*.tif'))

    for image in images:
        if os.path.basename(image) in file_list:
            print('moving file: ' + str(image))
            print('  to: ' + os.path.join(arguments.image_path, 'keep', ''))
            shutil.move(image, os.path.join(arguments.image_path, 'keep', ''))
