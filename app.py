import os, csv, glob, sqlite3, json, bisect, datetime, sys, base64
import pandas as pd
import numpy as np
from io import BytesIO
import matplotlib.pyplot as plt
from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, date
import operator
import math

# TO-DO:
# Incorporate charts/graphs and heat map for web application
# Don't show table of entities in front end (at least without selecting options/filters)

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.secret_key = "Foobar"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#db = SQLAlchemy(app)

# Video Event Entity
# Attributes are same as that of the Open Baltimore data/.csv file
'''
class Video(db.Model):
    video_id = db.Column(db.String(80), nullable = False, primary_key = True)
    title = db.Column(db.String(80), nullable = False)
    published_at = db.Column(db.String(80), nullable = False) # May want to change formatting of this
    channel_id = db.Column(db.String(80), nullable = False)
    channel_title = db.Column(db.String(80), nullable = False)
    category_id = db.Column(db.String(80), nullable = False)
    trending_date = db.Column(db.String(80), nullable = False) # Change this same as published_at
    tags = db.Column(db.String(80), nullable = False)
    view_count = db.Column(db.String(80), nullable = False)
    likes = db.Column(db.String(80), nullable = False)
    dislikes = db.Column(db.String(80), nullable = False)

    def __init__(self, video_id, title, published_at, channel_id, channel_title, category_id, trending_date, tags, view_count, likes):
        self.video_id = video_id
        self.title = title
        self.published_at = published_at
        self.channel_id = channel_id
        self.channel_title = channel_title
        self.category_id = category_id
        self.trending_date = trending_date
        self.tags = tags
        self.view_count = view_count
        self.likes = likes

# Update databases in web application
# Will clear out old data and replace with new data, may have a more efficient implementation we could do
def update_databases():
    db.drop_all()
    db.create_all()
    #print("Files in %r: %s" % (os.getcwd(), os.listdir(os.getcwd()))) # Testing/debugging purposes only
    hold = [] # Store data for creating charts/graphs

    # Get file name
    if __name__ == "__main__" and len(sys.argv) > 1:
        filename = str(sys.argv[1])
    else:
        filename = 'BR_youtube_trending_data.csv'

    with open(filename) as file:
        reader = csv.reader(file)
        skip_first = 1
        data = [] # Store data from .csv as a matrix

        # Read in data from .csv, store it in data matrix
        for row in reader:
            if skip_first == 0:
                new_row = []
                for item in row:
                    new_row.append(item)
                data.append(new_row)
            else:
                skip_first = 0

    # Convert data to database
    for row in data:
        if skip_first == 0: # Skip first line which just has labels for data
            if not(row[0] in hold):
                hold.append(row[0])
                new_video = Video(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])
                db.session.add(new_video)
        else:
            skip_first = 0
    db.session.commit()
'''

# Load data from a .csv into a 2D array for reference
def load_data():
    # Get file name
    if __name__ == "__main__" and len(sys.argv) > 1:
        filename = str(sys.argv[1])
    else:
        filename = 'US_youtube_trending_data.csv'

    with open(filename) as file:
        reader = csv.reader(file)
        skip_first = 1
        data = [] # Store data from .csv as a matrix

        # Read in data from .csv, store it in data matrix
        for row in reader:
            if skip_first == 0:
                new_row = []
                for item in row:
                    new_row.append(item)
                data.append(new_row)
            else:
                skip_first = 0
    return data

with app.app_context():
    load_data()
    #db.create_all()

@app.route("/")
def hello():
    data = load_data()

    # Vis 1: Grouped bar chart showing view count, likes, comment count
    gb_titles = [] # All video titles
    gb_views = [] # Views of videos
    gb_likes = [] # Likes of videos
    gb_comment_counts = [] # Comment counts of videos

    # Get data
    for i in data[:9]:
        gb_titles.append(i[1])
        gb_views.append(int(i[8]))
        gb_likes.append(int(i[9]))
        gb_comment_counts.append(int(i[11]))

    gb_x = np.arange(len(gb_titles))
    gb_width = 0.2
    plt.bar(gb_x-gb_width, gb_views, gb_width, color='green')
    plt.bar(gb_x, gb_likes, gb_width, color='orange')
    plt.bar(gb_x+gb_width, gb_comment_counts, gb_width, color='purple')
    plt.xticks(gb_x, gb_titles)
    plt.xlabel("Videos")
    plt.ylabel("User Engagements")
    plt.legend(["Views", "Likes", "Comments"])
    buf = BytesIO()
    plt.savefig(buf, format="png")
    gb_data = base64.b64encode(buf.getbuffer()).decode("ascii")

    '''
    # Vis 2: Stacked bar chart totalling views per channel
    sb_channels = []
    sb_videos = []
    sb_frame = []

    # Fill frame
    for i in data:
        new_channel = i[4]
        if new_channel not in sb_channels:
            sb_frame.append([new_channel])
            sb_channels.append(new_channel)
        sb_frame[len(sb_frame)-1].append(int(i[9]))
        sb_videos.append(i[1])

    max_length = 0
    for i in data:
        if len(i) > max_length:
            max_length = len(i)

    for i in range(len(data)):
        while len(data[i]) < max_length:
            data[i].append(0)

    col = ["Channel"]
    for i in range(max_length-1):
        col.append(i)
    df = pd.DataFrame(sb_frame, columns = col)
    df.plot(x='Channel', kind='bar', stacked=True, title='Views per Video of Trending Channels')
    buf = BytesIO()
    plt.savefig(buf, format="png")
    sb_data = base64.b64encode(buf.getbuffer()).decode("ascii")
    ''' 

    return f"<img src='data:image/png;base64,{gb_data}'/>"


    # Generate the figure **without using pyplot**.
    fig = Figure()
    ax = fig.subplots()
    ax.plot([1, 2])
    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"<img src='data:image/png;base64,{data}'/>"

if __name__=="__main__":
    app.run(debug = True)
