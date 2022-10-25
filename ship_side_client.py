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
    shipmrn = ""
    shoremrn = ""
    thread = None
    isClosing = False

    def __init__(self, user, password, shipmrn, shoremrn):
        self.user = user
        self.password = password
        self.shipmrn = shipmrn
        self.shoremrn = shoremrn

    def OnMessage(self, ws, message):
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
        basic = self.user + ":" + self.password + ":" + self.shipmrn
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
            msg = self.CreateMessage(i)
            print("Sending '" + msg + "'")
            ws.send(msg+"\n")
        pass

    def CreateMessage(self, data):
        return "{\"id\":\"" + str(uuid.uuid4()) + "\",\"src\":\"" + self.shipmrn + "\",\"dst\":\"" + self.shoremrn + "\",\"d\":\"" + base64.b64encode(data.encode()).decode() + "\"}"

if __name__ == "__main__":
    baseUrl = "ws://172.90.255.3:80"

    argumentList = sys.argv[1:]

    options = "u:p:s:h:"

    long_options = ["user=", "pass=", "ship-mrn=", "shore-mrn="]
    
    user = ""
    password = ""
    shipmrn = "shipmrn"
    shoremrn = "shoremrn"

    try:
        arguments, values = getopt.getopt(argumentList, options, long_options)
        
        for currentArgument, currentValue in arguments:
    
            if currentArgument in ("-u", "--user"):
                user = currentValue
                
            elif currentArgument in ("-p", "--pass"):
                password = currentValue
                
            elif currentArgument in ("-s", "--ship-mrn"):
                shipmrn = currentValue

            elif currentArgument in ("-h", "--shore-mrn"):
                shoremrn = currentValue
                
    except getopt.error as err:
        print (str(err))
        exit(1)

    print("User: " + user)
    print("Pass: " + password)
    print("Ship MRN:  " + shipmrn)
    print("Shore MRN:  " + shoremrn)

    wsh = WebSocketHandler(user, password, shipmrn, shoremrn)
    ws = websocket.WebSocketApp(baseUrl + "/interfaces/mms/socket",
                              on_open=wsh.OnOpen,
                              on_message=wsh.OnMessage,
                              on_error=wsh.OnError,
                              on_close=wsh.OnClose)

    ws.run_forever()
    
