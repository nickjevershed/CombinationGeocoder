import csv
import json
import requests

#Get and parse the geocoded locations from the API
def get_request(url, geoName, rowArray, k):
    if k == 0:
        rowArray.append(geoName + '_lat')
        rowArray.append(geoName + '_lng')
    else:
        try:
            r = requests.get(url)
            jsonData = r.json()
            # print url - use for errors to see what the API is fetching
            if(geoName == 'google'):
                elem1 = jsonData['results'][0]['geometry']['location']['lat']
                elem2 = jsonData['results'][0]['geometry']['location']['lng']
            elif(geoName == 'pickP'):
                elem1 = jsonData[0]['lat']
                elem2 = jsonData[0]['lon']
            elif(geoName == 'bing'):
                elem1 = jsonData['resourceSets'][0]['resources'][0]['point']['coordinates'][0]
                elem2 = jsonData['resourceSets'][0]['resources'][0]['point']['coordinates'][1]
            elif(geoName == 'openC'):
                elem1 = jsonData['results'][0]['geometry']['lat']
                elem2 = jsonData['results'][0]['geometry']['lng']    
            elif(geoName == 'mapQ'):
                elem1 = jsonData['results'][0]['locations'][0]['latLng']['lat']
                elem2 = jsonData['results'][0]['locations'][0]['latLng']['lng']
        except IndexError:
            elem1 = 'Index Error'
            elem2 = 'Index Error'
        except ValueError:
            elem1 = 'Value Error'
            elem2 = 'Value Error'
        #Pick point latLng coords returned as unicode.
        if type(elem1) == unicode:
            elem1 == float(elem1)
        if type(elem2) == unicode:    
            elem2 == float(elem2)
        rowArray.append(elem1)
        rowArray.append(elem2)
    print rowArray

#These functions format the query strings depending on the API's requirements
#Enter your API Keys here.
def google_maps_geocode(queryString, k, rowArray):
    googleMapsOptions = "json"
    googleMapsAPIkey = "YOUR_API_KEY"
    googleMapsUrl = "https://maps.googleapis.com/maps/api/geocode/" + googleMapsOptions + "?address=" + queryString + "&key=" + googleMapsAPIkey 
    get_request(googleMapsUrl, 'google', rowArray, k)

def open_cage_geocode(queryString, k, rowArray):
    openCageOptions = "json"
    openCageAPIkey = "YOUR_API_KEY"
    openCageUrl = "http://api.opencagedata.com/geocode/v1/" + openCageOptions + "?q=" + queryString + "&key=" + openCageAPIkey
    get_request(openCageUrl, 'openC', rowArray, k)

def pick_point_geocode(queryString, k, rowArray):
    pickPointAPIkey = "YOUR_API_KEY"
    pickPointUrl = "https://pickpoint.io/api/v1/forward?key=" + pickPointAPIkey + "&q=" + queryString
    get_request(pickPointUrl, 'pickP', rowArray, k)

def map_quest_geocode(queryString, k, rowArray):
    mapQuestOptions = "outFormat=json"
    mapQuestAPIkey = "YOUR_API_KEY"
    mapQuestUrl = "http://www.mapquestapi.com/geocoding/v1/address?&" + mapQuestOptions + "&key=" + mapQuestAPIkey + "&location=" + queryString
    get_request(mapQuestUrl, 'mapQ', rowArray, k)

def bing_maps_geocode(queryString, k, rowArray): 
    bingOptions = "o=json"
    bingAPIkey = "YOUR_API_KEY"
    bingUrl = "http://dev.virtualearth.net/REST/v1/Locations/" + queryString + "?" + bingOptions + "&key=" + bingAPIkey
    get_request(bingUrl, 'bing', rowArray, k)

#Writes results to a file, containing the original file also
def save_to_csv(rowMatrix, columnNumber, fileName):
    with open(fileName, 'r') as csvFileRead:
        csvReader = csv.reader(csvFileRead, delimiter = ',')
        with open('result_' + fileName, 'w') as csvFileWrite:
            csvWriter = csv.writer(csvFileWrite, delimiter = ',')
            existingRowArray = []
            for row in csvReader:
                print row
                existingRowArray.append(row)
            for l in range(0, len(existingRowArray)):
                print rowMatrix[l]
                csvWriter.writerow(existingRowArray[l] + rowMatrix[l])

