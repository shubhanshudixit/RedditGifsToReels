import cv2
import requests
import random as rng
import pandas as pd
import os
from tqdm import tqdm

#Clear the temp folder before starting
folder_path = 'tmp'
for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)
    try:
        if os.path.isfile(file_path):
            os.unlink(file_path)
            print(f'Deleted {file_path}')
    except Exception as e:
        print(f'Failed to delete {file_path}. Reason: {e}')

def download_gif(url,save_name):
    print("URL ", url)
    path = "tmp/"+save_name+".gif"
    with open(path, 'wb') as f:
        f.write(requests.get(url).content)

global clip_ori

# Load up the Pickle File
raw_data = pd.read_pickle("cat_gif_list")

# Choose a random gif from the system
gif_choose = rng.randint(0,(len(raw_data) - 2))

clip_ori = raw_data.iloc[gif_choose]['Orientation']

print('Orientation = ',raw_data.iloc[gif_choose]['Orientation'])
print('Col_Qud = ',raw_data.iloc[gif_choose]['Col_Qud'])
print('Hom_Cat = ',raw_data.iloc[gif_choose]['Hom_Cat'])

# Filter the required Dataset
filtered_df = raw_data[
    (raw_data['Orientation'] == raw_data.iloc[gif_choose]['Orientation'])
    & (raw_data['Col_Qud'] == raw_data.iloc[gif_choose]['Col_Qud'])
    & (raw_data['Hom_Cat'] == raw_data.iloc[gif_choose]['Hom_Cat'])
]
# Start a Making Loop
clip_num = 0
done_flag = True
curr_dur = 0
clip_len = 45
gif_used = []
dur_arr = []

while(done_flag):
    # Choose a random clip from the filtered data
    c_num  = rng.randint(0,(len(filtered_df) - 1))
    # Make sure you pickup a new gif everytime
    if c_num in gif_used or (filtered_df.iloc[c_num]['Dur_Cat'] == -1) or (filtered_df.iloc[c_num]['Dur_Cat'] == 3):
        rng_flg = True
    else :

        rng_flg = False
    while (rng_flg):
        c_num = rng.randint(0, (len(filtered_df) - 1))
        if c_num in gif_used or (filtered_df.iloc[c_num]['Dur_Cat'] == -1) or (filtered_df.iloc[c_num]['Dur_Cat'] == 3):
            rng_flg = True
        else:
            rng_flg = False
    gif_used.append(c_num)
    # Figure out the duration category and update the duration using loops
    print("Hom Cat of the Gif = ",filtered_df.iloc[c_num]['Dur_Cat'])
    #if filtered_df.iloc[c_num]['Dur_Cat'] == 1:
        #curr_dur = curr_dur + 5
        #dur_arr.append(5)
    #elif filtered_df.iloc[c_num]['Dur_Cat'] == 2:
        #curr_dur = curr_dur + 10
        #dur_arr.append(10)
    #else:
        #curr_dur = curr_dur + filtered_df.iloc[c_num]['Duration']
        #dur_arr.append(filtered_df.iloc[c_num]['Duration'])
    curr_dur = curr_dur + filtered_df.iloc[c_num]['Duration']
    dur_arr.append(filtered_df.iloc[c_num]['Duration'])
    # Move to the next Clip
    clip_num = clip_num + 1;
    print("Clip #",clip_num," | URL = ",filtered_df.iloc[c_num]['URL']," | Clip Duration = ",filtered_df.iloc[c_num]['Duration']," | Dur_Cat = ",filtered_df.iloc[c_num]['Dur_Cat']," | Clip Number = ",c_num)
    if curr_dur > clip_len :
        done_flag = False

# Create a Gaussian blur kernel with a size of 25x25 and a standard deviation of 10
kernel_size = (25, 25)
sigma = 10
kernel = cv2.getGaussianKernel(kernel_size[0], sigma)
kernel = kernel * kernel.T

