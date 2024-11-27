cp Dockerfile.base Dockerfile && \
./command2label.py xnat/command.json  >> Dockerfile && \
docker build -t xnat/mri_reface:dev -t registry.nrg.wustl.edu/docker/nrg-repo/mri_reface:dev .
rm Dockerfile
