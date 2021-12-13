"""Script excerpted and modified from iCLOTS,
a free software created for the analysis of common hematology workflow image data

Script used for data analysis in manuscript:
"Pathologic Mechanobiological Interactions between Red Blood Cells and Endothelial Cells
Directly Induce Vasculopathy in Iron Deficiency Anemia" (Caruso, 2022)

Author: Meredith Fay, Lam Lab, Georgia Institute of Technology and Emory University
Last updated: 2021-12-13

Script measures relative deformability index (RDI) of RBCs passing through
a specialized biophysical flow cytometer device (Rosenbluth, 2008)

This script analyzes a directory of video files pre-cropped to the small channel region of interest (ROI)
Script deformability_single_wroi.py guides user to select an ROI of a single video

Please see github repository README.md for a description of inputs and outputs

"""

# Import libraries
# File management
from tkinter import filedialog
import os
import glob
import shutil

# Number, file, and image management
import cv2  # Computer vision/image processing
import numpy as np  # For array management
import pandas as pd  # For database management
import pims

# Particle tracking
import trackpy as tp
import warnings
warnings.filterwarnings("ignore", module="trackpy")

# Labeling and plotting results
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt


# USER SHOULD EDIT THESE IMPORTANT VARIABLES
fps = 25  # Frames per second, pulling directly from a video can be inaccurate, especially if resized
pixum = 250/200  # Ratio of pixels per micron
size = 41  # Maximum diameter of tracked cells, err on the high side if unsure
minmass = 10000  # Minimum intensity of a tracked cell - roughly, area * 255
# If you'd like graphical data and the images labeled with the tracked cells, set as "True"
labelimg = True  # Recommended

# Choose directory using a file dialog
folder = filedialog.askdirectory()
dir = os.path.basename(folder)

# Create new directory for analysis results
dir_video = folder + '/Analysis'
if os.path.exists(dir_video):
    shutil.rmtree(dir_video)
os.makedirs(dir_video)
os.chdir(dir_video)

# Create an excel writer to save numerical analysis results to
writer = pd.ExcelWriter(dir + '_analysis.xlsx', engine='openpyxl')  # Writer

# Create a list of videos within the directory
videos = sorted(glob.glob(folder + '/*.avi'))

# Create background subtractor for analysis
fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows=False)

