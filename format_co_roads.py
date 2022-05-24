import json
import matplotlib.pyplot as plt
import geopandas as gpd

"""
Boulder roads data comes from
https://maps.bouldercounty.org/arcgis/rest/services/Transportation/RoadMapRoads/MapServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json
The geojson template is stolen from the european roads file
"""

bo = json.load(open('boulder_roads.json', 'r'))

t = {'type': 'Feature',
     'geometry':
         {'coordinates': [], 'type': 'LineString'},
     'properties': {}
     }

outer_t = {'type':'FeatureCollection', 'features':[]}

# for each set of coordiantes in boulder roads, add them as a list of list (inner list is a pair of points)
# to a t object and append the t object to 'features in the outer tempate'

for i in range(len(bo['features'])):
    t = {'type': 'Feature',
         'geometry':
             {'coordinates': [], 'type': 'LineString'},
         'properties': {}
         }
    copy = t.copy()
    copy['geometry']['coordinates'] = bo['features'][i]['geometry']['paths'][0]
    bo['features'][i]['geometry']['paths'][0]
    outer_t['features'].append(copy)
    print('\n\n\n')
    print(bo['features'][i]['geometry']['paths'][0])

json.dump(outer_t, open('boulder_roads.geojson', 'w'))

roads = gpd.read_file('boulder_roads.geojson')

fig, ax = plt.subplots()
roads.plot(ax=ax, alpha=0.3, linewidth=1, color='black')
plt.show()