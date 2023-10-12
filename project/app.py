import os, csv, glob, sqlite3, json, bisect, datetime, sys
import pandas as pd
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

db = SQLAlchemy(app)

# Video Event Entity
# Attributes are same as that of the Open Baltimore data/.csv file
class Video(db.Model):
    video_id = db.Column(db.String(80), nullable = False, primary_key = True)
    title = db.Column(db.String(80), nullable = False)
    published_at = db.Column(db.String(80), nullable = False) # May want to change formatting of this
    channel_id = db.Column(db.String(80), nullable = False)
    channel_title = db.Column(db.String(80), nullable = False)
    category_id = db.Column(db.String(80), nullable = False)
    trending_date = db.Column(db.String(80), nullable = False) # Change this same as published_at
    tags = db.Column(db.String(80), nullable = False)
    view_count = db.Column(db.Int)
    likes = db.Column(db.Int)

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
                for item in row[1:0]:
                    new_row.append(item)
                data.append(new_row)
            else:
                skip_first = 0

    # Convert data to database
    for row in data:
        if skip_first == 0: # Skip first line which just has labels for data
            if not(row[0] in hold):
                hold.append(row[0])
                new_video = Video(row)
                db.session.add(new_video)
        else:
            skip_first = 0
    db.session.commit()

with app.app_context():
    update_databases()
    db.create_all()




#@app.route('/')
#def start():
#    return charthome2()
@app.route('/heatmap')
def static_file():
    return app.send_static_file('js/leaflet-heat.js')

@app.route('/database')
def index():
    db.create_all()
    videos = Video.query.all()
    update_databases()
    return render_template('index.html', videos=videos)

# Visualizations below
# Need to update visualizations to match our chosen vis and use the appropriate variables

@app.route('/', methods = ['GET', 'POST'])
def charthome2():
    min_time, max_time = min_max_time()
    min_t_str = min_time.strftime("%D")
    max_t_str = max_time.strftime("%D")
    max_t_just_date = datetime.strptime(max_t_str, '%m/%d/%y')
    if request.method == "POST":
        sortby_data = request.form["s_id"]
        session["sortby"] = sortby_data
        w_id = request.form.getlist('w_id')
        if w_id == []:
            w_id = ['All']
        session['weapon'] = w_id
        d_id = request.form.getlist('d_id')
        if d_id == []:
            d_id = ['All']
        session['district'] = d_id
        c_id = request.form.getlist('c_id')
        if c_id == []:
            c_id = ['All']
        session['crime'] = c_id
        start = request.form['min_t']
        end = request.form['max_t']
        s_check, s_msg = date_check(start) 
        e_check, e_msg = date_check(end)
        flag, flags, flage = 0, 0, 0
        if(start == ''):
            session['start'] = min_time
            flags += 1
        if(end == ''):
            session['end'] = max_time
            flage += 1
        if flags != 0 and flage == 0:
            if(e_check == False):
                flash('End Date: ' + e_msg)
            else:
                user_e = datetime.strptime(end, '%m/%d/%y')
                if user_e > max_t_just_date:
                    flash('End date is past Max Date')
                else:
                    user_e = user_e + timedelta(hours = 23, minutes= 59,seconds=59)
                    session['end'] = user_e
        if flags == 0 and flage != 0:
            if(s_check == False):
                flash('Start Date: ' +s_msg)
            else:
                user_s = datetime.strptime(start, '%m/%d/%y')
                if user_s < min_time - timedelta(days=1):
                        flash('Start date is before to Min Date')
                else:
                    session['start'] = user_s
        if(flags == 0 and flage == 0):
            if(s_check == False):
                flash('Start Date: ' +s_msg)
                flag += 1 
            if(e_check == False):
                flash('End Date: ' + e_msg)
                flag += 1
            if(flag == 0):
                user_s = datetime.strptime(start, '%m/%d/%y')
                user_e = datetime.strptime(end, '%m/%d/%y')
                flag1 = 0
                if user_e < user_s:
                    flash('Start Date is after end date')
                    flag1 += 1
                if user_e > max_t_just_date:
                    flash('End date is past Max Date')
                    flag1 += 1
                if user_s < min_time - timedelta(days=1):
                    flash('Start date is before to Min Date')
                    flag += 1
                if(flag1 == 0):
                    user_e = user_e + timedelta(hours = 23, minutes= 59,seconds=59)
                    session['start'] = user_s
                    session['end'] = user_e
        
    s_w = session["weapon"].copy() if "weapon" in session else ['All']
    s_c = session["crime"].copy() if "crime" in session else ['All']
    s_d = session["district"].copy() if "district" in session else ['All']
    choose_s = session["sortby"] if "sortby" in session else 'weapon'
    sortby= ['weapon','district','crime','weekday','month','hour','age', 'gender', 'ethnicity', 'race']
    crime_set, weapon_set, district_set = ['All'], ['All'], ['All']
    for crime in Crime.query.all():
        hold = crime.description
        hold = hold.replace(' ','_')
        hold1 = crime.weapon
        hold1 = hold1.replace(' ', "_")
        if(not(hold in crime_set) and hold != ''):
            crime_set.append(hold) 
        if(not(hold1 in weapon_set) and hold1 != ''):
            weapon_set.append(hold1)
        if(not(crime.district in district_set) and crime.district != ''):
            district_set.append(crime.district)
    weapon_set.append('Not_Recorded'), crime_set.append('Not_Recorded'), district_set.append('Not_Recorded')
    if(not(choose_s in sortby)):
        choose_s = sortby[0]
    sortby.remove(choose_s)
    for s in s_d:
        if(s in district_set): district_set.remove(s)
    for s in s_w:
        if(s in weapon_set): weapon_set.remove(s)
    for s in s_c:
        if(s in crime_set): crime_set.remove(s)

    filtered_list, title2, datetitle, date_labels, date_data = get_filtered_list()
    latitudes, longitudes = [], []
    for crime in filtered_list:
        if (crime.latitude != '0' and crime.latitude != ''): latitudes.append(crime.latitude)
        if (crime.longitude != '0' and crime.longitude != ''): longitudes.append(crime.longitude)

    print(len(latitudes))
    print(len(longitudes))

    return render_template('chart_home2.html', districts = district_set, sortby = sortby,  crimes = crime_set, weapons = weapon_set, s_s = choose_s, s_w = s_w, s_d = s_d, s_c = s_c, young = min_t_str, old = max_t_str, lats = latitudes, longs = longitudes)
    
