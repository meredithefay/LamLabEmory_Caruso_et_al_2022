"""Script excerpted and modified from iCLOTS,
a free software created for the analysis of common hematology workflow image data

Script used for data analysis in manuscript:
"Pathologic Mechanobiological Interactions between Red Blood Cells and Endothelial Cells
Directly Induce Vasculopathy in Iron Deficiency Anemia" (Caruso, 2022)

Author: Meredith Fay, Lam Lab, Georgia Institute of Technology and Emory University
Last updated: 2021-12-13

Script crops a video to a selected region of interest (ROI)

Useful for pre-processing videos to be used with script deformability_directory.py

Please see github repository README.md for additional details

"""

# Import libraries
import cv2
from tkinter import filedialog
import os
import shutil
import glob

# Choose file using a file dialog
filepath = filedialog.askopenfilename(filetypes=[(".avi file", "*.avi")])
filename = os.path.basename(filepath).split(".")[0]
dir = os.path.dirname(filepath)
os.chdir(dir)

# New file name
nfile_name = filename + '_croppedroi.avi'

# Read video
cap = cv2.VideoCapture(filepath)
ret, frame = cap.read()  # First frame
fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Video writer
fps = cap.get(cv2.cv2.CAP_PROP_FPS)

# OpenCV does not resize windows for choosing an ROI to fit the screen
# Often these files have large frames to capture detail
# Here, we resize the original image by a factor of 2 to fit on screen
# Final ROI coordinates will be scaled appropriately
wn = int(cap.get(3)/2)
hn = int(cap.get(4)/2)
b = cv2.resize(frame, (wn, hn), fx=0, fy=0, interpolation=cv2.INTER_CUBIC)

# Choose ROI
fromCenter = False  # Set up to choose as a drag-able rectangle rather than a rectangle chosen from center
r = cv2.selectROI("Image", b, fromCenter)
ROI_x = int(r[0]) * 2 # Take result of selectROI and put into a variable
ROI_y = int(r[1]) * 2 # " "
ROI_w = int(r[2]) * 2 # " "
ROI_h = int(r[3]) * 2 # " "

out = cv2.VideoWriter(nfile_name, fourcc, fps, (ROI_w, ROI_h))

while True:
    ret, frame = cap.read()
    if ret == True:
        b = frame[ROI_y: (ROI_y + ROI_h), ROI_x: (ROI_x + ROI_w)]
        out.write(b)
    else:
        break

cap.release()
out.release()
cv2.destroyAllWindows()