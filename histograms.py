""" Script to visualise when and how many loop closures are detected. Assumed ORBSLAM ran with printstatements
Created in 2024, Authored by Java Terry (33javalava@gmail.com)
Designed as part of EGH400-1 and EGH400-2 project at QUT
"""

import numpy as np
import matplotlib.pyplot as plt
import re
import scipy.io as sio


def Fetch_ground_truth_loop_closures(gnd_truth_location: str)
    mat_file = sio.loadmat(gnd_truth_location + sequence + 'GroundTruth.mat')
    truth_data = mat_file['truth']
    return np.sum(truth_data, axis=1)

def Fetch_Orbslam_loop_closures(orbslam_location: str):
    orbslam_dict = {}
    with open(orbslam_location, 'r') as file:
        for line in file:
            match = re.search(r'DetectLoopCandidates: mnFrameID\s*=\s*(\d+)\s+inital matches:\s*(\d+)\s+1st Filter matches.*?=\s*(\d+)\s+2nd Filter matches.*?=\s*(\d+)\s+3rd Filter matches.*?=\s*(\d+)', line)
            if match:
                mnFrameID = int(match.group(1))
                initial_matches = int(match.group(2))
                first_filter_matches = int(match.group(3))
                third_filter_matches = int(match.group(5))
                # Store the extracted numbers
                orbslam_dict[mnFrameID] = {
                    'initial': initial_matches,
                    'one_filter': first_filter_matches,
                    '3rd_filter': third_filter_matches
                }
    ORBmnFramneID = sorted(orbslam_dict.keys())  # Sort ORBmnFramneID for better plotting
    initial_matches = [orbslam_dict[mnFrameID]['initial'] for mnFrameID in ORBmnFramneID]
    first_filter_matches = [orbslam_dict[mnFrameID]['one_filter'] for mnFrameID in ORBmnFramneID]
    third_filter_matches = [orbslam_dict[mnFrameID]['3rd_filter'] for mnFrameID in ORBmnFramneID]
    return np.array(ORBmnFramneID)

def Fetch_MixVPR_loop_closures(mix_vpr_location: str):
    mix_vpr_dict = {}
    with open(mix_vpr_location, 'r') as file:
        for line in file:
            match = re.search(r'vpFilteredLoopCandidate:\s*mnFrameId\s*=\s*(\d+)\s+inital matches:\s*(\d+)\s+vp 1st filtered matches:\s*(\d+)\s+vp 2nd filtered matches:\s*(\d+)', line)
            if match:
                mnFrameID = int(match.group(1))
                matches = int(match.group(2))
                one_filter = int(match.group(3))
                two_filter = int(match.group(4))

                # Store the extracted numbers
                mix_vpr_dict[mnFrameID] = {
                    'matches': matches,
                    'one_filter': one_filter,
                    'two_filter': two_filter,
                }
    MIXVPRmnFramneID = sorted(mix_vpr_dict.keys())  # Sort MIXVPRmnFramneID for better plotting
    mix_vpr_matches = [mix_vpr_dict[mnFrameID]['matches'] for mnFrameID in MIXVPRmnFramneID]
    one_filter = [mix_vpr_dict[mnFrameID]['one_filter'] for mnFrameID in MIXVPRmnFramneID]
    two_filter = [mix_vpr_dict[mnFrameID]['two_filter'] for mnFrameID in MIXVPRmnFramneID]
    return np.array(MIXVPRmnFramneID)



def Plot_ORB_n_GT(ORBmnFramneID, num_loop_closures): #ORBSLAM and GT
    bar_width = 0.5
    plt.figure(figsize=(10, 6))
    plt.bar(ORBmnFramneID + bar_width, first_filter_matches, bar_width, label='1st Filter Matches', color='green')
    plt.bar(ORBmnFramneID + 3 * bar_width, third_filter_matches, bar_width, label='3rd Filter Matches', color='red')
    plt.bar(np.arange(len(num_loop_closures)), num_loop_closures, label='Ground Truth Loop Closures', color='skyblue')
    plt.xlabel('Image Number')
    plt.ylabel('Number of Matches')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend()
    plt.tight_layout()
    plt.show()

