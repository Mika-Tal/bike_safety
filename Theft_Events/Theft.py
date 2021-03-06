"""
Created on Tue Nov 24 14:27:17 2020
@author: Mika, Christian 
"""

import pandas as pd 
import json
import requests

def welcome():
    print('Welcome to Bike Safe!')
    print('Give us your address and we will tell you where to park your bike!')

#return weather info based on the bike rack lat and long
def Weather(): 
    APIkey='845bf124b058d7198bdf344ea6d5d46d'
    #API call and format response as json
    headers = {'Content-Type': 'application/json'}
    url = 'http://api.openweathermap.org/data/2.5/weather?lat=40.440624&lon=-79.9959&''appid='+APIkey

    response = requests.get(url, headers = headers)
    if response.status_code == 200:
        data = json.loads(response.content.decode('utf-8'))    
        #extract relevant info
        for line in data:
            weather= dict(data['weather'][0]) #weather description
            #tempinfo=(data['main'])#all temp info
            temp=(((data['main']['feels_like'])-273.15)* 9/5 + 32)
            #Kelvin to Farenheit: (285.27 - 273.15) * 9/5 + 32
        print('Current weather in downtown Pittsburgh: %s, temperature %.2f F'%(weather['description'],temp))

#Get user input- current and destination addresses
def addresses ():
    CurrentAddress = input("Enter Current Street Name (street name and number):")
    atLocation = input("Is your current address same as desitnation (Y/N):")
    if atLocation == 'Y':
        destAddress = CurrentAddress
    else:
        destAddress = input("Enter Destination Address (street name and number):")
    locator = Nominatim(user_agent="myGeocoder")
    location = locator.geocode(DestinationAddress)
    "Latitude = {}, Longitude = {}".format(location.latitude, location.longitude)
    destAddress = input('Enter your destination address: ')
    print("Outdoor\n", "Indoor\n","No Preference\n")
    Choice = input("Enter where do you want to park your bike:")
    return Choice

CurrentAddress = input("Enter Current Address:")
CurrentDesti = input("Is your current address same as desitnation:")
if CurrentDesti == 'Y':
    DestinationAddress = CurrentAddress
else DestinationAddress = input("Enter Destination Address:")


#initializing locations from WPRDC csv file
#return: list of locations of all bike racks 
def findLocations():
    bike_locations = pd.read_csv("bike_rack_locations.csv")
    bike_locations_loc = bike_locations[['Longitude', 'Latitude']]
    return bike_locations_loc

#API call- returns theft count:   
def theftCount(loc):
    parameters = {
        'stolenness' : 'proximity', 
        'location' : loc, 
        'distance' : '1'}
    response = requests.get(
        "https://bikeindex.org:443/api/v3/search/count",
        params = parameters)
    if response.status_code== 200:
        data = json.loads(response.content.decode('utf-8'))
    return(data['proximity'])

#returns all theft counts by bike rack location
def allTheft(all_locs):
    thefts_store = []
    for i in range(len(all_locs)):
        longitude_start = locations.iloc[i][0]
        latitude_start = locations.iloc[i][1]
        api_loc = str(latitude_start) + ',' + str(longitude_start)
        thefts = theftCount(api_loc)
        thefts_store.append(thefts) 
    return thefts_store

#returns proportion of each rack's thefts relative to total 
def proportionTheft(rack_locs_wthefts):
    prop_store = []
    for i in range(len(rack_locs_wthefts)):
        thefts_loc = rack_locs_wthefts.iloc[i][2]
        prop = thefts_loc / totalThefts
        prop_store.append(prop)
    return prop_store

#returns group designation for each rack relative to proportion
def propGroups(locations, min, max, third):
    groups = []
    for i in range(len(locations)):
        prop = locations.iloc[i][3]
        if prop <= (min + third):
            groups.append('Low')
            print("here")
        if prop > (min + third) and prop <= (max - third):
            groups.append('Medium')
        if prop > (max - third):
            groups.append('High')
    return groups

locations = findLocations()
locations_thefts = locations.copy(deep=True)
thefts = allTheft(locations)
locations_thefts["Thefts"] = thefts
totalThefts = locations_thefts["Thefts"].sum()
props = proportionTheft(locations_thefts)
locations_thefts["Proportion"] = props
locations_thefts.sort_values(by='Proportion', inplace=True, ascending=False)
prop_min = locations_thefts["Proportion"].min()
prop_max = locations_thefts["Proportion"].max()
interval = prop_max - prop_min
interval_third = interval/3 
prop_groups = propGroups(locations_thefts, prop_min, prop_max, interval_third)
locations_thefts["Group"] = prop_groups 
print(locations_thefts[["Latitude","Longitude","Group"]])