def date_check(date):
    monthday = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if(len(date) < 8):
        return False, 'Input too short'
    elif(len(date) > 8):
        return False, 'Input too long'
    elif date[2] != '/' or date[5] != '/':
        return False, 'Not correctly Formatted'
    elif date[:2].isdigit() == False:
        return False, 'Enter numbers or / only'
    elif date[3:5].isdigit() == False:
        return False, 'Enter numbers or / only'
    elif date[6:].isdigit() == False:
        return False, 'Enter numbers or / only'
    elif int(date[:2]) > 12:
        return False, 'Month is greater than 12'
    elif int(date[:2]) < 1:
        return False, 'Month is less than 1'
    elif int(date[3:5]) < 1:
        return False, 'Day is less than 1'
    elif int(date[3:5]) > monthday[int(date[:2]) - 1]:
        if(monthday[int(date[:2]) == 2]):
            if int(date[6:]) % 4 == 0:
                if int(date[3:5]) > 29:
                    return False, 'Day is to large'
                else:
                    return True, 'Good job'
            return False, 'Day is to large'
    else:
        return True, 'Good job'
    

def min_max_time():
    min_time, max_time = 'inf', 'inf'
    for crime in Crime.query.all():
        time = crime.datetime
        curr_time = datetime.strptime(time, '%Y/%m/%d %H:%M:%S+%f')
        if(min_time == 'inf' or curr_time < min_time):
            min_time = curr_time
        if(max_time == 'inf' or curr_time > max_time):
            max_time = curr_time
    return min_time, max_time

