### libraries
from flask import Flask, request, jsonify
from flask_cors import CORS

# need to use S3 bucket
import pickle
import pandas as pd
from io import StringIO
import numpy as np

# for Youtube API
from googleapiclient.discovery import build

# didn't actually work
import requests

# for Youtube, AWS
from youtube_transcript_api import YouTubeTranscriptApi # this doesn't work in Heroku, returned 200
import os
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# for python BM25
# was in requirements as whoosh==2.7.4
#import whoosh # difficult to save in S3 bucket, decided not to use
import rank_bm25
from rank_bm25 import BM25Okapi

##### for Flask in Heroku
app = Flask(__name__)
CORS(app) # to enable CORS

##### Special access variables and connecting to S3
# these are the special secret vars stored in Heroku
aws_access_key_id = os.getenv('AWS_ACCESS_KEY')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
region_name = os.getenv('AWS_REGION')

# only one bucket being used, no sub
my_bucket = os.getenv('AWS_BUCKET_NAME')

# YouTube API
my_YT_API_KEY = os.getenv('YOUTUBE_API_KEY')


# these are using  the special config vars saved in Heroku
s3_client = boto3.client(
	's3',
	aws_access_key_id = aws_access_key_id,
	aws_secret_access_key = aws_secret_access_key,
	region_name = region_name
)


s3_resource = boto3.resource(
	's3',
	aws_access_key_id = aws_access_key_id,
	aws_secret_access_key = aws_secret_access_key,
	region_name = region_name
)


#### Function definitions 

# this deind''t work
def save_video_transcript1(video_id):

	print("video id", video_id)
	# may not always get a transcript
	try:
		print("Step 1 transcript")
		transcript = YouTubeTranscriptApi.get_transcript(video_id)
		return_value = 0
		#for entry in transcript:
		#	print(f"{entry['text']}" + "\n", file=f)

		print("Step 2 transcript")
		# list iteratio nover transcript
		fullTranscript = '\n'.join([f"{item['start']}: {item['text']}" for item in transcript])

		print("Step 3 transcript")
		# video file name
		video_file_name = f"video_v2_{video_id}.txt"

		print("Step 4 transcript")
		# place in bucket
		s3_client.put_object(Bucket=my_bucket, Key=video_file_name, Body=fullTranscript)
		print("saved new video file")

		# need to add a segment  to update the python df with new non-default video
		# open df
		# save new line
		# save df

	
	# no transcript, either not enabled, not in English, could be other
	except Exception as e:
		return_value = 0
		print("failed to get transcript")
		print(f"Failed: {e}")

	return return_value 

# new version with API
def save_video_transcript(video_id):
	api_key = my_YT_API_KEY
	youtube = build('youtube', 'v3', developerKey=api_key)
	return return_value

# need to save the python pandas table of video data info
def df_save_s3(mydf, file_name_in_bucket):
    df_csv = mydf.to_csv(index=False)  

    # put in into same bucket as others
    s3_client.put_object(Bucket=my_bucket, Key=file_name_in_bucket, Body=df_csv)
    return 1

# load df back from bucket
def df_load_s3(file_name_in_bucket):
    response = s3_client.get_object(Bucket=my_bucket, Key=file_name_in_bucket)
    df_csv = response['Body'].read().decode('utf-8')
    df = pd.read_csv(StringIO(df_csv)) 
    return df

# create the video list (file names of transcripts)
def create_video_list():
	
	#s3_resource = boto3.resource('s3')

	# listing the video files
	all_files_bucket = s3_resource.Bucket(my_bucket)

	# loading the dataframe with all video info (title, etc)
	video_df = df_load_s3("table_of_video_id.csv")

	# start the empty video list and the count
	video_list = []
	count_n = 0 

	# loop over all objects, only process "video" text files
	for my_bucket_object in all_files_bucket.objects.all():
		#print(my_bucket_object.key)
		bucket_obj_name = my_bucket_object.key
		if bucket_obj_name[:5]=='video':
			# get the 11-digit video_d
			video_id_curr = bucket_obj_name[6:17]
			print("video id", video_id_curr)

			# update the dataframe so order num will match the corpus
			video_df.loc[video_df['video_ID'] == video_id_curr, 'order_in_BM25_Index'] = count_n

			# add to the corpus and increment up
			video_list.append(my_bucket_object.key)
			count_n = count_n + 1

	# save new version of the video table
	df_save_s3(video_df, "table_of_video_id.csv")

	return video_list

