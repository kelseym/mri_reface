cp Dockerfile.base Dockerfile && \
./command2label.py xnat/command.json  >> Dockerfile && \
docker build -t xnat/mri_reface:1.6 -t registry.nrg.wustl.edu/docker/nrg-repo/mri_reface:1.6 .
rm Dockerfile
