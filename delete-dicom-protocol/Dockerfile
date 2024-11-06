FROM openjdk:11
ADD ./dicom-edit6-6.6.0-jar-with-dependencies.jar dicom-edit.jar
ADD ./remove-protocol-name.txt remove-protocol-name.txt
LABEL org.nrg.commands="[{\"name\": \"delete-protocol-tag\", \"description\": \"Removes Protocol Name and Series Description DICOM tags from input.\", \"version\": \"1.1\", \"type\": \"docker-setup\", \"command-line\": \"java -jar dicom-edit.jar -s remove-protocol-name.txt -i /input -o /output\", \"image\": \"registry.nrg.wustl.edu/docker/nrg-repo/delete-protocol-tag:1.1\", \"generic-resources\": {\"RESERVED\": \"1\"}}]"
