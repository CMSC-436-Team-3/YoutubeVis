# CMSC 447 - Web Application

# How to Run:
** NOTE: Ensure you have a Python interpreter able to run Flash applications, such as virtualenv with flask installed **

With all prerequisite models installed, path to the location of the 'app.py' file (this should be /YoutubeVis/project).
Once there, you can run the file by with the following command:
    python app.py '[FILENAME]'
Where [FILENAME] is replaced with the .csv file you want to pull data from. If a file isn't provided, a default one will be selected.

Once the application is started, you can open it in your web browser with the link tied to it, which should be provided in the terminal you are using.

The web app will display a title, a drop down menu, a visualization, as well as some filters in the form of checkboxes and a timeline. You can open the drop down menu to choose different visualizations, the four currently implemented are:
* Likes to Views
* User Engagement
* Likes and Dislikes
* Sunburst Popularity Chart
Some of these visualizaitons are currently in an unfinished state, with plans to update them to better represent the data.

The filters at the bottom of the web app allows you to change the data being presented. You can use the timeline to set a specific window from which to gather data, and the visualizations will only count data from videos published within the window. The checkboxes can be used to only display certain categories, such as Music, Gaming, Entertainment, etc. When no checkboxes are selected, all data will be shown; otherwise if you have at least one checkbox selected it will only display selected data.

# Data processing
Firstly, you will need Updated_youtube_trending_data.csv to run the app.py application.
This is created using clean.py which requires two files a .json file and a .csv file pairs from the dataset linked below.
There is a Updated_US_youtube_trending_data.csv provided to be used. Currently, this application only functions using United States data as US_youtube_trending_data.csv.
https://www.kaggle.com/datasets/rsrishav/youtube-trending-video-dataset

# Clearing data
While running the app.py, switching to each different implementations will causes data manipulations via the code. In case of any random error, relaunching the python app.py could be necessary. As of 12/4/2023 there is no issue of this.
