# Launch the mri_reface command on a remote XNAT
import argparse
import csv
import sys
import time
import getpass
import requests


# ~ Sample launch command:
# python mri_reface_launcher.py --xnat_host http://localhost --xnat_user admin --xnat_pass admin --project Test --csv_input sample.csv --command_wrapper_id 12
def main():
    try:
        params = parse_command_line_parameters()

        # Get Jsession from XNAT
        xnat_session = start_xnat_session(params)

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
    response = xnat_session.post(launch_string, json={'scan': scan})
    if response.status_code != 200:
        raise Exception(
            f'Failed to launch command wrapper {params.command_wrapper_id} on scan {scan} with status code {response.status_code}')
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
    parser.add_argument('--command_wrapper_id', help='XNAT command wrapper ID', required=True)

    args = parser.parse_args()

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


if __name__ == '__main__':
    print(f"Command line call: {' '.join(sys.argv)}", flush=True)
    start_time = time.time()
    main()
    minutes, seconds = divmod((time.time() - start_time), 60)
    print(f"Execution time: {int(minutes)}:{int(seconds)} (minutes:seconds)", flush=True)