def Plot_ORB(ORBmnFramneID):#ORBSLAM
    bar_width = 0.5
    plt.figure(figsize=(10, 6))
    ORBmnFramneID = np.array(ORBmnFramneID)
    plt.bar(ORBmnFramneID + bar_width, first_filter_matches, bar_width, label='1st Filter Matches', color='green')
    plt.bar(ORBmnFramneID + 3 * bar_width, third_filter_matches, bar_width, label='3rd Filter Matches', color='red')
    plt.xlabel('Frame Number')
    plt.ylabel('Number of Matches')
    plt.title('Matches per Key ID')
    plt.xticks(ORBmnFramneID[::100])  # Use ORBmnFramneID for x-ticks
    plt.legend()
    plt.tight_layout()
    plt.show()

def Plot_MIX_n_GT(MIXVPRmnFramneID, num_loop_closures, threashold):
    bar_width = 0.5
    plt.figure(figsize=(10, 6))
    plt.bar(np.arange(len(num_loop_closures)), num_loop_closures, label='Ground Truth Loop Closures', color='skyblue')
    plt.bar(MIXVPRmnFramneID, one_filter, label='Similarity Filter', color='green')
    plt.bar(MIXVPRmnFramneID, two_filter, label='Filter Connected Images', color='red')
    plt.xlabel('Image Number')
    plt.ylabel('Number of Matches')
    plt.title(f'Loop Candidates with MIXVPR, similarity threashold {threashold}')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend()
    plt.tight_layout()
    plt.show()

def Plot_Mix(MIXVPRmnFramneID, threashold):
    plt.figure(figsize=(10, 6))
    plt.bar(MIXVPRmnFramneID, one_filter, label='Similarity Filter', color='green')
    plt.bar(MIXVPRmnFramneID, two_filter, label='Filter Connected Images', color='red')
    plt.xlabel('Image Number')
    plt.ylabel('Number of Matches')
    plt.title(f'Loop Candidates with MIXVPR, similarity threashold {threashold}')
    plt.xticks(MIXVPRmnFramneID[::100])  # Use MIXVPRmnFramneID for x-ticks
    plt.legend()
    plt.tight_layout()
    plt.show()

def Plot_GT(num_loop_closures):
    ##Plot GROUND TRUTH numbers of loop colsoures
    plt.figure(figsize=(10, 6))
    plt.bar(np.arange(len(num_loop_closures)), num_loop_closures, color='skyblue', edgecolor='black')
    plt.title('Number of Ground Truth Loop Closures per Image')
    plt.xlabel('Image Number')
    plt.ylabel('Number of Matching Images (Ground Truth)')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()


def main():
    gnd_truth_location = '/home/java/AnyFeature-Benchmark/KITTI/KITTI_GroundTruth/kitti'
    sequence = '05'
    run = '00001'
    Mix_threashold = 0.2
    orbslam_location = '/home/java/VSLAM-LAB-Evaluation/exp_demo_anyfeature/KITTI/'+sequence+'/system_output_00000.txt'
    mix_vpr_location = '/home/java/VSLAM-LAB-Evaluation/exp_demo_anyfeature/KITTI/'+sequence+'/system_output_'+run+'.txt'
    num_loop_closures = Fetch_ground_truth_loop_closures(gnd_truth_location)
    ORBmnFramneID = Fetch_Orbslam_loop_closures(orbslam_location)
    MIXVPRmnFramneID = Fetch_MixVPR_loop_closures(mix_vpr_location)

    ## Plot
    Plot_ORB_n_GT(ORBmnFramneID, num_loop_closures)
    Plot_ORB(ORBmnFramneID)
    Plot_MIX_n_GT(MIXVPRmnFramneID, num_loop_closures, Mix_threashold)
    Plot_Mix(MIXVPRmnFramneID, Mix_threashold)
    Plot_GT(num_loop_closures)


if __name__ == '__main__':
    main()
