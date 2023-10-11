# CMSC 447 - Web Application

# How to Run:
** NOTE: Ensure you have a Python interpreter able to run Flash applications, such as virtualenv with flask installed **

Within a virtual environment with all prerequisites installed, path to the location of the 'app.py' file (this should be /cmsc447-team4-project/project).
Once there, you can run the file by with the following command:
    python app.py '[FILENAME]'
Where [FILENAME] is replaced with the .csv file you want to pull data from. 'crime500.csv' is recommended. If a file isn't provided, a default one will be selected.

Once the application is started, you can open it in your web browser with the link tied to it, which should be provided in the terminal you are using.

The application itself is very straightforward, at the top of the screen are filters allowing you to choose whether to see all crimes, or only crimes relating to the following:
    * Crime Type (All by default)
    * Weapon Type (All by default)
    * District (All by default)
    * Timespan
The timespan is limited to all crimes between 01/25/23 and 04/22/23, which will be the default timespan. You can type in different dates if you want to narrow down the timespan.
Once filters are selected, you can choose how data is sorted (by weapon, district, crime, weekday, month, hour, or demographic information).

Below the filters is the heatmap, which can be navigated using the mouse or the buttons on the map itself. Hold left-click and drag to move around the map, and use the scroll wheel or the +/- buttons on the heatmap to zoom in and out. The heatmap will update based on the chosen filters.

Below the heatmap is the graphs and charts, which will automatically update based on the chosen filters.