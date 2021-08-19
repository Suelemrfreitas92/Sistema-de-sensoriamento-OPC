from opcua import ua, Server
from flask import Flask, render_template, url_for, Response, flash, request, send_file
import sys
import time
import threading
import json

from werkzeug.utils import redirect
from models.forms import LoginForm


sys.path.insert(0, "..")

app = Flask(__name__) #Aplicativo http de servidor

OPC_server = {
    "index": None,
    "uri": "SuelemDaiane",
    "endpoint": "opc.tcp://192.168.0.150:4840",
    "server": None
}
run = True
lastDatetime = None

dadosArray = {
    'series': [],
    'series1': [],
    'labels': [],
}

'''dadosArrayG = [ #DEBUG SUELEM
    ["Hora", "BMP-Temp.", "BMP-Pressão"]
]'''

dadosArrayT = [
    ["Hora","BMPTemp"]
]

dadosArrayP = [
    ["Hora","BMPPress"]
]

dadosArrayL = [
    ["Hora","Light"]
]


def startServer():
    """Inicializa e configura o servidor OPCUA"""
    global run
    global OPC_server

    # setup our server
    OPC_server["server"] = Server()
    
    # setup our own namespace, not really necessary but should as spec
    OPC_server["index"] = OPC_server["server"].register_namespace(OPC_server["uri"])
    #OPC_server["server"].set_endpoint(OPC_server["endpoint"])

    initializeOpcObjects()

def initializeOpcObjects():
    """Configura os objetos no servidor OPC."""
    global OPC_server
    # get Objects node, this is where we should put our nodes
    objects = OPC_server["server"].get_objects_node()

    # populating our address space
    sensor = objects.add_object(OPC_server["index"], "MyObject")
    sensor_Temp1 = sensor.add_variable(OPC_server["index"], "MyData1", 0)
    sensor_Press = sensor.add_variable(OPC_server["index"],"MyData2",0)
    sensor_Light = sensor.add_variable(OPC_server["index"],"MyData3",0)
    myDataDatetime = sensor.add_variable(OPC_server["index"], "MyDataDatetime", None)

    '''potentiometer = objects.add_object(OPC_server["index"], "MyObject")
    pot1 = potentiometer.add_variable(OPC_server["index"], "MyData1", 0)'''


    sensor_Temp1.set_writable()    # Set MyVariable to be writable by clients
    sensor_Press.set_writable()
    sensor_Light.set_writable()
    myDataDatetime.set_writable()    # Set MyVariable to be writable by clients 
    #pot1.set_writable()  

def startHttp():
    app.run(host="0.0.0.0")
    run = False




# Rotas HTTP

@app.route('/')
def HelloWorld():
    global OPC_server

    root = OPC_server["server"].get_root_node()
    sensor_Temp1 = root.get_child(["0:Objects", "2:MyObject", "2:MyData1"])
    sensor_Press = root.get_child(["0:Objects", "2:MyObject", "2:MyData2"])
    myDataDatetime = root.get_child(["0:Objects", "2:MyObject", "2:MyDataDatetime"])
    return str(OPC_server["server"].get_node(sensor_Temp1).get_value()) + "  " + str(OPC_server["server"].get_node(myDataDatetime).get_value())

@app.route('/sensor_value')
def getWebSensorData():
    global OPC_server
    BMPTemp1 = OPC_server["server"].get_node("ns=2;i=2").get_value()
    BMPpress = OPC_server["server"].get_node("ns=2;i=3").get_value()
    Light = OPC_server["server"].get_node("ns=2;i=4").get_value()
    Data = OPC_server["server"].get_node("ns=2;i=5").get_value().timestamp()
    if(Data == None):
        print('Aguardando Conexão Client')

    sensor_data={
            'dadosgraficoT': dadosArrayT,         #Coloca os dados do vetor no JSON
            'dadosgraficoP': dadosArrayP,
            'dadosgraficoL':dadosArrayL,
            #'dadosgrafico1':dadosArray1,
            'BMPTemp': BMPTemp1, #variavel que será encapsulada no json
            'BMP-Pressão':BMPpress,
            'myDate': Data #variavel que será encapsulada no json
        
    }
    return json.dumps(sensor_data)
    


