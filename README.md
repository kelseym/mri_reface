# XNAT Container Service mri_reface

## Command line options

```
xnat_reface.py
--mri_reface_script run_mri_reface.sh 
--csv /Users/Kelsey/Projects/Containers/mri_reface/workspace/sample.csv 
--input /Users/Kelsey/Projects/Containers/mri_reface/workspace/sample_in 
--output /Users/Kelsey/Projects/Containers/mri_reface/workspace/sample_out 
--experiment=M00812503_20171127144401 --scan=9 
--mri_reface_opts '-verbose=1'
```

## Sample command
/usr/bin/mlrtapp/run_mri_reface.sh /input /output -imType CT

## mri_reface options

```
-verbose <0|1>
   default=1.
 -saveQCRenders <0|1>
   If set to 1, saves .png files before/after de-facing in the output directory, for QC purposes. default=1.
 -regFile <file .txt or .mat>
   Overrides the affine registration between input and MCALT_FaceTemplate. If not specified, one will be generated using reg_aladin. Designed to read matrix save formats from: Matlab/SPM (.txt ascii or .mat binary), reg_aladin (.txt ascii), ITK/ANTs (.txt ascii), or FLIRT (.mat ascii).
 -threads <count>
   How many threads to use? Default: 1. Only very small portions of the software can use multiple threads, so users should expect only very modest speed gains from multithreading.
 -matchNoise <0|1>
   Should we add noise to the replacement face to try to match the input image?  Default: 1 (yes). In versions before 0.3, this feature did not exist, so you can get the old behavior with -matchNoise 0
 -altReg <0|1>
   Default: 0. If coreg failed, try clearing your output directory and re-running with -altReg 1. Internally, coreg runs with two different masks, then the one with the lowest cost function is used. Running with altReg 1 will use the other option of the two, which often times will fix things if it didn't work the first time. Running with this in general is not advised. Use it only to fix failures with specific inputs.

 -faceMask <PATH>
   Default: ''. Overrides the mask defining face regions to replace. This image MUST be in the voxel space of MCALT_FaceTemplate_T1.nii. Voxel value 1 = face; voxel value 2 = air behind the head potentially containing wraped face-parts; voxel value 3 = ears
   Warning: Using this option may produce de-faced images that do NOT offer adequate protection from re-identification
```