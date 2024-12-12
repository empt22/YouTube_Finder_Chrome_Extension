
# https://skillshats.com/blogs/how-to-use-the-youtube-api-with-python-a-step-by-step-guide/
#https://docs.python.org/3/library/functions.html#open


import pandas as pd
from io import StringIO
import numpy as np


## libraries
from googleapiclient.discovery import build
import os
from youtube_transcript_api import YouTubeTranscriptApi

# need to have this saved in Heroku
API_KEY = 'myKey_myKey'

# URL is https://www.youtube.com/@naturepbs
# sometimes there is no @ sign https://www.youtube.com/bbctravelshow
# handle name without @ symbol
#CHANNEL_HANDLE = 'naturepbs'  # worked, but many of first few don't have transcripts
#CHANNEL_HANDLE = 'KQEDDeepLook'  # worked
#CHANNEL_HANDLE = 'RoadshowPBS'  # not worked
#CHANNEL_HANDLE = 'PBSNewsHour'  # worked

#CHANNEL_HANDLE = 'MotorTrendWatch' # didn'g work
#CHANNEL_HANDLE = 'pbsspacetime' # didn't work
#CHANNEL_HANDLE = 'BBCStudios'  # only returned one video
#CHANNEL_HANDLE = 'bbctravelshow'    # didn't work


# create the YouTube client
youtube = build('youtube', 'v3', developerKey=API_KEY)

# Saving .txt file for a video , including id, title, transcript in a .txt file
def save_video_caption(video_id, title) :

    file_location = 'video_captions_1212'
    dir_fd = os.open(file_location, os.O_RDONLY)

    # have the path
    def opener(path, flags):
        return os.open(path, flags, dir_fd=dir_fd)

    # return different values depending on wheter saving captions succeeds
    return_value = -1

    # for this video, savee data
    with open('video_'+video_id+'.txt', 'w', opener=opener) as f:
        # start with title/id even if transcript not found
        print(f"Title: {title}" + "\n", file=f)
        print(f"Video ID: {video_id}" + "\n", file=f)

        # try to get a transcript, and print every line
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return_value = 1
            for entry in transcript:
                #print(f"{entry['start']}: {entry['text']}", file=f)
                print(f"{entry['text']}" + "\n", file=f)
        # if no transcript, say why
        except Exception as e:
            #print("No transcript available ", e  , file = f)
            return_value = 0
            #print("No transcript for "  + video_id)

    # steps to take depending on return value
    #print("return_value", return_value)

    # if transcript wasn't found, will return a 0 and 
    if return_value ==0 :
        if os.path.exists(file_location+'/'+'video_'+video_id+'.txt'):
            #print("removing...")
            os.remove(file_location+'/'+'video_'+video_id+'.txt')
    
    # closing the directory
    os.close(dir_fd)  

    return return_value



##### get the CHANNEL_ID from CHANNEL_HANDLE

def get_video_list(input_channel_handle, num_results) :
    # Use the "channels" endpoint to retrieve the CHANNEL_ID by handle
    response = youtube.channels().list(
        part='id',
        forUsername=input_channel_handle
    ).execute()

    print("step 1")

    # try again if forUsername does not work with handles - from examples
    if 'items' not in response or not response['items']:
        response = youtube.search().list(
            part='snippet',
            q=f'@{input_channel_handle}',
            type='channel'
        ).execute()


    print("step 2")

    # finding the channel ID
    if 'items' in response and response['items']:
        channel_id = response['items'][0]['id'] if 'id' in response['items'][0] else response['items'][0]['snippet']['channelId']
        print(f"Channel ID: {channel_id}")
    else:
        print("Channel not found.")


    print("step 3")

    ##### get the list of videos from CHANNEL_ID
    # the playlist ID
    channel_response = youtube.channels().list(
        part='contentDetails',
        id=  channel_id  
    ).execute()

    print("step 4")

    # based on channel_id
    uploadsPlaylist = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    print("step 5")
    # pull most recent 10 videos from the uploads playlist
    itemsInPlaylist = youtube.playlistItems().list(
        part='snippet', playlistId=uploadsPlaylist, maxResults=num_results #23  
    ).execute()


    print("step 6")
    # p
    print("creating channel play list")

    return itemsInPlaylist


