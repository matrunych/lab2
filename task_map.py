import csv
import copy
import folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderTimedOut


def read_file(file_name):
    """
    (str) -> list
    Read a csv file and put info in a list
    """
    reader = csv.reader(file_name)
    large_lst = []
    for row in reader:
        large_lst.append(row)

    return large_lst


def dict_years(lst):
    """
    (list) -> dict
    Return dict from list with year as key and places, where films were produced, as values
    >>> dict_years([['With Interest ', '2013', 'Los Angeles'], ['With It ', \
    '2004', 'Venice Beach'],['With Just a Little Trust ', '1975', \
    'Los Angeles']])
    {'2013': ['Los Angeles'], '2004': ['Venice Beach'], '1975': ['Los Angeles']}
    """
    dct = {}
    for el in lst:
        if len(el) > 2:
            if el[1] in dct:
                dct[el[1]].append(el[-1])
            else:
                dct[el[1]] = [el[-1]]
    return dct


def freq_places(dct, key):
    """
    (dict, str) - > dict
    Find key in dict with its values - lists and return new dict,
    where keys are unique elements of list and their frequency of use as value
    >>> freq_places({'1997': ['Marquee Caf Soho London W1'], \
    '2013': ['Los Angeles California USA'], '2004': ['Venice Beach Venice Los \
    Angeles California USA'], '1975': ['1229 South Santee Street Los Angeles \
    California USA']}, '2013')
    {'Los Angeles California USA': 1}
    """
    dct_1 = {}
    values = dct.get(key)
    values_1 = copy.deepcopy(values)
    values = set(values_1)
    for i in values:
        count = values_1.count(i)
        dct_1[i] = count
    return dct_1


def map_creator(dct, cur_location):
    """
    (dict, str) - > None
    Save html file with web-map with markers and coloured.
    """
    geolocator = Nominatim(user_agent="specify_your_app_name_here")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    map = folium.Map()

    lay_1 = folium.FeatureGroup(name="Film_map")
    for key in dct.keys():
        try:
            location = geolocator.geocode(key)
            if location != None:
                lat, long = location.latitude, location.longitude
                print("Finding coordinates of all places. Please wait ...")
                lay_1.add_child(folium.Marker(location=[lat, long], popup=str(key) + "-" + str(dct.get(key)) + " film(s) produced", icon = folium.Icon()))

            map.add_child(lay_1)
        except GeocoderTimedOut:
            continue

    lay_2 = folium.FeatureGroup(name="Population")

    lay_2.add_child(folium.GeoJson(data=open('world.json', 'r',
                                             encoding='utf-8-sig').read(),
                                   style_function=lambda x: {'fillColor': 'green'
                                   if x['properties']['POP2005'] < 10000000
                                   else 'red' if 10000000 <= x['properties']['POP2005'] < 100000000
                                   else 'blue'}))
    map.add_child(lay_2)

    lay_3 = folium.FeatureGroup(name="Your location")

    location = geolocator.geocode(cur_location)
    lat, long = location.latitude, location.longitude

    lay_3.add_child(folium.Marker(location=[lat, long],
                                popup="You are here!",
                                icon=folium.Icon(color='red', icon='info-sign')))

    map.add_child(lay_3)
    map.add_child(folium.LayerControl())
    map.save('Map_1.html')


if __name__ == "__main__":
    year = input("Type year: ")
    my_location = str(input("Type your location(city): ")).capitalize()
    csv_path = "locations.csv"
    with open(csv_path, "r") as f:
        lst = read_file(f)
    dct = dict_years(lst)
    dct_2 = freq_places(dct, year)
    map_creator(dct_2, my_location)