@app.route('/index', methods=['GET'])
def index():
    return render_template('index_new.html')

#TESTEE 
@app.route('/login', methods=["POST", "GET"])
def login():
    return render_template('login.html')


#TESTE
if __name__ == "__main__":
    
    # starting!
    startServer()
    threadOpc = threading.Thread(target=OPC_server["server"].start)
    threadOpc.setDaemon(True)
    # inicia o server OPC
    threadOpc.start()

    threadHTTP = threading.Thread(target=startHttp)
    threadHTTP.setDaemon(True)
    # Inicia o server HTTP
    threadHTTP.start()
    try:
        root = OPC_server["server"].get_root_node()
        sensor_Temp1 = root.get_child(["0:Objects", "2:MyObject", "2:MyData1"])
        sensor_Press = root.get_child(["0:Objects", "2:MyObject", "2:MyData2"])
        sensor_Light = root.get_child(["0:Objects", "2:MyObject", "2:MyData3"])

        myDataDatetime = root.get_child(["0:Objects", "2:MyObject", "2:MyDataDatetime"])
        sensor = root.get_child(["0:Objects", "2:MyObject"])

        '''root1 = OPC_server["server"].get_root_node()
        pot1 = root1.get_child(["1:Objects", "2:MyObject", "2:MyData1"])'''

        #rodar os dois servidores ao mesmo tempo
        print("Iniciando servidor HTTP")
        while True:
            #print((OPC_server["server"].get_node(myDataDatetime).get_value()))
            print("myDataDatetime = ", OPC_server["server"].get_node("ns=2;i=4").get_value())
            '''time.sleep(1)'''
            time.sleep(2)   
            
            lastDatetime = OPC_server["server"].get_node(myDataDatetime).get_value()
            lastTempS1 = OPC_server["server"].get_node(sensor_Temp1).get_value()
            lastPress = OPC_server["server"].get_node(sensor_Press).get_value()
            lastLight = OPC_server["server"].get_node(sensor_Light).get_value()

            if(lastDatetime != None):
                #dadosArrayG.append([lastDatetime.strftime("%Y-%m-%d     %H:%M:%S"), lastTempS1, lastTempS2])
                dadosArrayT.append([lastDatetime.strftime("%Y-%m-%d     %H:%M:%S"), lastTempS1])
                dadosArrayP.append([lastDatetime.strftime("%Y-%m-%d     %H:%M:%S"), lastPress])
                dadosArrayL.append([lastDatetime.strftime("%Y-%m-%d     %H:%M:%S"), lastLight])

                #dadosArray['series'].append(lastTempS1) #adiciona os dados no final da fila conforme é atualizado e salva em series para o chartist entender
                #dadosArray['series1'].append(lastTempS2)
                #dadosArray['labels'].append(lastDatetime.strftime("%Y-%m-%d     %H:%M:%S"))#adiciona os dados no final da fila conforme é atualizado e salva em labels para o chartist entender


            #dadosArray1['series1'].append(OPC_server["server"]t.get_node(myData2).get_value()) #adiciona os dados no final da fila conforme é atualizado e salva em series para o chartist entender
            #dadosArray1['labels1'].append(OPC_server["server"].get_node(myDataDatetime1).get_value().strftime("%Y-%m-%d     %H:%M:%S"))#adiciona os dados no final da fila conforme é atualizado e salva em labels para o chartist entender



            #corta a mensagem se for muito grande
            if len(dadosArray) > 22:
                dadosArray.pop(1) #Tirar dados antigo do começo da fila


            # if len(dadosArray1['series1']) > 22:
                
            #   dadosArray1['series1'].pop(0) #Tirar dados antigo do começo da fila
            #   dadosArray1['labels1'].pop(0) #Tirar dados antigo do começo da fila

    finally:
        #close connection, remove subcsriptions, etc
        OPC_server["server"].stop()