This is a setup container designed to remove/delete the DICOM Protocol Name tag from a directory of DICOM files and pass them to another container. It is used to feed the mri_reface container, which fails on certain files with Protocol Name containing special characters.
This container will use DicomEdit and a static script.

