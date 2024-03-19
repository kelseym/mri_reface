# This script will launch mri_reface by:
# Parsing command line parameters
# Parsing a csv file and extracting scan information
# Launch the mri_reface shell script
import argparse
import csv
import subprocess
import sys


# See https://www.nitrc.org/projects/mri_reface for more information

def main(name):
    param = None;
    try:
        param = parse_command_line_parameters()
    except Exception as e:
        sys.exit(f'Error parsing command line parameters: {e}')

    try:
        parse_csv_file(param.csv_file)
    except csv.Error as e:
        sys.exit(f'Error parsing CSV file: {e}')


def parse_command_line_parameters():
    parser = argparse.ArgumentParser(description='XNAT mri_reface Launcher'
                                                 'This script will launch mri_reface:')
    parser.add_argument('--csv_file', help='CSV file containing scan classification')
    args = parser.parse_args()
    return args.param


def parse_csv_file(file_path='sample.csv'):
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            print(', '.join(row))

def extractScanType(row):

def launch_shell_script(script_path):
    result = subprocess.run(['sh', script_path], stdout=subprocess.PIPE)
    if result.returncode != 0:
        sys.exit(f"Shell script failed with error: {result.stderr.decode()}")


if __name__ == '__main__':
    main('PyCharm')
