from __future__ import print_function
import time
import httplib2
import requests
from bs4 import BeautifulSoup
import json
import os
import pandas as pd
from apiclient import discovery
from pprint import pprint
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import datetime

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None
teamKey = "frc4904"
events = []
data = []

class Event():
    """docstring for Event."""
    def __init__(self, eventKey, eventName):
        self.eventName = eventName
        self.eventKey = eventKey
        self.matches = []
        self.teams = getQueryFromTBA("/event/"+self.eventKey+"/teams")
        #for getting the team data from TBA, should prob use a quicksort
    def getMatchData(self):
        matchQuery = getQueryFromTBA("/event/"+self.eventKey+"/matches/simple")
        matchData = []
        for match in matchQuery:
            if match['comp_level'] == "qm":
                if match['winning_alliance'] == "blue":
                    redWin = "False"
                    blueWin = "True"
                elif match['winning_alliance'] == "red":
                    redWin = "True"
                    blueWin = "False"
                else:
                    redWin = ""
                    blueWin = ""
                #put all the useful stuff from the Query into one giant dictionary to pass off to the match class
                matchData.append({"event_name":self.eventName,"event_key":self.eventKey,"number":match["match_number"],"time":match['actual_time'],"red":{"teams":{"1":match['alliances']['red']['team_keys'][0],
                "2":match['alliances']['red']['team_keys'][1],"3":match['alliances']['red']['team_keys'][2]},"win":redWin,"score":match['alliances']['red']['score']},"blue":{"teams":
                {"1":match['alliances']['blue']['team_keys'][0],"2":match['alliances']['blue']['team_keys'][1],"3":match['alliances']['blue']['team_keys'][2]},"win":blueWin,"score":match['alliances']['blue']['score']}})
        for match in matchData:
            i = 0
            for team in match['red']['teams']:
                i +=1
                teamKey = match['red']['teams'][str(i)]
                for teamData in self.teams:
                    if teamData['key'] == teamKey:
                        teamInfoToPass = teamData
                self.matches.append(Match(match,"red",i,teamInfoToPass))
            i = 0
            for team in match['blue']['teams']:
                i +=1
                teamKey = match['blue']['teams'][str(i)]
                for teamData in self.teams:
                    if teamData['key'] == teamKey:
                        teamInfoToPass = teamData
                self.matches.append(Match(match,"blue",i,teamInfoToPass))


class Match():
    """docstring for Match."""
    def __init__(self,matchDict,teamAlliance,number,teamData):
        matchDict[teamAlliance]['teams'][str(number)] = makeSureNumeric(matchDict[teamAlliance]['teams'][str(number)])
        self.teamData = teamData
        self.time = matchDict['time']
        self.dictionary = {"event":matchDict['event_name'],"match":matchDict['number'],"team_number":self.teamData['team_number'],"team_name":self.teamData['name'],"alliance":teamAlliance,"robotNumber":number,"W/L":matchDict[teamAlliance]['win'],"score":matchDict[teamAlliance]['score'],
        'dataID':str(matchDict['event_name']+' '+str(matchDict['number'])+' '+str(self.teamData['team_number']))}
        #desired sheet output |event|match|teamNumber|teamName|alliance|robotNumber|win?|score|currentRank(will add on later)

def makeSureNumeric(teamKeyString):
    numberPart = teamKeyString[3:]
    numbers = "1234567890"
    finalString = teamKeyString[:3]
    for character in numberPart:
        if character in numbers:
            finalString = finalString + character
    return finalString
def getKey(filePath):

    #Get API Key
    tbaFile = open(os.path.expanduser(filePath))
    tbaKey = tbaFile.read()
    tbaFile.close()
    return tbaKey

def getQueryFromTBA(suffix):
    #Query TBA's API given url suffix
    tBAFilePath = '~/Documents/Programming/ScoutingAPIKeys/TBAAPIKey.txt'
    baseURL = "https://www.thebluealliance.com/api/v3"
    url = baseURL + suffix
    key = getKey(tBAFilePath)
    headers = {'X-TBA-Auth-Key': key}
    query = requests.get(url, headers=headers)
    decodedQuery = query.json()
    return decodedQuery