def time_chart(formatted, start, end):
    length = len(formatted)
    #newlist = sorted(formatted, key=operator.attrgetter('datetime'))
    curr = start
    label = []
    #curr = start.strftime("%D")
    while curr < end:
        label.append(curr.strftime("%Y/%m/%d"))
        curr = curr + timedelta(days = 5)
    label.append(end.strftime("%Y/%m/%d"))
    data = [0 for each in label]
    for crime in formatted:
        date = crime.datetime
        date, i = date[:10], 0
        for each in label:
            if date <= each:
                data[i] += 1
                break
            i += 1        
    return label, data
        

def ret_sort(crime, sort):
    if sort == 'weapon':
        return crime.weapon
    elif sort == 'crime':
        return crime.description
    elif sort == 'gender':
        return crime.gender
    elif sort == 'ethnicity':
        return crime.ethnicity
    elif sort == 'race':
        return crime.race
    elif sort == 'district':
        return crime.district
    elif sort == 'weekday':
        time = crime.datetime
        time = time[:time.index(' ')]
        year, time = int(time[:time.index('/')]), time[time.index('/') + 1:]
        month, day = int(time[:time.index('/')]), int(time[time.index('/') + 1:])
        the_day = date(year,month,day)
        return the_day.weekday()
    elif sort == 'month':
        time = crime.datetime
        time = time[:time.index(' ')]
        year, time = int(time[:time.index('/')]), time[time.index('/') + 1:]
        month = int(time[:time.index('/')])
        return month
    elif sort == 'hour':
        time = crime.datetime
        time = time[time.index(' ') + 1:]
        hour = int(time[:time.index(':')])
        return hour
    else:
        age, hold_i = crime.age, 0
        if(age == ''):
            hold_i = 8
        else:
            for i in range(1, 9):
                if int(age) <= (i * 10):
                    hold_i = i - 1
                    break
                if i == 8:
                    hold_i = i - 1
                    break
        return hold_i

@app.route('/chartshow2')
def chartshow2():
    month = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November','December']
    labels, datas, labelss, weekday = [], [], [], ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    age_labels = ['[0-10]','[11-20]','[21-30]','[31-40]','[41-50]','[51-60]','[61-70]','[71+]','Not Recorded']
    choose_s = session["sortby"] if "sortby" in session else 'weapon'
    filtered_list, title2, datetitle, date_labels, date_data = get_filtered_list()
    # latitudes, longitudes = [], []

    # for crime in filtered_list:
    #     print(crime.latitude, ", ", crime.longitude)

    if choose_s == 'weekday':
        for each in weekday: #initilize the data for weekdays (set list of size 7 with 0's)
            datas.append(0)
    if choose_s == 'month': #initilize data list of month (set list of size 12 with 0's)
        for each in month:
            datas.append(0)
    if choose_s == 'age':
        for each in age_labels:
            datas.append(0)
    if choose_s == 'hour': #initiliaze and create the label list and data list for time of day
        labels.append('12am')
        for i in range(1,12):
            labels.append(str(i) + 'am')
        labels.append('12pm')
        for i in range(1,12):
            labels.append(str(i) + 'pm')
        for each in labels:
            datas.append(0)
    count_hold = 0
    for crime in filtered_list:
        # latitudes.append(crime.latitude)
        # longitudes.append(crime.longitude)
        curr = ret_sort(crime,choose_s) #ret_sort function will, return element or what index to add data to
        if(choose_s == 'weekday'):
            datas[curr] += 1
        elif(choose_s == 'month'):
            datas[curr - 1] += 1
        elif(choose_s == 'hour'):
            datas[curr] += 1
        elif(choose_s == 'age'):
            datas[curr] += 1
        else:
            if(curr == ''):
                curr = 'Not Recorded'
            if not(curr in labels): #add new info to labels and add 1 to data index for that label
                labels.append(curr)
                datas.append(1)
            else: #if info already in labels will add 1 to index for the data
                i = labels.index(curr)
                datas[i] += 1
    #if(choose_s == 'age'):
    #    labelss = [str(each) for each in labels]
    #    if(count_hold != 0):
    #        labelss.append('Not Recorded')
    #        datas.append(count_hold)
            
    #i have to convert the lists to json for the graphs i think (it works)
    labels_json = '' 
    if choose_s == 'age':
        labels_json = json.dumps(age_labels)
    elif choose_s == 'weekday':
        labels_json = json.dumps(weekday)
    elif choose_s == 'month':
        labels_json = json.dumps(month)
    else:
        labels_json = json.dumps(labels)
    datas_json = json.dumps(datas)
    
    session['labels'] = labels_json
    session['datas'] = datas
    #this is just some string manipulation to get titles of charts

    title = 'Baltimore Crime Data Visualization: Sorted by ' + choose_s
    title1 = json.dumps(title)

    
    date_l_json = json.dumps(date_labels)
    date_d_json = json.dumps(date_data)
    return render_template('chart2.html', datas = datas_json, labels = labels_json, title1 = title1, title2 = title2, range = datetitle, date_d = date_d_json, date_l = date_l_json)

