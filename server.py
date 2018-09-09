from flask import Flask, json, request
from flask_cors import CORS, cross_origin
from sklearn.neighbors import NearestNeighbors
from pandas import read_hdf
import pandas as pd
import random

app = Flask(__name__)
CORS(app)

model_s = read_hdf('datasets/model_set.h5')

all_attr = model_s.columns
n_subs = model_s.shape[0]

def get_burbs(user, attirbutes=all_attr, df=model_s):
    '''
    Takes a user feature vector and returns a ranked list of preffered suburbs
    The model attributes assessed can be changed by feeding in a more limited list of attributes
    '''
    X = df[attirbutes[1:]].values # TODO: reduce model or reorder attributes by editing the attirbutes here
    Y = df['Suburb'].values
    nbrs = NearestNeighbors(n_neighbors=n_subs, algorithm='ball_tree').fit(X)
    distances, indices = nbrs.kneighbors([user])
    df['score']=100
    for i, s in zip(indices, distances):
        df['score'].loc[i]=s
    #print(df.columns)
    return model_s.sort_values(by='score',ascending=False)[['Suburb']].values

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/match", methods=['POST'])
def match():
    content = request.json
    content_list = list(content.values())

    print(content_list )

    # Jake's test array
    #from numpy import random
    #test_user = random.uniform(low=0,high=1,size=len(all_attr)-1)
    #print(test_user)
    # compatible suburb results
    cs_results = get_burbs(content_list)
    print(cs_results )
    # Pulls data from govhack csv to match selected suburb
    csv_file_df = pd.read_csv('datasets/govhack-act.csv')
    first_picked_name = cs_results[0][0].lower().title()
    print(first_picked_name)
    govhack_values = (csv_file_df[csv_file_df['Suburb'] == first_picked_name])
    url = "http://129.144.154.154/images"

    # Array to contain graffiti url objects
    graffiti_urls = []
    print(govhack_values)
    graffiti_url_split = govhack_values.GRAFFITI_IMG.astype(str).item().split(", ")
    if(len(graffiti_url_split) > 1):
        for idx, val in enumerate(govhack_values.GRAFFITI_IMG.item().split(", ")):
            graffiti_urls.append({'id' : idx, 'image_url' : val}) 

    resp_data = {
        'name' : first_picked_name,
        'age' : str(govhack_values.AGE.astype(int).item()),
        'description' : govhack_values.DESCRIPTION.astype(str).item(),
        'mode_demo' : govhack_values.MODE_DEM.astype(str).item(),
        'commute_time' : govhack_values.COMMUTE.item(),
        'no_arts' : govhack_values.NO_ARTS.item(),
        'no_sports' : govhack_values.NO_FIT_SITES.item(),
        'no_basketball' : govhack_values.NO_BB_CRTS.item(),
        'no_skate_parks' : govhack_values.NO_SKATE_PARKS.item(),
        'no_hospitals' : govhack_values.NO_HOSPITALS.item(),
        'dog_park' : govhack_values.DOG_PARK.item(),
        'no_graffiti' : govhack_values.NO_GRAFITTI.item(),
        'no_bbq' : govhack_values.NO_BBQ.item(),
        'no_parks' : govhack_values.NO_PARKS_AND_PLAYGROUNDS.item(),
	'distance' : random.randint(5,15),
	'pop' : govhack_values.TOTAL_POP.item(),
	'fem_pop' : govhack_values.FEM_POP.item(),
	'male_pop' : govhack_values.MALE_POP.item(),
        'image_url' : "%s/%s.png" % (url, first_picked_name),
	'graffiti' : graffiti_urls
    }
    response = app.response_class(
        response=json.dumps(resp_data),
        status=200,
        mimetype='application/json'
    )
    response.headers.add('Access-Control-Allow-Origin', '*')	
    return response

def main():
    app.run("0.0.0.0",8000,True)

if __name__== "__main__":
    main()