#channelPlaylist = get_video_list("PBSNewsHour")  # not using
#channelPlaylist = get_video_list("NationalParkDiaries") # doens't work
#channelPlaylist = get_video_list("nationalparkdiaries")

#channelPlaylist = get_video_list("NatGeo")  #doesn't works
#channelPlaylist = get_video_list("natgeo")  #doesn't works
#channelPlaylist = get_video_list("BBCTravelShow")  #BBCTravelShow # doesn't work
#channelPlaylist = get_video_list("bbctravelshow") 


# Create a sample DataFrame
df = pd.DataFrame({
    'video_ID': ['3pRiQ1Lnfjo', 'I2dHYSbH0a4', 'XXD6oK1b_vk', 'Nr7gSfylUOo', 'slSFN1Ka8_g', '9kqAxENnizI'],
    'order_in_BM25_Index': [2,3,1,0,5,4],   ##[1, 1, 1, 1, 1, 1],
    'Title': ["Attenborough's Life Journey | PBS Nature Trailer"
        , 'Young Lioness Learns to Hunt Giraffes'
        , 'Extraordinary Lion Behavior Caught on Camera'
        , "San Diego: America’s Wildest City | PBS NATURE Documentary"
        , "Capturing San Diego: America's Wildest City"
        , "Desert Lion Cubs Hunt at Night"
        ],
    'included_in_default': [1, 1, 1, 1, 1, 1],
})

start_df = df[0:0]

### channels to use
channelPlaylist = get_video_list("bonappetit",15)  # works

# Getting the titles and video IDs
print('___________finding recent videos_____\n')
for item in channelPlaylist['items']:
    title = item['snippet']['title']
    video_id = item['snippet']['resourceId']['videoId']
    print(f"Title: {title}, Video ID: {video_id}")

    # call function to save save video captions for the video found
    outresult = save_video_caption(video_id, title) 

    if outresult == 1 :
        # add info to dataframe for each video
        to_add_df  =  pd.DataFrame({ 'video_ID' : [video_id], 'order_in_BM25_Index': [1], 'Title': [title], 'included_in_default': [1] })
        start_df = pd.concat([start_df, to_add_df])

    print(outresult)
print('___________end finding recent videos_____\n')

channelPlaylist = get_video_list("KQEDDeepLook",15)  #works

# Getting the titles and video IDs
print('___________finding recent videos_____\n')
for item in channelPlaylist['items']:
    title = item['snippet']['title']
    video_id = item['snippet']['resourceId']['videoId']
    print(f"Title: {title}, Video ID: {video_id}")

    # call function to save save video captions for the video found
    outresult = save_video_caption(video_id, title) 
    
    if outresult == 1 :
        # add info to dataframe for each video
        to_add_df  =  pd.DataFrame({ 'video_ID' : [video_id], 'order_in_BM25_Index': [1], 'Title': [title], 'included_in_default': [1] })
        start_df = pd.concat([start_df, to_add_df])

    print(outresult)
print('___________end finding recent videos_____\n')

channelPlaylist = get_video_list("naturepbs", 25)  #works, but lots have transcripts diasabled

# Getting the titles and video IDs
print('___________finding recent videos_____\n')
for item in channelPlaylist['items']:
    title = item['snippet']['title']
    video_id = item['snippet']['resourceId']['videoId']
    print(f"Title: {title}, Video ID: {video_id}")

    # call function to save save video captions for the video found
    outresult = save_video_caption(video_id, title) 

    if outresult == 1 :
        # add info to dataframe for each video
        to_add_df  =  pd.DataFrame({ 'video_ID' : [video_id], 'order_in_BM25_Index': [1], 'Title': [title], 'included_in_default': [1] })
        start_df = pd.concat([start_df, to_add_df])

    print(outresult)
print('___________end finding recent videos_____\n')


print(start_df)
print(len(start_df))

local_file_name = "table_of_video_id2.csv"
start_df.to_csv(local_file_name, index=False)