# createing the rank_bm25 index (won't recreate on every run)
def create_save_bm25_index():

	# list of all "video_" files currenlty in bucket
	all_video_txt_files = create_video_list()

	# need a corpus, will come from Youtube transcirpts
	corpus = [
	]
	
	# add each video transcript to the corpus
	for transcript_file_name in all_video_txt_files:
		yt_file = openFileS3(transcript_file_name)
		corpus.append(yt_file)

	# from the BM25 documentation
	tokenized_corpus = [doc.split(" ") for doc in corpus]

	# will be saved to be used again
	bm25 = BM25Okapi(tokenized_corpus)

	# use dumps, not dump, to get it into bytes not file, ready for S3 saving
	bm25_pickle = pickle.dumps(bm25)
	corpus_pickle = pickle.dumps(corpus)

	# placing in bucket, same name, same bucket, every time
	s3_client.put_object(Bucket=my_bucket, Key = "bm25_index", Body=bm25_pickle)
	s3_client.put_object(Bucket=my_bucket, Key = "corpus", Body=corpus_pickle)

	return 1

# open the already created bm25 index
def load_bm25_index():
	# read it from bucket
	bm25ind_s3_obj = s3_client.get_object(Bucket = my_bucket, Key = "bm25_index")

	# s3 blob is 'Body'
	bm25_pickle =bm25ind_s3_obj['Body'].read()

	# loads to undo dumps
	bm25_index = pickle.loads(bm25_pickle)

	return bm25_index

# open the already created corpus
def load_corpus():
	# read it from bucket
	corpus_s3_obj = s3_client.get_object(Bucket = my_bucket, Key = "corpus")

	# s3 blob is 'Body'
	corpus_pickle =corpus_s3_obj['Body'].read()

	# loads to undo dumps
	corpus = pickle.loads(corpus_pickle)

	return corpus


# for opening a file from S3
def openFileS3(my_file_name):

	#print("opening a file")

	# bucket storage as Bucket/Key
	fileobject = s3_client.get_object(Bucket = my_bucket, Key = my_file_name)

	# get the text dat
	file_text= fileobject['Body'].read().decode('utf-8')

	return file_text

# home page, not really using this
@app.route("/")
def home_view():
		return "<h1>Welcome to my website EMPT...</h1>"

# just hello world attempt, not really using this
# will listen for GET requests at /hello endpoint, ethe default is GET
@app.route('/hello', methods=['GET'])
def hello_world():
    return "<h1>Goodbye :)</h1>"

# Main method - this is what they python file will do in respnse to click of the "Go" button
# POST means data from chrome extension is "posted" to the flask app, as an input
@app.route('/send-data', methods=['POST'])
def send_data():
    try:
        data = request.get_json()  
        if not data:
            return jsonify({'error': 'No data received'}), 400

		### INPUTS ###
		# can use url to add a new channel
        url = data.get('url')

		# this is the full text displayed on screen
        content = data.get('content')

		### UPDATES ###
        # index/table creation won't happen every time button is clicked, will
        # need a new index each time a custom video added, but this feature not enabled
        new_index = 0
        if new_index ==1 :
            create_save_bm25_index()

            
		### CURRENT QUERY ###
        # use current website as a query
        start_website_content = content[0:200]
        query_website = content  #[0:10000]
        tokenized_webInput = query_website.split(" ")

        # load the index already created
        bm25_fromS3 = load_bm25_index()
        corpus_fromS3 = load_corpus()

        # these are the videos
        video_df = df_load_s3("table_of_video_id.csv")

        # use the loaded index to get doc scores for each doc (ranking)
        doc_scores_webInput = bm25_fromS3.get_scores(tokenized_webInput)
        #print("length of scores", len(doc_scores_webInput))

        # scores will be in same order as corpus		
        bm_id = np.arange(0,len(doc_scores_webInput),1)

        # label the scores with doc ID		        
        bm_scores_df = pd.DataFrame({
            'bm_25scores': doc_scores_webInput,
            'doc_id': bm_id
        })
		
        # join BM scores with doc info, and sort by descding scor
        df_alldocs_info = bm_scores_df.merge(video_df, left_on='doc_id', right_on='order_in_BM25_Index')
        df_alldocs_info_sort = df_alldocs_info.sort_values(by='bm_25scores', ascending=False, ignore_index = True)

        # get top n, although do need to match up to title/url of doc
        top1_webInput = bm25_fromS3.get_top_n(tokenized_webInput, corpus_fromS3, n=1)

	    # check if "youtube" in url
        is_youtube = False
        if "youtube" in url.lower():
            is_youtube = True
		
		### OUTPUTS ###
        return jsonify({
			"result": {
				"url": "placeholder", #df_alldocs_info_sort["Title"][0], ###start_website_content[:50],
				"is_youtube": is_youtube,
				"word_output": "placeholder", #top1_webInput[:10],  #start_file_contents  #"testing 2" #start_file_contents # "hello testing"
				"n1_video_id": df_alldocs_info_sort["video_ID"][0],
				"n1_video_title": df_alldocs_info_sort["Title"][0],
				"n2_video_id": df_alldocs_info_sort["video_ID"][1],
				"n2_video_title": df_alldocs_info_sort["Title"][1],
				"n3_video_id": df_alldocs_info_sort["video_ID"][2],
				"n3_video_title": df_alldocs_info_sort["Title"][2]
			}
		}),200  # indicating success in JSON, though not really used

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500

