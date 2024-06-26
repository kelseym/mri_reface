# Launch the mri_reface command on a remote XNAT
import argparse
import csv
import sys
import time
import getpass
import requests


# ~ Sample launch command:
# python mri_reface_launcher.py --xnat_host http://localhost --xnat_user admin [--xnat_pass admin] --project Test --csv_input sample.csv [--xnat_scan_class_filename sample.csv]
def main():


    try:
        params = parse_command_line_parameters()

        # Get Jsession from XNAT
        xnat_session = start_xnat_session(params)

        # Get the wrapper ID
        if not params.command_wrapper_id:
            params.command_wrapper_id = get_wrapper_id(xnat_session, params.xnat_host, "mri_reface", "mri-reface-scan")

        # Get scans from CSV
        scans = getScans(xnat_session, params)

        for scan in scans:
            print(f"Launching mri_reface on {scan}...", flush=True)
            # Launch mri_reface on xnat
            launch_command_wrapper(xnat_session, params, scan)

    except csv.Error as e:
        sys.exit(f'Error parsing CSV file: {e}')
    except Exception as e:
        sys.exit(f'Error launching mri_reface: {e}')


def launch_command_wrapper(xnat_session, params, scan):
    launch_string = f'{params.xnat_host}/xapi/projects/{params.project}/wrappers/{params.command_wrapper_id}/root/scan/launch'
    response = xnat_session.post(launch_string,
                                 json={'scan': scan,
                                       'scan-class-file': '/archive/projects/'+params.project+'/resources/DICOM_LM_CLASSIFIER_OUTPUT/files/' + params.xnat_scan_class_filename})
    if response.status_code != 200:
        raise Exception(
            f'Failed to launch command wrapper {params.command_wrapper_id} on scan {scan} with status code {response.status_code}\n {response.text}')
    else:
        print(f"Launched mri_reface on {scan}", flush=True)
        print(f"Response: {response.text}", flush=True)

    return response.json()


def start_xnat_session(params):
    session = requests.Session()
    session.auth = (params.xnat_user, params.xnat_pass)

    # Test the connection
    response = session.get(params.xnat_host)

    if response.status_code != 200:
        raise Exception(f'Failed to connect to XNAT at {params.xnat_host} with status code {response.status_code}')

    return session


def parse_command_line_parameters():
    parser = argparse.ArgumentParser(description='XNAT mri_reface Launcher'
                                                 'This script will launch the mri_reface command on a remote XNAT')
    parser.add_argument('--xnat_host', help='XNAT host url', required=True)
    parser.add_argument('--xnat_user', help='XNAT username', required=True)
    parser.add_argument('--xnat_pass', help='XNAT password')
    parser.add_argument('--project', help='XNAT project ID', required=True)
    parser.add_argument('--csv_input', help='CSV file containing session and scan information'
                                            'Columns must include: experiment, scan', required=True)
    parser.add_argument('--xnat_scan_class_filename', help='XNAT Project Resource scan classification CSV filename, if different than csv_input filename.')
    parser.add_argument('--command_wrapper_id', help='XNAT command wrapper ID')

    args = parser.parse_args()

    if not args.xnat_scan_class_filename:
        print(f'No XNAT scan classification CSV file specified. '
              f'Using input CSV filename {args.csv_input} for scan classification.', flush=True)
        args.xnat_scan_class_filename = args.csv_input

    if not args.xnat_pass:
        args.xnat_pass = getpass.getpass('XNAT password: ')

    return args


def getScans(xnat_session, params):
    # Get experiment IDs
    exp_ids = get_experiment_ids(xnat_session, params)

    with open(params.csv_input, 'r') as f:
        reader = csv.DictReader(f)
        scans = []
        for row in reader:
            if row['experiment'] not in exp_ids:
                print(f"Experiment {row['experiment']} not found in XNAT.", flush=True)
                continue
            exp_id = exp_ids[row['experiment']];
            scans.append((get_scan_uri(xnat_session, params.project, exp_id, row['scan'])))
    return scans


def get_scan_uri(xnat_session, params, experiment, scan):
    return f'/archive/experiments/{experiment}/scans/{scan}'


def get_experiment_ids(xnat_session, params):
    label_id_map = {}
    url = f"{params.xnat_host}/data/archive/projects/{params.project}/experiments"
    response = xnat_session.get(url, json={'columns': "ID,label"})
    if response.status_code != 200:
        raise Exception(f'Failed to get experiments from XNAT at {params.xnat_host} with status code {response.status_code}')
    experiments = response.json()["ResultSet"]["Result"]
    for experiment in experiments:
        label_id_map[experiment['label']] = experiment['ID']
    return label_id_map

def get_wrapper_id(session, xnat_host, command_name, wrapper_name):
    # Send a GET request to the /xapi/commands endpoint
    response = session.get(f'{xnat_host}/xapi/commands')

    # Check the status code of the response
    if response.status_code != 200:
        raise Exception(f'Failed to get commands from XNAT at {xnat_host} with status code {response.status_code}')

    # Parse the JSON response
    commands = response.json()

    # Iterate over the commands
    for command in commands:
        # Check if the command name and wrapper name match the given parameters
        if command['name'] == command_name:
            # Iterate over the command's wrappers
            for wrapper in command['xnat']:
                # Check if the wrapper name matches the given parameter
                if wrapper['name'] == wrapper_name:
                    # If they match, return the wrapper ID
                    return wrapper['id']
    # If no matching command is found, raise an exception
    raise Exception(f'No command found with name {command_name} and wrapper name {wrapper_name}')

if __name__ == '__main__':
    print(f"Command line call: {' '.join(sys.argv)}", flush=True)
    start_time = time.time()
    main()
    minutes, seconds = divmod((time.time() - start_time), 60)
    print(f"Execution time: {int(minutes)}:{int(seconds)} (minutes:seconds)", flush=True)
