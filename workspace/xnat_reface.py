# This script will launch mri_reface by:
# Parsing command line parameters
# Parsing a csv file and extracting scan information
# Launch the mri_reface shell script
import argparse
import csv
import subprocess
import sys
from ScanClassifierCSV import ScanClassifierCSV


# See https://www.nitrc.org/projects/mri_reface for more information

def main():
    try:
        param = parse_command_line_parameters()

        # If scan_type is not specified, parse csv file to extract scan type
        if param.scan_type is not None:
            scan_type = param.scan_type
        else:
            scan_type = extract_im_type(param.csv, param.experiment, param.scan)

        # Stage input files
        print('Staging input files...', flush=True)

        # Launch mri_reface
        print('Launching mri_reface...', flush=True)
        launch_shell_script(param.mri_reface_script, param.input, param.output, scan_type, param.mri_reface_opts)

        # Stage output files
        print('Staging output files...', flush=True)

    except csv.Error as e:
        sys.exit(f'Error parsing CSV file: {e}')
    except Exception as e:
        sys.exit(f'Error parsing command line parameters: {e}')


def parse_command_line_parameters():
    parser = argparse.ArgumentParser(description='XNAT mri_reface Launcher'
                                                 'This script will launch mri_reface:')
    parser.add_argument('--mri_reface_script', default='/usr/bin/mlrtapp/run_mri_reface.sh',
                        help='mri_reface shell script')
    parser.add_argument('--scan_type', default=None, help='Specify scan type.')
    parser.add_argument('--csv', default=None,
                        help='If no scanType given, specify CSV file containing scan classification data.')
    parser.add_argument('--experiment', required=False, default=None, help='Specify experiment name.')
    parser.add_argument('--scan', required=False, default=None, help='Specify scan name.')
    parser.add_argument('--mri_reface_opts', required=False, help='Specify optional mri_reface arguments.')
    parser.add_argument('--input', required=True, help='DICOM Scan input directory')
    parser.add_argument('--output', required=True, help='mri_reface output directory')
    args = parser.parse_args()
    if args.scan_type is None and args.csv is None:
        raise Exception('Either --scan_type or --csv must be specified.')
    return args


# Parse csv output from scan classifier, return mri_reface compatible imType
def extract_im_type(csv_file, experiment, scan):
    return ScanClassifierCSV(csv_file).get_im_type(experiment, scan)


def launch_shell_script(script_path, input, output, scan_type, mri_reface_opts):
    # Prepare the command
    command = [script_path, input, output, '-imType', scan_type]
    print(f"Launching mri_reface with command: {' '.join(command)}", flush=True)
    # Add mri_reface_opts if it is not None
    if mri_reface_opts is not None:
        command.extend(mri_reface_opts.split())
    # Run the command
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip(), flush=True)
    rc = process.poll()
    if rc != 0:
        raise Exception(f"Error launching mri_reface: return code {rc}")
    return rc


if __name__ == '__main__':
    print(f"Command line call: {' '.join(sys.argv)}", flush=True)
    main()
