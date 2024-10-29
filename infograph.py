""" Display an infographic of the images with groundtruth and most similar MIXVPR result and scores
Created in 2024, Authored by Java Terry (33javalava@gmail.com)
Designed as part of EGH400-1 and EGH400-2 project at QUT
"""
import numpy as np
import matplotlib.pyplot as plt
import os
import cv2
import scipy.io as sio


def get_ground_truth(groundtruth_path: str, query_img_no: int):
    mat_file = sio.loadmat(groundtruth_path)
    truth_data = mat_file['truth']
    num_images = truth_data.shape[0]
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
    try:
        groundtruth_nos = image_groups[query_img_no]
    except KeyError:
        print(f'No groundtruth for query image {query_img_no}')
        groundtruth_nos = None
    return groundtruth_nos

def get_loop_candidates(similarity_matrix: np.ndarray, query_index: int, top_k: int, frame_distance: int):
    array = similarity_matrix[query_index, :]
    sorted_indices = np.argsort(array)
    top_K_indices = sorted_indices[-top_k:]
    filtered_indices = [i for i in top_K_indices if not (i == query_index or (query_index - frame_distance < i < query_index + frame_distance))]
    mix_vpr_no = filtered_indices[-1]
    mix_vpr_score = array[mix_vpr_no]
    return mix_vpr_no, mix_vpr_score

def plot_read_imgs(query_img, database_img, mix_vpr_img, query_img_no, database_img_no, database_img_score, mix_vpr_no, mix_vpr_score, groundtruth_no, groundtruth_nos, groundtruth_img_score):
    plt.figure(figsize=(12, 6))
    plt.subplot(2, 2, 1)
    plt.imshow(query_img)
    plt.title(f'Query Image {query_img_no}')
    plt.axis('off')
    plt.subplot(2, 2, 2)
    plt.imshow(database_img)
    plt.title(f'Database Image {database_img_no} with a MIXVPR score of {database_img_score}')
    plt.axis('off')
    plt.subplot(2, 2, 3)
    plt.imshow(mix_vpr_img)
    plt.title(f'MixVPR Image {mix_vpr_no} with score {mix_vpr_score}')
    plt.axis('off')
    if not groundtruth_no:
        print('No groundtruth for query image')
        plt.subplot(2, 2, 4)
        plt.title('Groundtruth Image not found')
        plt.axis('off')
    else:
        groundtruth_img_file = os.path.join(image_location, '{:06d}'.format(groundtruth_no) + '.png')
        groundtruth_img = cv2.imread(groundtruth_img_file, cv2.IMREAD_COLOR)
        plt.subplot(2, 2, 4)
        plt.imshow(groundtruth_img)
        plt.title(f'Groundtruth Image {groundtruth_no} with {len(groundtruth_nos)} other images and a score of {groundtruth_img_score}')
        plt.axis('off')
    plt.show()

def plot_info(query_img_no, database_img_no, similarity_mat, frame_distance):
    groundtruth_nos = get_ground_truth(groundtruth_path, query_img_no)
    groundtruth_no = groundtruth_nos[0] if groundtruth_nos else None
    mix_vpr_no, mix_vpr_score = get_loop_candidates(similarity_mat, query_img_no, frame_distance)
    database_img_score = similarity_mat[query_img_no, database_img_no]
    groundtruth_img_score = similarity_mat[query_img_no, groundtruth_no] if groundtruth_no else None

    query_img_file = os.path.join(image_location, '{:06d}'.format(query_img_no) + '.png')
    database_img_file = os.path.join(image_location, '{:06d}'.format(database_img_no) + '.png')
    mix_vpr_img_file = os.path.join(image_location, '{:06d}'.format(mix_vpr_no) + '.png')
    query_img = cv2.imread(query_img_file, cv2.IMREAD_COLOR)
    database_img = cv2.imread(database_img_file, cv2.IMREAD_COLOR)
    mix_vpr_img = cv2.imread(mix_vpr_img_file, cv2.IMREAD_COLOR)

    plot_read_imgs(query_img, database_img, mix_vpr_img, query_img_no, 
                   database_img_no, database_img_score, mix_vpr_no, mix_vpr_score, 
                   groundtruth_no, groundtruth_nos, groundtruth_img_score)


def main():
    query_img_no = 2629
    database_img_no = 877
    image_location = '/home/java/AnyFeature-Benchmark/KITTI/05/rgb/'
    groundtruth_path = '/home/java/AnyFeature-Benchmark/KITTI/KITTI_GroundTruth/kitti05GroundTruth.mat'
    similarity_mat = np.loadtxt('/home/java/MixVPR/similarity_matrix_05.txt', delimiter='\t')

    frame_distance = 15 #how many frames around the query image to exclude from potential loop candidates
    #plot_info(query_img_no, database_img_no, similarity_mat)
    #plot_info(50, database_img_no, similarity_mat)
    plot_info(1500, 1900, similarity_mat, frame_distance)


if __name__ == '__main__':
    main()
