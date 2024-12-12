# YouTube Finder Chrome Extension
This Chrome extension helps you find YouTube videos from pre-selected channels (about nature and cooking) that relate to the current website you are browsing.

## Installation
1. Download this repository from the green "Code" button.
2. Open Chrome and go to `chrome://extensions/`.
3. Enable "Developer mode" (toggle in the top-right corner).
4. Click "Load unpacked" and select the folder containing this Repo, which will also have "Python_app" as a subdirectory, though that is not needed.

## Documentation

### Technology Used
* Chrome extension uses Javascript to collect all text contents of current tab (even adds and extraneous text)
* The current website is compared to video Youtube channels of 32 video transcripts stored in S3 bucket
* Python library rank-bm25 running in Heroku is used to find the top 3 videos most similar to your current tab
* The 32 pre-selected video transcripts were already saved in advance (using the "manual" file in main folder which is not part of the extension)
* The Python_app folder is also not needed for the extension, and is what Heroku is running separately -- all API keys stored in Heroku

### How to use
Once installed, you go to a tab you find interesting. Then click the purple smiley face icon in your Chrome extensions. Then press the "Go" button, and 3 links to the top videos from the custom library will appear. You can click them and they will open in a new tab. You can view transcripts in Youtube to see if it looks like a good match

### Requirements for Python in Heroku
Flask==3.0.3
gunicorn==23.0.0
flask-cors==5.0.0
boto3==1.35.77
rank-bm25==0.2.2
pandas==2.2.3
youtube-transcript-api==0.6.3
google-api-python-client==2.100.0
requests==2.32.3

Flask and gunicorn were to work with Heroku, boto3 for the AWS S3 bucket. The rank-bm25 and pandas were used in Python to rank the videos and keep a dataframe of info. The YouTube libraries didn't work in Heroku but were used locally to set up the video library. The "requests" library is not currently used but for future development once getting special Google Authorization to access Youtube videos through Heroku.

### Files included:
* manually_save_videos_for_S3_bucket.py : not part of chrome extension, just a one-time set up to create the 32 Youtube video transcript files
* Python_app : folder for Heroku Flask to run Python
  * app : folder with Python code
    * main.py : Python code to perform bm25
    * __init__.py : not in use but for further development to start a Python class
  * Procfile : to be able to use flask
  * requirements.txt : libraries needed by Python
  * runtime.txt : python version
  * wsgi.py : to run in Flask
* manifest.json : setting up chrome extension
* display_window.html : formatting popup window
* popup.js : for the button that calls the Flask endpoint

### Limitations
I did not meet all the goals I planned. Two main shortcomings:
* User is not able to add their own videos or channels. I used Heroku to run the Python part, and unfortunately I realized too late I needed special Google Authorization for my free YouTube API to be able to access channels through Heroku. The manual Python script ran OK locally on my computer, but I was not able to integrate it into Heroku to be an interactive part of the app
* There are only 3 channels represented. I had trouble identifying YouTube channels even manually. Individual YouTube videos have a consistent format with 11-digit YouTube ID, but channels have different formats. The first channel I used for testing worked with my original script, but it was hard to find additional channels using the same format, so videos from only 3 channels are included in the video library, of 32 videos.


## Evaluation
I did not compare the bm25 method used here with other techniques, but I manually looked at results I got with various websites including Wikipedia and news articles, and the results made sense to me. Many of these videos have pretty focused topics, so looking at Wikipedia pages for "sunflower" would return the "How Sunflowers Bring All the Bees to the Yard | Deep Look" and "These 5 Bees Are Waaay More Than Honey and Stingers | Deep Look" video. However it left out "Behind-the-Scenes with Sunflowers | #DeepLook #Shor", so probably more advanced data cleaning or semantic search might help.

Another result was searching "giraffes" in google, which brings up a bunch of "Lions of the Skeleton Coast", which makes sense since the video describes the lions hunting giraffes.

There were also some poor results that did not seem intuitive, which might relate to the Javascript including even ads and unrelated contents, and the app does not do any data cleaning. Also, longer videos seemed to be favored in search results, so fine-tuning the TF-IDF in BM25 to penalize longer docs may have helped.

## Cited Code Sources
https://skillshats.com/blogs/how-to-use-the-youtube-api-with-python-a-step-by-step-guide/
https://medium.com/@luv_uiux/your-first-chrome-extension-hello-world-0f6898791489
https://stackoverflow.com/questions/74409759/chrome-extension-that-searches-for-text-in-a-page-then-changes-the-message-on-th
https://www.scaler.com/topics/javascript-return-multiple-values/
https://stackoverflow.com/questions/54511144/print-set-element-in-javascript
https://stackoverflow.com/questions/3787901/why-javascripts-typeof-always-return-object
https://developer.chrome.com/docs/extensions/develop/concepts/messaging
https://developers.google.com/youtube/v3/docs/channels/list
https://developers.google.com/youtube/v3/quickstart/js
https://medium.com/@cmurphy580/a-quick-walkthrough-of-the-youtube-api-javascript-4f0b0a13f988
https://www.geeksforgeeks.org/introduction-and-installation-of-heroku-cli-on-windows-machine/
https://devcenter.heroku.com/articles/getting-started-with-python#clone-the-sample-app
https://www.geeksforgeeks.org/deploy-python-flask-app-on-heroku/
https://whoosh.readthedocs.io/en/latest/indexing.html#merging-segments
https://dev.to/aws-builders/how-to-list-contents-of-s3-bucket-using-boto3-python-47mm
https://stackoverflow.com/questions/18500759/createelement-a-href-variable1variable2-a
https://coreui.io/blog/how-to-open-all-links-in-new-tab-using-javascript/
https://stackoverflow.com/questions/65566850/what-permissions-are-needed-to-delete-an-object-from-a-specific-bucket-in-s3

