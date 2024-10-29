import scipy.io as sio
import numpy as np
import cv2 as cv
import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import math

sequence = '08'

# Load the .mat file
mat_file = sio.loadmat('/home/java/AnyFeature-Benchmark/KITTI/KITTI_GroundTruth/kitti'+ sequence + 'GroundTruth.mat')
## kittiXXGroundTruth.mat is a binary matrix with size of N x N, where N is the number of images. 
#Entry (i,j) of the matrix is 0 if image i and image j were taken at the different places. 
#When entry (i,j) is equal to 1, it indicates that image i and image j are regareded as the same place, i.e. a loop closure.
mat_file2 = sio.loadmat('/home/java/AnyFeature-Benchmark/KITTI/KITTI_GroundTruth/gnd_kitti'+ sequence + '.mat')
## gnd_kittiXX.mat lists, for each image in a sequence, the indices of images that are regarded as the same place.

truth_data = mat_file['truth']
gnd_data = mat_file2['gnd']


num_images = truth_data.shape[0]

# # Create a dictionary to store groups of images with loop closures
image_groups = {}

# Iterate through the binary matrix to identify images with loop closures
for i in range(num_images):
    for j in range(num_images):
        if truth_data[i, j] == 1 and i != j:
            if i not in image_groups:
                image_groups[i] = []
            if j not in image_groups:
                image_groups[j] = []
            image_groups[i].append(i)
            image_groups[i].append(j)
image_groups = {k: v for k, v in image_groups.items() if v} #remove nums
image_groups = {k: [x for x in v if x != k] for k, v in image_groups.items()} #remove self
unique_values = list(set(value for values in image_groups.values() for value in values)) #get frames with loop closures

import code
code.interact(local=dict(globals(), **locals()))

# # Display images in each group
# for group_id, image_indices in image_groups.items():
#     if len(image_groups[group_id]) > 2:
#         plt.figure(figsize=(12, 6))
#         num_images_in_group = len(image_indices)
#         for i, image_index in enumerate(image_indices, 1):
#             img_name = os.path.join('/home/java/AnyFeature-Benchmark/KITTI/'+ sequence +'/rgb', '{:06d}'.format(image_index) + '.png')
#             image = mpimg.imread(img_name)
#             plt.subplot(1, num_images_in_group, i)
#             plt.imshow(image)
#             plt.title(f'Image {image_index}')
#             plt.axis('off')
#         plt.show()



# visualise two images of same place
for item in gnd_data:
    array_data = item[0][0][0]  # Access the array
    if len(array_data) > 2 and array_data[0]-1+len(array_data)!=array_data[-1]:
        print(array_data)
        num_rows = math.ceil(len(array_data) / 2)
        num_cols = 2
        fig, axes = plt.subplots(num_rows, num_cols, figsize=(12, 3*num_rows))
        for idx, number in enumerate(array_data):
            number = number - 1
            img_name = os.path.join('/home/java/AnyFeature-Benchmark/KITTI/'+ sequence +'/rgb', '{:06d}'.format(number) + '.png')
            image = mpimg.imread(img_name)

            row_idx = idx // num_cols
            col_idx = idx % num_cols

            # Plot the image on the corresponding subplot
            axes[row_idx, col_idx].imshow(image)
            axes[row_idx, col_idx].axis('off')
           

        import code
        code.interact(local=dict(globals(), **locals()))
        # Adjust layout to prevent overlap of subplots
        plt.tight_layout()
        #plt.show()  # Display all subplots together

       
