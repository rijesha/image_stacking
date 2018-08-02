import os
import cv2
import numpy as np
from time import time
import argparse
import yaml
import cv2
#from PIL import Image
#import PIL
import re
import collections
import tifffile

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split('(\d+)', text) ]

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('calib_file', help='calibration file path')
    parser.add_argument('input_dir', help='Input directory of images ()')
    parser.add_argument('--compression', help='Level of Tiff Compression (0 is no compression)')

    args = parser.parse_args()

    if args.compression is not None:
        compress_val = int(args.compression)
    else:
        compress_val = 0

    if not os.path.exists(args.calib_file):
        print("ERROR {} not found!".format(args.calib_file))
        exit()

    with open(args.calib_file, 'r') as f:
        matrices = yaml.load(f)

    for m in matrices:
        matrices[m] = np.array(matrices[m])

    image_folder = args.input_dir
    if not os.path.exists(image_folder):
        print("ERROR {} not found!".format(image_folder))
        exit()

    file_list = os.listdir(image_folder)
    file_list = [os.path.join(image_folder, x)
                 for x in file_list if x.endswith(('.jpg', '.png','.bmp'))]
    
    file_list.sort(key=natural_keys)

    sortedFrames = {}
    for f in file_list:
        t = f.split("/")[-1][:-4].split("_")
        cam_num = t[-1]
        frame_num = int(t[-3])
        if frame_num in sortedFrames:
            temp = sortedFrames[frame_num]
            temp.append(f)
            sortedFrames[frame_num] = temp
        else:
            sortedFrames[frame_num] = [f]
    
    for key in sorted(sortedFrames.iterkeys()):
        frames = []
        frames_names = sortedFrames[key]
        for file in frames_names:
            image = cv2.imread(file,1)

            t = file.split("/")[-1][:-4].split("_")
            t = t[-2] + "_" + t[-1]
            w, h, _ = image.shape
            image = cv2.warpPerspective(image, matrices[t], (h, w))
            frames.append(image)

        print("saving: " + sortedFrames[key][0][:-9] + "aligned.tiff")
        with tifffile.TiffWriter(sortedFrames[key][0][:-9] + "aligned.tiff") as tiff:
            for img in frames:
                tiff.save(img,  compress=compress_val)