for vid in videos:

    # Extract filename for saving results
    filename = os.path.basename(vid).split(".")[0]
    print('Currently analyzing ' + filename)  # Useful to mark progress on a long script

    # Defining a function to grayscale the image
    @pims.pipeline
    def gray(image):
        return image[:, :, 1]

    # Create a frames object using pims
    frames = gray(pims.PyAVReaderTimed(vid))
    frame_count = len(frames)

    # Create a small kernel for morphological operations
    kernel = np.ones((5, 5), np.uint8)
    # Create a list of frames with background removed
    bg_frames = []
    for i in range(frame_count):
        frame = fgbg.apply(frames[i])  # Apply background removal
        closing = cv2.morphologyEx(frame, cv2.MORPH_CLOSE, kernel)  # Morphological closing operation
        bg_frames.append(closing.copy())

    # Find width of each frame, useful for data quality criteria
    [ROW_h, ROI_w] = bg_frames[0].shape
    ROI_w_um = ROI_w / pixum  # Width converted to microns

    # Begin trackpy tracking analysis
    tp.quiet()
    f = tp.batch(bg_frames[:frame_count], size, minmass=minmass, invert=False); # Detect particles/cells
    # Link particles, cells into dataframe format
    # Search range criteria: must travel no further than 1/3 the channel length
    # Memory here signifies a particle/cell cannot "disappear" for more than one frame
    tr = tp.link_df(f, search_range=ROI_w/3, memory=1, adaptive_stop=1, adaptive_step=0.95)
    # Filter stubs criteria requires a particle/cell to be present for at least three frames
    t_final = tp.filter_stubs(tr, 3)

    # Series of vectors for final results dataframe
    p_i = []  # Particle index
    f_start = []  # Start frame, frame where cell first detected
    f_end = []  # End frame, frame where cell last detected
    dist = []  # Distance traveled
    time = []  # Time for travel
    sizes = []  # Cell size
    t_rdi = pd.DataFrame()  # Create dataframe
    # For each particle, calculate RDI and save data for results dataframe:
    for p in range(t_final['particle'].iloc[-1]):
        df_p = tr[tr['particle'] == p]  # Region of trackpy dataframe corresponding to individual particle index
        x_0 = df_p['x'].iloc[0]  # First x-position
        x_n = df_p['x'].iloc[-1]  # Last x-position
        f_0 = df_p['frame'].iloc[0]  # First frame number
        f_n = df_p['frame'].iloc[-1]  # Last frame number
        s = df_p['mass'].mean() / 255  # Area of cell (pixels)
        d = (x_n - x_0) / pixum  # Distance (microns)
        t = (f_n - f_0) / fps  # Time (seconds)
        # Criteria to save cells as a valid data point:
        # Must travel no shorter than 1/3 the length of channel
        # Must travel no further than length of channel
        if d < ROI_w_um and d > ROI_w_um / 3:
            t_rdi = t_rdi.append(df_p, ignore_index=True)  # Save trackpy metrics
            # Append data for particle/cell
            p_i.append(p)
            f_start.append(f_0)
            f_end.append(f_n)
            dist.append(d)
            time.append(t)
            sizes.append(s)

    # Calculate RDI by dividing distance by time (um/sec)
    rdi = []
    rdi = np.asarray([u / v for u, v in zip(dist, time)])

    # Orgnize time, location, and RDI data in a list format
    list = pd.DataFrame(
        {'particle': p_i,
         'start frame': f_start,
         'end frame': f_end,
         'transit time': t,
         'distance traveled': d,
         'rdi': rdi,
         'size': sizes
        })

    # Renumber particles 0 to n
    list['particle'] = np.arange(len(list))
    uniqvals = t_rdi['particle'].unique()
    newvals = np.arange(len(uniqvals))
    for val in newvals:
        uniqval = uniqvals[val]
        t_rdi['particle'] = t_rdi['particle'].replace(uniqval, val)

    # Final data to excel
    # Filename cropped to prevent excel errors caused by a sheet name over 30 characters
    if len(filename) > 20:
        filename = filename[:20]
    list.to_excel(writer, sheet_name = filename + ', all', index=False)  # RDI
    t_rdi.to_excel(writer, sheet_name= filename +', trackpy', index=False)  # Trackpy outputs

    # If user would like graphical data and frames labeled with particle numbers
    # Computationally expensive but useful, so recommended
    if labelimg is True:
        # Create a directory for that image
        dir_folder = dir_video + '/' + filename
        if os.path.exists(dir_folder):
            shutil.rmtree(dir_folder)
        os.makedirs(dir_folder)
        os.chdir(dir_folder)

        # Graphical data, RDI histogram
        fig = plt.figure()
        plt.hist(rdi, 25, facecolor='blue')
        plt.title(filename)
        plt.xlabel(u'RDI (\u03bcm/s)')
        plt.ylabel('n cells')
        plt.savefig(filename + '_histogram.png', dpi=300)
        plt.cla()

        # Graphical data, RDI vs size scatterplot
        fig = plt.figure()
        plt.scatter(sizes, rdi, color='blue')
        plt.title(filename)
        plt.xlabel('size (pix)')
        plt.ylabel(u'RDI (\u03bcm/s)')
        plt.savefig(filename + '_scatter.png', dpi=300)
        plt.cla()

        # Read video as an OpenCV video object
        cap = cv2.VideoCapture(vid)
        # Label
        success, image = cap.read()
        count = 1
        while success:
            # New filename: original, frame, frame number
            image_name = filename + '_frame_' + str(count).zfill(5)
            success, image = cap.read()
            if image is not None:
                f = t_rdi[t_rdi['frame'] == count]
                PILimg = Image.fromarray(image)  # Set up image to label
                drawimg = ImageDraw.Draw(PILimg)  # " "
                for i in range(len(f)):
                    drawimg.text((f['x'].iloc[i], f['y'].iloc[i]), str(f['particle'].iloc[i]),
                                 fill="#ff0000")  # Label
                PILimg.save(image_name + "_labeled.png")  # Save image
            count += 1

os.chdir(dir_video)  # Return to original analysis directory

# Save and close excel file writer
writer.save()
writer.close()