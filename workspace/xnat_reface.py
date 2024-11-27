# This script will launch mri_reface by:
# Parsing command line parameters
# Parsing a csv file and extracting scan information
# Launch the mri_reface shell script
import argparse
import csv
import logging
import subprocess
import sys
import time
import glob
import shutil
import xnat
import os

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

        # if delete_existing is True, delete existing output resources
        if param.delete_existing:
            delete_reface_outputs(param)

        # Stage input files
        print('Staging input files...', flush=True)

        # Launch mri_reface
        print('Launching mri_reface...', flush=True)
        launch_shell_script(param.mri_reface_script, param.input, param.output, scan_type, param.mri_reface_opts)

        # Stage output files
        print('Staging output files...', flush=True)
        refaced_nifti_output_dir = f'{param.output}/refaced_nifti'
        subprocess.run(['mkdir', refaced_nifti_output_dir])
        print(f"Moving refaced nifti files to {refaced_nifti_output_dir}", flush=True)
        stage_output_files(param.output, refaced_nifti_output_dir, '*deFaced.nii')
        stage_output_files(param.output, refaced_nifti_output_dir, '*Warp.nii')

        nifti_output_dir = f'{param.output}/nifti'
        subprocess.run(['mkdir', nifti_output_dir])
        print(f"Moving nifti files to {nifti_output_dir}", flush=True)
        stage_output_files(param.output, nifti_output_dir, '*.nii')

    except csv.Error as e:
        sys.exit(f'Error parsing CSV file: {e}')
    except Exception as e:
        sys.exit(f'Error launching mri_reface: {e}')


def parse_command_line_parameters():
    parser = argparse.ArgumentParser(description='XNAT mri_reface Launcher'
                                                 'This script will launch mri_reface:')
    parser.add_argument('--mri_reface_script', default='/usr/bin/mlrtapp/run_mri_reface.sh',
                        help='mri_reface shell script')
    parser.add_argument('--scan_type', default=None, help='Specify scan type.')
    parser.add_argument('--csv', default=None,
                        help='If no scanType given, specify CSV file containing scan classification data.')
    parser.add_argument('--project', required=False, default=None, help='Specify project id.')
    parser.add_argument('--experiment', required=False, default=None, help='Specify experiment name.')
    parser.add_argument('--scan', required=False, default=None, help='Specify scan name.')
    parser.add_argument('--mri_reface_opts', required=False, help='Specify optional mri_reface arguments.')
    parser.add_argument('--input', required=False, default='/input', help='DICOM Scan input directory')
    parser.add_argument('--output', required=False, default='/output', help='mri_reface output directory')
    parser.add_argument('--delete_existing', required=False, default=True, help='Delete existing output recources - '
                                                                                'REFACED_QC, REFACED_DICOM, NIFTI, '
                                                                                'REFACED_NIFTI')
    parser.add_argument("--host", default=os.getenv("XNAT_HOST"),
                        help="XNAT server URL (default: environment variable XNAT_HOST)."
                        )
    parser.add_argument("--user", default=os.getenv("XNAT_USER"),
                        help="XNAT username (default: environment variable XNAT_USER)."
                        )
    parser.add_argument("--password", default=os.getenv("XNAT_PASSWORD"),
                        help="XNAT password (default: environment variable XNAT_PASSWORD)."
                        )
    args = parser.parse_args()
    if args.scan_type is None and args.csv is None:
        raise Exception('Either --scan_type or --csv must be specified.')
    return args


# Delete existing mri_reface output resources
def delete_reface_outputs(param):
    reface_resources = ['REFACED_QC', 'REFACED_DICOM', 'NIFTI', 'REFACED_NIFTI']
    with xnat.connect(param.host, user=param.user, password=param.password) as session:
        scan = session.projects[param.project].experiments[param.experiment].scans[param.scan]
        for resource in reface_resources:
            try:
                if resource in scan.resources:
                    logging.debug(f'Deleting existing reface resource: {resource} on scan {param.scan} in '
                                  f'experiment {param.experiment}')
                    scan.resources[resource].delete()
            except Exception as e:
                logging.error(f'Error deleting existing reface resource: {resource}: {e} on scan {param.scan} in '
                              f'experiment {param.experiment}')


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
    result = subprocess.run(command)
    print(f"mri_reface returned with exit code: {result.returncode}", flush=True)
    return result


def stage_output_files(input_dir, output_dir, pattern):
    # Move files from input_dir to output_dir
    for file in glob.glob(f'{input_dir}/{pattern}'):
        shutil.move(file, output_dir)


if __name__ == '__main__':
    print(f"Command line call: {' '.join(sys.argv)}", flush=True)
    start_time = time.time()
    main()
    minutes, seconds = divmod((time.time() - start_time), 60)
    print(f"Execution time: {int(minutes)}:{int(seconds)} (minutes:seconds)", flush=True)
