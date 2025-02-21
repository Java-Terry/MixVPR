""" Script to calcuate the similarity matrix of a database and query images using a trained model."""

import glob
import os
from typing import Tuple

import torch
from PIL import Image
from torch.utils import data
import numpy as np
import torchvision.transforms as tvf
from tqdm import tqdm
import cv2

import matplotlib.pyplot as plt

from main import VPRModel


class BaseDataset(data.Dataset):
    """Dataset with images from database and queries, used for inference (testing and building cache).
    """

    def __init__(self, img_path):
        super().__init__()
        self.img_path = img_path

        # path to images
        img_path_list = glob.glob(self.img_path + '*.png', recursive=True)
        self.img_path_list = sorted(img_path_list)
        
        assert len(self.img_path_list) > 0, f'No images found in {self.img_path}'

    def __getitem__(self, index):
        img = load_image(self.img_path_list[index])
        return img, index

    def __len__(self):
        return len(self.img_path_list)


class InferencePipeline:
    def __init__(self, model, dataset, feature_dim, batch_size=4, num_workers=4, device='cuda'):
        self.model = model
        self.dataset = dataset
        self.feature_dim = feature_dim
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.device = device

        self.dataloader = data.DataLoader(self.dataset,
                                          batch_size=self.batch_size,
                                          shuffle=False,
                                          num_workers=self.num_workers,
                                          pin_memory=True,
                                          drop_last=False)

    def run(self, split: str = 'db') -> np.ndarray:

        if os.path.exists(f'./LOGS/global_descriptors_{split}.npy'):
            print(f"Skipping {split} features extraction, loading from cache")
            return np.load(f'./LOGS/global_descriptors_{split}.npy')

        self.model.to(self.device)
        with torch.no_grad():
            global_descriptors = np.zeros((len(self.dataset), self.feature_dim))
            for batch in tqdm(self.dataloader, ncols=100, desc=f'Extracting {split} features'):
                imgs, indices = batch
                imgs = imgs.to(self.device)

                # model inference
                descriptors = self.model(imgs)
                descriptors = descriptors.detach().cpu().numpy()

                # add to global descriptors
                global_descriptors[np.array(indices), :] = descriptors

        # save global descriptors
        np.save(f'/home/java/MixVPR/logs/global_descriptors_{split}.npy', global_descriptors)
        return global_descriptors


def load_image(path):
    image_pil = Image.open(path).convert("RGB")

    # add transforms
    transforms = tvf.Compose([
        tvf.Resize((320, 320), interpolation=tvf.InterpolationMode.BICUBIC),
        tvf.ToTensor(),
        tvf.Normalize([0.485, 0.456, 0.406],
                      [0.229, 0.224, 0.225])
    ])

    # apply transforms
    image_tensor = transforms(image_pil)
    return image_tensor


def load_model(ckpt_path):
    # Note that images must be resized to 320x320
    model = VPRModel(backbone_arch='resnet50',
                     layers_to_crop=[4],
                     agg_arch='MixVPR',
                     agg_config={'in_channels': 1024,
                                 'in_h': 20,
                                 'in_w': 20,
                                 'out_channels': 1024,
                                 'mix_depth': 4,
                                 'mlp_ratio': 1,
                                 'out_rows': 4},
                     )

    state_dict = torch.load(ckpt_path)
    model.load_state_dict(state_dict)

    model.eval()
    print(f"Loaded model from {ckpt_path} Successfully!")
    return model


def simluarity_matrix(q_matrix: np.ndarray,
                    db_matrix: np.ndarray) -> np.ndarray:
    # compute similarity matrix
    similarity_matrix = np.matmul(q_matrix, db_matrix.T)  # shape: (num_query, num_db)

    #Set the images in the future to 0 similarity
    num_rows, num_cols = similarity_matrix.shape
    for i in range(num_rows):
        for j in range(num_cols):
            if j > i:  # above the diagonal line
                similarity_matrix[i, j] = 0 #set to 1

    return similarity_matrix

def save_sim_matrix(similarity_matrix: np.ndarray, path: str):
    np.savetxt(path, similarity_matrix, fmt='%1.4f', delimiter='\t')

def get_loop_canditates_from_text(file_path: str,
                                query_index: int,
                                top_k: int = 10,
                                sim_threshold: int = 0.8):
    similarity_matrix = np.loadtxt(file_path, delimiter='\t')
    filtered_indices = get_loop_candidates(similarity_matrix, query_index, top_k, sim_threshold)
    return filtered_indices


def get_loop_candidates(similarity_matrix: np.ndarray, 
                    query_index: int,
                    top_k: int,
                    sim_threshold: int):
    
    top_k_matches = np.argsort(-similarity_matrix, axis=1)[:, :top_k]  # shape: (num_query_images, 10)
    db_indices = top_k_matches[query_index]
    scores = similarity_matrix[query_index, db_indices]
    filtered_indices = db_indices[scores >= sim_threshold]

    return filtered_indices.tolist()

def plot_sim(simularity_mat: np.ndarray):
    plt.imshow(simularity_mat, cmap='viridis', interpolation='nearest')
    plt.colorbar(label='Similarity')
    plt.xlabel('Frame Index')
    plt.ylabel('Frame Index')
    plt.title('Similarity Matrix')
    plt.show()
   

    

def main():
    # load images
    query_path = '/home/java/AnyFeature-Benchmark/KITTI/08/rgb/'         # path to query images folder path
    datasets_path = '/home/java/AnyFeature-Benchmark/KITTI/08/rgb/'      # path to database images folder path

    # #assert query_path == '' and datasets_path == '', 'Please specify the path to the query and datasets'

    # query_dataset = BaseDataset(query_path)
    # database_dataset = BaseDataset(datasets_path)

    # # load model # './LOGS/resnet50_MixVPR_4096_channels(1024)_rows(4).ckpt')
    # model = load_model('/home/java/MixVPR/resnet50_MixVPR_4096_channels(1024)_rows(4).ckpt')

    # # set up inference pipeline
    # database_pipeline = InferencePipeline(model=model, dataset=database_dataset, feature_dim=4096)
    # query_pipeline = InferencePipeline(model=model, dataset=query_dataset, feature_dim=4096)

    # # run inference
    # db_global_descriptors = database_pipeline.run(split='db')  # shape: (num_db, feature_dim)
    # query_global_descriptors = query_pipeline.run(split='query')  # shape: (num_query, feature_dim)

    # # calculate top-k matches
    # simluarity_mat = simluarity_matrix(q_matrix=query_global_descriptors, db_matrix=db_global_descriptors)

    # filtered_indices = get_loop_candidates(simluarity_mat, query_index=1000, top_k=10, sim_threshold=0.8)
    # save_sim_matrix(simluarity_mat, 'similarity_matrix_08.txt')
    # new_indices = get_loop_canditates_from_text('/home/java/MixVPR/similarity_matrix_05.txt', query_index=100, top_k=10, sim_threshold=0.5)
    # print(new_indices)

    similarity_mat = np.loadtxt('/home/java/MixVPR/similarity_matrix_08.txt', delimiter='\t')
    plot_sim(similarity_mat)

    import code
    code.interact(local=locals())


if __name__ == '__main__':
    main()
