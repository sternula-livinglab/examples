# Prerquisites
# pip install flask

from flask import Flask, json
from flask import request
import requests
import getopt, sys
import base64

callbackPort = 8081
relativeCallbackUrl = "/callback"
baseUrl = "http://172.90.255.3:80"

api = Flask(__name__)

@api.route(relativeCallbackUrl + '/message', methods=['POST'])
def ReceiveMessage():
    mrn = request.headers['srcMRN']
    print("Received from '" + mrn + "': " + str(request.data.decode("ascii")))
    return "", 200

@api.route(relativeCallbackUrl + '/packet', methods=['POST'])
def ReceivePacket():
    mmsi = request.headers['srcMMSI']
    print("Received from '" + mmsi + "': " + str(request.data.decode("ascii")))
    return "", 200

@api.route(relativeCallbackUrl + '/state', methods=['POST'])
def StateChanged():
    return "", 200

def SetupCallback(user, password, shoreid):
    print("Setting up callback")
    headers={
        'Authorization': 'Basic %s' % GenerateBasicAuth(user, password),
        "MMSI": shoreid,
        "username": "not_used",
        "password": "in_this_example",
        "relativeurl": relativeCallbackUrl,
        "port": str(callbackPort)
    }
    response = requests.post(baseUrl + "/packet/callback", headers=headers)
    if(response.status_code != 200):
        print("Could not setup callback")
        exit(1)


def SetupEnvironment(user, password, fixedDelay):
    # This sets up the simulator to use a fixed delay by setting execution to "<seconds>sec"
    # To have realtime execution, set execution to "realtime"
    print("Setting up sim environment with a fixed delay of " + str(fixedDelay) + " seconds")
    basic = user + ":" + password
    b64 = base64.b64encode(basic.encode()).decode()
    headers={
        'Authorization': 'Basic %s' % GenerateBasicAuth(user, password),
        "execution": str(fixedDelay) + "sec"
    }
    response = requests.post(baseUrl + "/simulator/environment", headers=headers) 
    if(response.status_code != 200):
        print("Could not setup environment")
        exit(1)

def GenerateBasicAuth(user, password):
    basic = user + ":" + password
    return base64.b64encode(basic.encode()).decode()

def NMEACheckSum(nmeaStr):
    cs = 0
    chars = list(nmeaStr)
    for c in chars:
        cs = cs ^ c 
    return cs


if __name__ == '__main__':
    argumentList = sys.argv[1:]

    options = "u:p:h:d:"

    long_options = ["user=", "pass=", "shore-id=", "delay="]
    
    user = ""
    password = ""
    shoreid = "shoreid"
    delay = 5

    try:
        arguments, values = getopt.getopt(argumentList, options, long_options)
        
        for currentArgument, currentValue in arguments:
    
            if currentArgument in ("-u", "--user"):
                user = currentValue
                
            elif currentArgument in ("-p", "--pass"):
                password = currentValue

            elif currentArgument in ("-h", "--shore-id"):
                shoreid = currentValue

            elif currentArgument in ("-d", "--delay"):
                delay = currentValue
                
    except getopt.error as err:
        print (str(err))
        exit(1)

    print("User: " + user)
    print("Pass: " + password)
    print("Shore ID:  " + shoreid)
    print("Delay:  " + str(delay))

    print("----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
    print("MMS Data can be sent to the ship using this CURL command:")
    print('curl -X POST -H "Authorization: Basic ' + GenerateBasicAuth(user, password) + '\" -H "dstMRN:shipid" -H "srcMRN:' + shoreid + '" -H "Content-Type:application/octet-stream" --data "Your payload" -v ' + baseUrl + '/mms/unicast')
    print("----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")

    print("----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
    print("VDES Data can be sent to the ship using this CURL command:")
    print('curl -X POST -H "Authorization: Basic ' + GenerateBasicAuth(user, password) + '\" -H "dstMMSI:shipid" -H "srcMMSI:' + shoreid + '" -H "sequenceNumber:0" -H "packageId:0" -H "Content-Type:application/octet-stream" --data "Your payload" -v ' + baseUrl + '/packet/unicast')
    print("----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")

    SetupCallback(user, password, shoreid)
    SetupEnvironment(user, password, delay)

    api.run(host='0.0.0.0', port=callbackPort) 