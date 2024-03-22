import csv


class ScanClassifierCSV:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = self._read_csv()
        self.header = self.data[0]
        self.scan_row = None

    def _read_csv(self):
        with open(self.file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            return list(reader)

    def _find_scan_row(self, experiment, scan):
        # If there is only one row of data, that's the scan row
        if len(self.data) - 1:
            return 1
        # Otherwise, search for the scan row
        else:
            for row_index in len(self.data) - 1:
                if self._get_value('experiment', row_index) == experiment \
                        and self._get_value('scan', row_index) == scan:
                    return row_index
        return None

    def _get_value(self, column_label, row_number):
        if column_label in self.header:
            return self.data[row_number][self.header.index(column_label)]
        else:
            raise ValueError(f"Label {column_label} not found in header.")

    # Return mri_reface compatible imType: T1|T2|FLAIR|FDG|PIB|FBP|TAU|CT
#     Hierarchy of imtype
#       Body part:
#           if Head, brain, or none then Perform reface
#           if Any other body part then Stop container:
#           maybe state an error about body part in the container log
#       Modality:
#           If CT = label Imtype CT
#           If PET = refer to radiopharmaceutical
#               Imtype PIB = Amyloid, PIB, AV45, florbetapir, AV-45
#               Imtype fdg = fdg,
#               Imtype Tau = AV-1451, flortaucipir, AV1451, AV-1451, tau
#           If MRI = refer to scan classifier "label"
#               Initiate type with "flair":
#                   *flair* = Imtype flair
#               Imtype t2 = contains t2 but not flair
#               Imtype T1 = contains T1, mprage
    def get_im_type(self, experiment, scan):
        im_type = None
        print(f"Finding scan {scan} in experiment {experiment}.")
        self.scan_row = self._find_scan_row(experiment, scan)
        print(f"Scan row: {self.scan_row}")
        if self.scan_row is not None:
            if self._get_value('0018_0015', self.scan_row).lower() in ['head', 'brain', 'neuro']:
                if self._get_value('0008_0060', self.scan_row) == 'CT':
                    im_type = 'CT'
                elif self._get_value('0008_0060', self.scan_row) == 'PET':
                    radiopharmaceutical = self._get_value('0054_0016', self.scan_row)
                    if radiopharmaceutical in ['Amyloid', 'PIB', 'AV45', 'florbetapir', 'AV-45']:
                        im_type = 'PIB'
                    elif radiopharmaceutical.lower() in ['fdg']:
                        im_type = 'FDG'
                    elif radiopharmaceutical in ['AV1451', 'AV-1451', 'flortaucipir', 'tau']:
                        im_type = 'TAU'
                    else:
                        raise ValueError(f"PET Radiopharmaceutical {radiopharmaceutical} not supported.")
                elif self._get_value('0008_0060', self.scan_row) in ['MRI', 'MR']:
                    label = self._get_value('labels1', self.scan_row)
                    im_type = 'FLAIR'
                    if 't2' in label.lower() and 'flair' not in label.lower():
                        im_type = 'T2'
                    elif 't1' in label or 'mprage' in label:
                        im_type = 'T1'
            else:
                raise ValueError(f"Body part {self._get_value('0018_0015', self.scan_row)} not supported.")
        else:
            raise ValueError(f"Scan: {scan} and experiment: {experiment} not found in CSV: {self.file_path}.")
        if im_type is None:
            raise ValueError(f"Imtype not found for scan {scan} in experiment {experiment}.")

        print(f"Found mri_reface imType: {im_type}")
        return im_type

