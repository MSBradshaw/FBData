import json

bo = json.load(open('boulder_roads.json', 'r'))
po = json.load(open('europe-road.geojson', 'r'))

t = {'type': 'Feature',
     'geometry':
         {'coordinates': [], 'type': 'LineString'},
     'properties': {}
     }

outer_t = {'type':'FeatureCollection', 'features':[]}

# for each set of coordiantes in boulder roads, add them as a list of list (inner list is a pair of points)
# to a t object and append the t object to 'features in the outer tempate'

for i in range(len(bo['features'])):
    copy = t
    print(bo['features'][i]['geometry']['paths'][0])
    copy['geometry']['coordinates'] = bo['features'][i]['geometry']['paths'][0]
    outer_t['features'].append(copy)
    # for j in range(len(bo['features'][i]['geometry']['paths'][0])):
    #     pass
        # print(bo['features'][i]['geometry']['paths'][0][j])