def get_filtered_list():
    weapon_set = session["weapon"].copy() if "weapon" in session else ['All']
    crime_set = session["crime"].copy() if "crime" in session else ['All']
    district_set = session["district"].copy() if "district" in session else ['All']
    start_date = session["start"] if "start" in session else min_max_time()[0]
    end_date = session["end"] if "end" in session else min_max_time()[1]
    start_date = start_date.replace(tzinfo=None)
    end_date = end_date.replace(tzinfo=None)
    filtered_set = []
    if 'All' in weapon_set:
        weapon_set = ['All']
    if 'All' in district_set:
        district_set = ['All']
    if 'All' in crime_set:
        crime_set = ['All']
    for i in range(len(weapon_set)):
        weapon_set[i] = weapon_set[i].replace('_',' ')
        if weapon_set[i] == 'Not Recorded':
            weapon_set[i] = ''
    for i in range(len(district_set)):
        district_set[i] = district_set[i].replace('_',' ')
        if district_set[i] == 'Not_Recorded':
            district_set[i] = ''
    for i in range(len(crime_set)):
        crime_set[i] = crime_set[i].replace('_',' ')
        if crime_set[i] == 'Not_Recorded':
            crime_set[i] = ''
    for crime in Crime.query.all():
        d, w, c = crime.district, crime.weapon, crime.description
        d, w, c = d.replace('_',' '), w.replace('_',' '), c.replace('_',' ')
        timedate = crime.datetime
        timedate = datetime.strptime(timedate, '%Y/%m/%d %H:%M:%S+%f')
        timedate = timedate.replace(tzinfo=None)
        if(d in district_set or district_set == ['All']):
            if(w in weapon_set or weapon_set == ['All']):
                if(c in crime_set or crime_set == ['All']):
                    if(timedate >= start_date and timedate <= end_date):
                        filtered_set.append(crime)
    title2 = 'Data is filtered from: Weapons('
    for each in weapon_set:
        title2 += each + ','
    title2 = title2[:-1]
    title2 += ') Crimes('
    for each in crime_set:
        title2 += each + ','
    title2 = title2[:-1]
    title2 += ') Districts('
    for each in district_set:
        title2 += each + ','
    title2 = title2[:-1]
    title2 += ')'

    min_str = start_date.strftime("%D")
    max_str = end_date.strftime("%D")
    datetitle = 'Date Range: ' + min_str + ' - ' + max_str
    date_labels, date_data = time_chart(filtered_set, start_date, end_date)
    return filtered_set, title2, datetitle, date_labels, date_data


    

    

@app.route('/test',methods = ['GET', 'POST'])
def test():
    if request.method == "POST":
        leng = request.form.getlist('languages')
        session['array'] = leng
    leng = ' yes'
    #data1 = session["weapon"].copy() if "district" in session else 'No data yet'
    data1 = session["young"] if "young" in session else 'No data yet'
    #data1 = data1.strftime("%m/%d/%Y, %H:%M:%S")
    data2 = session["old"] if "old" in session else 'No choice'
    #data2 = data2.strftime("%m/%d/%Y, %H:%M:%S")
    data3 = session['labels'] if "labels" in session else ['No choice']
    data4 = session['datas'] if "datas" in session else ['No choice']
    arg = get_filtered_list()
    return render_template('test1.html', data1 = data1, data2 = data2, data3 = data3, data4 = data4, leng = arg)




if __name__=="__main__":
    app.run(debug = True)
