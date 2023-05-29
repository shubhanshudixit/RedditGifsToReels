#   This Script ->
#   1. Pulls gifs from the Subreddit "PixelArt"
#   2. Analyzes them with respect to their size, duration, orientation, most common colors, and homogeneity
#   3. Creates a Pickle file to save the raw info
#       3.a. Also, a csv file to hold the permalink to check is the gif has already been used
#   4. It pulls the reddit login credentials for a "creds" file ( Nothing encrypted )

#   Libraries
import json
import praw
import pandas as pd
import requests
from requests.adapters import HTTPAdapter, Retry
import time
from PIL import Image
from io import BytesIO
import numpy as np
from scipy.cluster.vq import kmeans, vq
from scipy.spatial import KDTree
from webcolors import CSS3_HEX_TO_NAMES , hex_to_rgb

#   Variables
time_filter = "all"
posts_limit = 1000
pickle_fname = "raw_pickle_1"
permalink_fname = "perma_link_1.csv"

#   Functions
def convert_rgb_to_names(rgb_tuple):
    # a dictionary of all the hex and their respective names in css3
    css3_db = CSS3_HEX_TO_NAMES
    names = []
    rgb_values = []
    for color_hex, color_name in css3_db.items():
        names.append(color_name)
        rgb_values.append(hex_to_rgb(color_hex))

    kdt_db = KDTree(rgb_values)
    distance, index = kdt_db.query(rgb_tuple)
    return names[index]

def get_gif_info(url):
    print("URL ", post.url)
    s = requests.Session()
    retries = Retry(total=25,
                    backoff_factor=0.5,
                    status_forcelist=[500, 502, 503, 504]
                    )
    s.mount(url, HTTPAdapter(max_retries=retries))
    response = s.get(url, timeout=5)
    image = Image.open(BytesIO(response.content))
    width, height = image.size
    ratio = width / height
    if ratio < 0.9:
        ori = 'vertical'
    elif ratio < 1.2 :
        ori = 'square'
    else:
        ori = 'horizontal'
    n_frames = image.n_frames
    palette = image.palette.getdata()[1]
    duration = image.info['duration']
    total_duration  = (n_frames * duration) / 1000

    # parse the binary string into a NumPy array
    palette = np.array(bytearray(palette), dtype=np.uint8)

    # reshape the array into a 3-column array (for red, green, and blue values)
    palette = palette.reshape(-1, 3)

    # calculate the standard deviation of the RGB values
    rgb_stddev = np.std(palette, axis=0)

    # calculate the average standard deviation of the RGB values
    homogeneity = np.mean(rgb_stddev)
    # common colors calculation
    rgb_values = np.array(palette).reshape(-1, 3)
    try :
        n_clusters = 50
        centroids, variance = kmeans(rgb_values.astype(float), n_clusters)
    except :
        try :
            n_clusters = 15
            centroids, variance = kmeans(rgb_values.astype(float), n_clusters)
        except :
            try :
                n_clusters = 2
                centroids, variance = kmeans(rgb_values.astype(float), n_clusters)
            except :
                pass
    code, distance = vq(rgb_values, centroids)
    n_distinct_colors = len(np.unique(code))
    unique, counts = np.unique(code, return_counts=True)
    index = np.argsort(counts)[::-1][:5]
    most_common_colors = centroids[index]
    # rgb to name
    named_colors = []
    for x in most_common_colors:
        named_colors.append(convert_rgb_to_names(x))
    # return
    return width, height, ori, n_frames, total_duration, homogeneity , n_distinct_colors, named_colors ,most_common_colors

# Open the creds file and read credentials for reddit login
with open("creds", "r") as file:
    data = json.load(file)

c_id = data["c_id"]
c_sec = data["c_sec"]
c_username = data["c_username"]
c_password = data["c_password"]
c_user_agent = data["c_user_agent"]

# Pandas DF for Post Info
post_lists = pd.DataFrame(columns = [
    'URL',
    'PermaLink',
    'Width',
    'Height',
    'Orientation',
    'Num_of_frames',
    'Duration',
    'Homogenity',
    'Num_of_Distinct_Cols',
    'N_Col',
    'Col',
    'Used'
])

# Log into Reddit
reddit = praw.Reddit(client_id=c_id,
                    client_secret=c_sec,
                    username=c_username,
                    password=c_password,
                    user_agent=c_user_agent)


# List of SubReddits to pickup from
sub_reddit = "PixelArt"
iteration_start = time.time()
# List all Top Posts
top_post = reddit.subreddit(sub_reddit).top(time_filter=time_filter, limit=posts_limit)
iteration_end = time.time()
print("Time taken to pull posts lists :", iteration_end - iteration_start, "seconds")
# Basic Counters
i = 0
j = 0
for post in top_post:
    j = j + 1
    if ('.gif' in post.url) and ('i.redd.it' in post.url) and (post.score >= 1000):
        iteration_start = time.time()
        i = i + 1
        print("Post # ", i)
        print("Reached Post # ", j)
        dets = get_gif_info(post.url)
        post_lists = post_lists.append(
            {
                'URL': post.url,
                'PermaLink': post.permalink,
                'Width' : dets[0],
                'Height' : dets[1],
                'Orientation' : dets[2],
                'Num_of_frames': dets[3],
                'Duration' : dets[4],
                'Homogenity' : round(dets[5]),
                'Num_of_Distinct_Cols' : dets[6],
                'N_Col': dets[7],
                'Col': dets[8],
                'Used': "False"
            },
                       ignore_index=True)
        iteration_end = time.time()
        print("Time Taken for Pulling Post Info  :", iteration_end - iteration_start, "seconds")
        print("\n\n")
        time.sleep(0.5)

# Create a new DF only for PermaLink
pd_csv = post_lists[['PermaLink', 'Used']].copy()

# Write data to files
pd_csv.to_csv(permalink_fname, index=False)
post_lists.to_pickle(pickle_fname)