#For trying to do multiple queries
def getQueriesFromTBA(start,terms,finish):
    queries = []
    for term in terms:
        suffix = start + term + finish
        queries.append(getQueryFromTBA(suffix))
    return queries

def writeInfotoDataList(eventsList):
    masterData = []
    for event in eventsList:
        export = []
        for match in event.matches:
            export.append(match.dictionary)
        masterData.append(export)
    return masterData
#Get List of 2018 Events
eventQueries = getQueryFromTBA("/team/"+teamKey+"/events/2018")
#filter out the event name and the event Key and put it in
for eventQuery in eventQueries:
    events.append(Event(eventQuery['key'],eventQuery['name']))
    print(eventQuery['key'])

for event in events:
    event.getMatchData()

def writeUpcomingMatchList(eventsList):
    masterData = []
    for event in eventsList:
        export = []
        for match in event.matches:
            export.append(match.dictionary)
        masterData.append(export)
    return masterData
#desired sheet output |event|match|teamNumber|teamName|alliance|robotNumber|win?|score|
data = writeInfotoDataList(events)
x = 0
fieldnames = ['Event', 'Match', 'Team Number', 'Team Name','Alliance','Robot Position','Win/Loss','Score','DataID']
finalData = []
sheetData = [fieldnames]
for sheet in data:
    x+=1

    exportableData = []

    for match in sheet:
        listFromDict = []
        for term in match:
            listFromDict.append(match[term])
        exportableData.append(listFromDict)
    finalData= finalData +exportableData
    sheetData= sheetData +exportableData
df = pd.DataFrame(columns = fieldnames,data=finalData)
#print(df)

""" This is code to generate a list of teams at an event
for event in events:
    print(event.eventName)
    if event.eventName == "San Francisco Regional":
        print("true")
        teamList = getQueryFromTBA("/event/"+event.eventKey+"/teams/keys")
dfSFTeams = pd.DataFrame(columns = ["teamKey"],data=teamList)
df.to_csv('teamData.csv')
#/event/{event_key}/teams/keys """

def getNextMatch(eventcode):
    nextMatch = ""
    matchList = getQueryFromTBA("/event/"+"2018casj"+"/matches/simple")
    matchList.sort(key=lambda x: x['match_number'])
    for match in matchList:

        if str(match['actual_time']) == "None":
            if nextMatch == "":
                nextMatch = match
    return nextMatch


#Now the pushing to API
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = os.path.join(os.environ['HOME'],'Documents/Programming/ScoutingAPIKeys/client_secret.json')
APPLICATION_NAME = 'Google Sheets API Python Quickstart'
# TODO: Change placeholder below to generate authentication credentials. See
# https://developers.google.com/sheets/quickstart/python#step_3_set_up_the_sample


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.environ['HOME']
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        #print('Storing credentials to ' + credential_path)
    return credentials

def main(spreadsheet_id, pushData):

    """Shows basic usage of the Sheets API.

    Creates a Sheets API service object and prints the names and majors of
    students in a sample spreadsheet:
    https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
    """



    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')


    service = discovery.build('sheets', 'v4', credentials=credentials)


    # The A1 notation of the values to update.
    range_ = 'A1:AZ3000'

    # How the input data should be interpreted.
    value_input_option = 'USER_ENTERED'


    valuetoencode = {
        "range": "A1:AZ3000",
        "values": pushData
    }

    value_range_body = json.dumps(valuetoencode)
    #print(value_range_body)
    request = service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=range_, valueInputOption=value_input_option, body=valuetoencode)
    response = request.execute()

    # TODO: Change code below to process the `response` dict:
    #pprint(response)

#Team match data table

# data = {'qual1': {'red': [6658, 5572, 5190], 'blue': [...]}}


if __name__ == '__main__':
    main('1QTdG8EFg7ob5qtzc7f6aGbVuh8vdr_faDxOfTEO1VbY',sheetData)
while True:
    print(getNextMatch("2018cada"))
    time.sleep(10)
