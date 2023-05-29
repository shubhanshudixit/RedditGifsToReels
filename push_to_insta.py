import instagrapi
from instagrapi import Client as InstaClient
#from instagrapi.types import Location, MediaRendition
from instagrapi.exceptions import ClientError
import requests
from moviepy.video.io.VideoFileClip import VideoFileClip

# Set up InstaClient
insta_username = #######################
insta_password = ################
insta_client = InstaClient()
insta_client.login(insta_username, insta_password)

# Search for the x most popular "lofi" song
search_results = insta_client.search_music('moon lofi beats')
music_track = search_results[3]

# The path to the video file
video_path = 'final/reel.mp4'
# Create a VideoFileClip object for the video
clip = VideoFileClip(video_path)
# Get the duration of the video in seconds
clip_duration = clip.duration
clip.close()

# Upload video to Instagram as a Reel with the chosen song attached
video_duration = clip_duration  # set duration to 60 seconds

#insta_client.clip_upload(path=video_path,caption="Test")
insta_client.clip_upload_as_reel_with_music(path = video_path,caption="Test 6",track=music_track)

# Logout from the client
insta_client.logout()