# Clip is Defined ->
print("Gifs = ",gif_used)
print("Durations = ",dur_arr)
print("Clip Duration = ",curr_dur)
print("Clips Used = ",clip_num)

##########################
# Define the Output File #
##########################
# Define the output filename and codec
output_filename = "final/reel.mp4"
codec = 'mp4v'
# Define the output resolution and frame rate
output_resolution = (1080, 1920)
frame_rate = 60
# Define the output video bitrate (8 Mbps)
bitrate = 8000000
# Create a VideoWriter object with the output filename, fourcc code, frame rate, and new frame size
fourcc = cv2.VideoWriter_fourcc(*codec)
output_video = cv2.VideoWriter(output_filename, fourcc, frame_rate, output_resolution)
# Set the output video bitrate
output_video.set(cv2.CAP_PROP_FOURCC, fourcc)
output_video.set(cv2.CAP_PROP_BITRATE, bitrate)


clips = []
# Work with Clips
for i in range(0,len(gif_used)):
    gif_num = gif_used[i]
    # Download the file
    download_gif(filtered_df.iloc[gif_num]['URL'], str(i) )
    # Load the Gif
    gif_loc = "tmp/"+str(i)+".gif"
    chosen_clip = cv2.VideoCapture(gif_loc)
    ori = clip_ori
    # Get the frame size and frame rate of the input video
    frame_size = (int(chosen_clip.get(cv2.CAP_PROP_FRAME_WIDTH)), int(chosen_clip.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    if ori == "horizontal":
        frame_size = (int(chosen_clip.get(cv2.CAP_PROP_FRAME_HEIGHT)), int(chosen_clip.get(cv2.CAP_PROP_FRAME_WIDTH)))
    # Determine the width and height
    if frame_size[0] > output_resolution[0]:  # Video is broader
        sc = output_resolution[0] / frame_size[0]
    #elif frame_size[0] <= output_resolution[0] / 2:
    elif frame_size[0] <= (output_resolution[0] * 0.7):
        sc = output_resolution[0] / frame_size[0]
    else:
        sc = 1
    new_w = min(int(sc * frame_size[0]),output_resolution[0])
    new_h = min(int(sc * frame_size[1]),output_resolution[1])
    # Determine Top left
    top_left_x = int((output_resolution[0] / 2) - new_w / 2)
    top_left_y = int((output_resolution[1] / 2) - new_h / 2)
    gif_fps = chosen_clip.get(cv2.CAP_PROP_FPS)
    # print("Orignal FPS = ",gif_fps)
    # Set the desired frame rate for the final video
    final_fps = frame_rate
    # Compute the ratio between the desired and original frame rates
    frame_rate_ratio = int(final_fps / gif_fps)
    tot_frames = int( (frame_rate_ratio*gif_fps) * dur_arr[i] )
    print("\nStarting Work on Clip #",i+1,"| Total Frames  = ",tot_frames," | OG FPS = ",gif_fps," | FPS Ratio = ",frame_rate_ratio,)
    for j in range(tot_frames):
    #while chosen_clip.isOpened():
        ret, frame = chosen_clip.read()
        if not ret:
            break
        # If the video is horizontal, rotate it
        if ori == "horizontal":
            # Rotate the frame by the specified angle
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        # Make the blurred frame to the set resolution
        b_frame = cv2.resize(frame, output_resolution)
        # Apply the Gaussian blur to the frame
        b2_frame = cv2.filter2D(b_frame, -1, kernel)
        b2_frame = cv2.applyColorMap(b2_frame, cv2.COLORMAP_BONE)
        frame = cv2.resize(frame, (new_w, new_h))
        b2_frame[top_left_y:top_left_y + new_h, top_left_x:top_left_x + new_w] = frame
        # Duplicate each frame by the ratio between the desired and original frame rates
        k = 0
        for k in range(frame_rate_ratio):
            output_video.write(b2_frame)
    chosen_clip.release()
output_video.release()
