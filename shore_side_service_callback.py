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

@api.route(relativeCallbackUrl + '/state', methods=['POST'])
def StateChanged():
    return "", 200

def SetupCallback(user, password, shoremrn):
    print("Setting up callback")
    headers={
        'Authorization': 'Basic %s' % GenerateBasicAuth(user, password),
        "MMSI": shoremrn,
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


if __name__ == '__main__':
    argumentList = sys.argv[1:]

    options = "u:p:h:d:"

    long_options = ["user=", "pass=", "shore-mrn=", "delay="]
    
    user = ""
    password = ""
    shoremrn = "shoremrn"
    delay = 5

    try:
        arguments, values = getopt.getopt(argumentList, options, long_options)
        
        for currentArgument, currentValue in arguments:
    
            if currentArgument in ("-u", "--user"):
                user = currentValue
                
            elif currentArgument in ("-p", "--pass"):
                password = currentValue

            elif currentArgument in ("-h", "--shore-mrn"):
                shoremrn = currentValue

            elif currentArgument in ("-d", "--delay"):
                dealy = currentValue
                
    except getopt.error as err:
        print (str(err))
        exit(1)

    print("User: " + user)
    print("Pass: " + password)
    print("Shore MRN:  " + shoremrn)
    print("Delay:  " + str(delay))

    print("----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
    print("Data can be sent to the ship using this CURL command:")
    print('curl -X POST -H "Authorization: Basic ' + GenerateBasicAuth(user, password) + '\" -H "dstMRN:shipmrn" -H "srcMRN:' + shoremrn + '" -H "Content-Type:application/octet-stream" --data "Your payload" -v ' + baseUrl + '/mms/unicast')
    print("----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
    SetupCallback(user, password, shoremrn)
    SetupEnvironment(user, password, delay)

    api.run(host='0.0.0.0', port=callbackPort) 