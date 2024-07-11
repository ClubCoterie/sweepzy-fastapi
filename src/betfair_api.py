from dotenv import load_dotenv
import os, json, urllib.error, urllib.request
import betfairlightweight
from betfairlightweight import filters



def callAping(jsonrpc_req):

    try:
        req = urllib.request.Request(url, jsonrpc_req.encode('utf-8'), headers)
        response = urllib.request.urlopen(req)
        jsonResponse = response.read()
        return jsonResponse.decode('utf-8')
    except urllib.error.URLError as e:
        print (e.reason)
        print ('Oops no service available at ' + str(url))
        exit()
    except urllib.error.HTTPError:
        print ('Oops not a valid operation from the service ' + str(url))
        exit()

def getEventTypes():
    event_type_req = '{"jsonrpc": "2.0", "method": "SportsAPING/v1.0/listEventTypes", "params": {"filter":{ }}, "id": 1}'
    print ('Calling listEventTypes to get event Type ID')
    eventTypesResponse = callAping(event_type_req)
    eventTypeLoads = json.loads(eventTypesResponse)

def getEventTypeIDForEventTypeName(eventTypesResult, requestedEventTypeName):
    if(eventTypesResult is not None):
        for event in eventTypesResult:
            eventTypeName = event['eventType']['name']
            if( eventTypeName == requestedEventTypeName):
                return event['eventType']['id']
    else:
        print ('Oops there is an issue with the input')
        exit()

if __name__ == '__main__':
    url = "https://api.betfair.com/exchange/betting/json-rpc/v1"
    dotenv_path = "../.env"
    load_dotenv(dotenv_path=dotenv_path)
    appKey = os.getenv('API_KEY')
    sessionToken = os.getenv('SSOID')
    headers = {'X-Application': appKey, 'X-Authentication': sessionToken, 'content-type': 'application/json'}

    eventTypesResult = getEventTypes()
    horseRacingEventTypeID = getEventTypeIDForEventTypeName(eventTypesResult, 'Horse Racing')


