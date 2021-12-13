# LamLabEmory_Caruso_et_al_2022
Scripts used for data analysis in manuscript: "Pathologic Mechanobiological Interactions between Red Blood Cells and Endothelial Cells Directly Induce Vasculopathy in Iron Deficiency Anemia" (Caruso, 2022)

Scripts are designed to analyze video data of cells transiting a specialized microfluidic device in order to measure relative deformability (Rosenbluth, 2008).

My authorship contribution: developed data analysis methods and performed data analysis.

Script excerpted and modified from iCLOTS, a free software created for the analysis of common hematology workflow image data.

Tracking methods adapted from Trackpy library.

## Scripts included in repository
- deformability_single_wroi.py: analyze a single video, allows user to choose a region of interest (ROI)
- deformability_directory.py: analyze a folder of videos pre-cropped to an ROI
- crop_video_to_roi.py: crop any video to an ROI, useful for preprocessing videos to be analyzed with deformability_directory.py

## Inputs, outputs, methods

Users are guided to choose a directory or an individual .avi file using a file dialog window. Scripts are designed to analyze .avi files only.

Users should edit input parameters based on their own individual data files:

```
# USER SHOULD EDIT THESE IMPORTANT VARIABLES
fps = 25  # Frames per second, pulling directly from a video can be inaccurate, especially if resized
pixum = 250/200  # Ratio of pixels per micron
size = 41  # Maximum diameter of tracked cells, err on the high side if unsure
minmass = 10000  # Minimum intensity of a tracked cell - roughly, area * 255, err on low side if unsure
# If you'd like graphical data and the images labeled with the tracked cells, set as "True"
labelimg = True  # Recommended
```

Script uses Trackpy to locate and track individual cells (particles). Script requires the following criteria to ensure highest quality data points: 
- Cells that travel no further than 1/3 of the channel width at a time
- Cells tracked for at least 1/3 the width of the channel
- Cells tracked for no further than the width of the channel
- Cells present for at least three frames
Ideally ~75% of cells will be tracked. If the majority of cells are not being tracked, troubleshoot experimental protocol by reducing pump flow speed.

Outputs:
- If labelimg parameter is set to True:
  - Each frame of each video with each tracked cell labeled with an ID, consider quality criteria
  - (video name) histogram.png, an automatically generated graph of RDI measurements
  - (video name) scatterplot.png, an automatically generated graph of size vs. RDI measurements
- Excel file with two sheets per video:
  - (video name), all: RDI and size measurements per cell, ID corresponds to labeled images
  - (video name), trackpy: additional details from the trackpy algorithm

These outputs are organized in new analysis directories, located in the directory or the directory of the file selected. I suggest always exporting the labeled images - while computationally expensive, it provides valuable troubleshooting information.

## Help and contributing
Contributions are always welcome! Submit a pull request, contact me directly at mfay7@gatech.edu, or contact the Lam lab coding team directly at lamlabcomputational@gmail.com. Please also feel free to reach out via email for assistance. The Lam lab is happy to provide microfluidic mask design files upon request.

## References
Original "biophysical flow cytometer" manuscript:
- Rosenbluth MJ, Lam WA, Fletcher DA. Analyzing cell mechanics in hematologic diseases with microfluidic biophysical flow cytometry. Lab Chip. 2008 Jul;8(7):1062-70. doi: 10.1039/b802931h. Epub 2008 Jun 5. PMID: 18584080; PMCID: PMC7931849.

Trackpy version used:
- Allan, Daniel B., Caswell, Thomas, Keim, Nathan C., van der Wel, Casper M., & Verweij, Ruben W. (2021). soft-matter/trackpy: Trackpy v0.5.0 (v0.5.0). Zenodo. https://doi.org/10.5281/zenodo.4682814

Core feature-finding and linking algorithms that trackpy is based on:
- Crocker, J. C., & Grier, D. G. (1996). Methods of Digital Video Microscopy for Colloidal Studies. J. Colloid Interf. Sci., 179(1), 298–310. http://doi.org/10.1006/jcis.1996.0217
