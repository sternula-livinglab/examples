import websocket
import _thread
import time
import base64
import getopt, sys
import threading
import uuid
import json

class WebSocketHandler():
    user = ""
    password = ""
    shipid = ""
    shoreid = ""
    thread = None
    isClosing = False
    isVdes = False

    def __init__(self, user, password, shipid, shoreid, isVdes):
        self.user = user
        self.password = password
        self.shipid = shipid
        self.shoreid = shoreid
        self.isVdes = isVdes

    def OnMessage(self, ws, message):
        if self.isVdes == True:
            print("Received NMEA: " + str(message.decode("ascii")))
        else:
            print("Received raw JSON: " + str(message.decode("ascii")))
            jsn = json.loads(message.decode("ascii"))
            b64encStr = jsn['d']
            b64encBytes = b64encStr.encode("ascii")
    
            dateBytes = base64.b64decode(b64encBytes)
            data = dateBytes.decode("ascii")
            print("Received message from " + jsn['src'] + ": " + str(data))

    def OnError(self, ws, error):
        print(error)

    def OnClose(self, ws, close_status_code, close_msg):
        print("Connection closed. Press enter to quit")
        self.isClosing = True
        exit(1)

    def OnOpen(self, ws):
        print("Opened connection. Sending authentication")
        basic = self.user + ":" + self.password + ":" + self.shipid
        b64 = base64.b64encode(basic.encode()).decode()
        auth = "Basic %s" % b64
        ws.send(auth+"\n")
        self.thread = threading.Thread(target=self.GetInput, args=(ws,))
        self.thread.start()

    def GetInput(self, ws):
        while self.isClosing == False:
            print("Type what you want to send:")
            i = input()
            if self.isClosing == True:
                return
            if self.isVdes == True:
                msg = self.CreateVDESMessage(i)
                print("Sending NMEA: '" + msg + "'")
                ws.send(str.encode(msg),websocket.ABNF.OPCODE_BINARY)
            else:
                msg = self.CreateMMSMessage(i)
                print("Sending MMS: '" + msg + "'")
                ws.send(msg+"\n")
        pass

    def NMEACheckSum(self, nmeaStr):
        cs = 0
        chars = list(nmeaStr)
        for c in chars:
            #if c != ",":
                cs = cs ^ (ord(c))
        return cs

    def CreateMMSMessage(self, data):
        return "{\"id\":\"" + str(uuid.uuid4()) + "\",\"src\":\"" + self.shipid + "\",\"dst\":\"" + self.shoreid + "\",\"d\":\"" + base64.b64encode(data.encode()).decode() + "\"}"

    def CreateVDESMessage(self, data):
        nmea = "VEEDM,1," + self.shipid + "," + self.shoreid + "," + data + ",0,0,0"
        nmea = "$" + nmea + "*" + hex(self.NMEACheckSum(nmea)).replace("0x", "")
        return nmea



if __name__ == "__main__":
    baseUrl = "ws://172.90.255.3:80"

    argumentList = sys.argv[1:]

    options = "u:p:s:h:v"

    long_options = ["user=", "pass=", "ship-id=", "shore-id=", "vdes="]
    
    user = ""
    password = ""
    shipid = "shipid"
    shoreid = "shoreid"
    isVdes = False



    try:
        arguments, values = getopt.getopt(argumentList, options, long_options)
        
        for currentArgument, currentValue in arguments:
    
            if currentArgument in ("-u", "--user"):
                user = currentValue
                
            elif currentArgument in ("-p", "--pass"):
                password = currentValue
                
            elif currentArgument in ("-s", "--ship-id"):
                shipid = currentValue

            elif currentArgument in ("-h", "--shore-id"):
                shoreid = currentValue

            elif currentArgument in ("-v", "--vdes"):
                isVdes = bool(currentValue)
                
    except getopt.error as err:
        print (str(err))
        exit(1)

    print("User: " + user)
    print("Pass: " + password)
    print("Ship ID:  " + shipid)
    print("Shore ID:  " + shoreid)
    print("VDES:  " + str(isVdes))

    relUrl = ""
    if isVdes == True:
        relUrl = "/interfaces/iec61162_450/socket"
    else:
        relUrl = "/interfaces/mms/socket"

    wsh = WebSocketHandler(user, password, shipid, shoreid, isVdes)
    ws = websocket.WebSocketApp(baseUrl + relUrl,
                              on_open=wsh.OnOpen,
                              on_message=wsh.OnMessage,
                              on_error=wsh.OnError,
                              on_close=wsh.OnClose)

    ws.run_forever()
    