#Average of successful geocoded points
#This has a bug, but works well enough, for now
def get_average(rowArray, k):
    if k == 0:
        rowArray.append('avg_lat')
        rowArray.append('avg_lng')
    else:
        calcNumber = len(rowArray)/2
        sumOfLat = 0.0
        sumOfLng = 0.0
        divideLatBy = 0
        divideLngBy = 0
        for m in range(0, calcNumber):
            if type(rowArray[m*2]) == int or type(rowArray[m*2]) == float:
                divideLatBy = divideLatBy + 1
                sumOfLat = sumOfLat + rowArray[m*2]
            if type(rowArray[(m*2)+1]) == int or type(rowArray[(m*2)+1]) == float:
                divideLngBy = divideLngBy + 1
                sumOfLng = sumOfLng + rowArray[(m*2)+1]
	print sumOfLat, divideLatBy
	print sumOfLng, divideLngBy        
	avgLat = sumOfLat/divideLatBy
        avgLng = sumOfLng/divideLngBy
        rowArray.append(avgLat)
        rowArray.append(avgLng)
        print rowArray

#Range of successful geocoded points
def get_range(rowArray, k):
    if k == 0:
        rowArray.append('range_lat')
        rowArray.append('range_lng')
    else:
        calcNumber = len(rowArray)/2
        results = False
        getFirstLat = True
        getFirstLng = True
        for n in range(0, calcNumber-1):
            if type(rowArray[n*2]) == int or type(rowArray[n*2]) == float:
                results = True
                if(getFirstLat):
                    getFirstLat = False
                    lowLat = rowArray[n*2]
                    highLat = rowArray[n*2]               
                if rowArray[n*2] < lowLat:
                    lowLat = rowArray[n*2]
                if rowArray[n*2] > highLat:
                    highLat = rowArray[n*2]
            if type(rowArray[(n*2)+1]) == int or type(rowArray[(n*2)+1]) == float:
                results = True
                if(getFirstLng):
                    getFirstLng = False
                    lowLng = rowArray[(n*2)+1]
                    highLng = rowArray[(n*2)+1]
                if rowArray[(n*2)+1] < lowLng:
                    lowLng = rowArray[(n*2)+1]
                if rowArray[(n*2)+1] > highLng:
                    highLng = rowArray[(n*2)+1]
        if (results):
            rangeLat = highLat - lowLat
            rangeLng = highLng - lowLng
            rowArray.append(rangeLat)
            rowArray.append(rangeLng)

#Receives queryStrings from _init_()
def loop_through_locations(queryStrings, columnNumber, fileName):
    rowMatrix = []
    for k in range(0, len(queryStrings)):
        print queryStrings[k]
        rowArray = []
        #Order of results in final csv
        google_maps_geocode(queryStrings[k], k, rowArray)
        open_cage_geocode(queryStrings[k], k, rowArray)
        pick_point_geocode(queryStrings[k], k, rowArray)
        map_quest_geocode(queryStrings[k], k, rowArray)
        #bing_maps_geocode(queryStrings[k], k, rowArray) Up to 50 per day, then it costs.                
        get_average(rowArray, k)
        get_range(rowArray, k)
        rowMatrix.append(rowArray)
    save_to_csv(rowMatrix, columnNumber, fileName)

def _init_():
    fileName = raw_input('File name (.csv): ')
    locationColumns = raw_input('Columns with location data eg. 2,3,5: ')
    locationColumns = locationColumns.split(',')
    queryStrings = []
    with open(fileName, 'r') as csvFile:
        csvReader = csv.reader(csvFile, delimiter = ',')
        for row in csvReader:
            columnNumber = len(row)
            queryString = ''
            for i in range(0, len(locationColumns)):
                rowIterator = int(locationColumns[i])
                if (i == len(locationColumns)-1):
                    queryString = queryString + row[rowIterator] 
                else:
                    queryString = queryString + row[rowIterator]+',%20'
            queryStrings.append(queryString)
        loop_through_locations(queryStrings, columnNumber, fileName)

_init_()
