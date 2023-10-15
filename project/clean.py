# Currently this code only focus on US data any other data as of right now needs to be manually edited to change
#
import json
import pandas as pd
import numpy as np

json_data_path = "US_category_id.json"
csv_data_path = "US_youtube_trending_data.csv"
file_encoding = "utf-8"


if __name__=="__main__":
    with open(json_data_path, 'r') as json_file:
        data = json.load(json_file)

    titles = []
    ids = []

    # inserts json data into the array
    for item in data['items']:
        ids.append(item['id'])
        titles.append(item['snippet']['title'])

    # testing - printing out array value
    #for i in range(len(ids)):
    #    print(f"ID: {ids[i]}, Title: {titles[i]}")

    data = pd.read_csv("US_youtube_trending_data.csv")

    print(data['categoryId'].head(5))
    data['categoryId'] = data['categoryId'].astype(str)
    for i in range(len(data)):
        category_id = data.at[i, 'categoryId']
        for j in range(len(ids)):
            if category_id == ids[j]:
                data.at[i, 'categoryId'] = titles[j]
                break
    # hard code number of columns
    num_column = 16

    reshaped_data = np.array(data).reshape(-1, num_column)
    df = pd.DataFrame(reshaped_data, columns=[data.columns])

    df.to_csv('Updated_US_youtube_trending_data.csv', index=False)
