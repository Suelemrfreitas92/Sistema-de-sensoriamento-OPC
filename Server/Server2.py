from opcua import ua, Server
from flask import Flask, render_template, url_for, Response, flash, request, send_file, jsonify
import sys
import time
import threading
import json



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
    ["Hora","BMPTemp", "DHT11Temp"]
]

dadosArrayU = [
    ["Hora","DHT11Umi"]
]

dadosArrayP = [
    ["Hora","BMPPress"]
]

dadosArrayL = [
    ["Hora","Poti"]
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
    node = OPC_server["server"].get_objects_node()

    # Variáveis criadas - Referentes aos sensores
    sensores = node.add_object(OPC_server["index"], "MyObject")
    sensor_Temp1 = sensores.add_variable(OPC_server["index"], "Temp1",0)
    sensor_Temp2 = sensores.add_variable(OPC_server["index"], "Temp2",0)
    sensor_Press = sensores.add_variable(OPC_server["index"],"Press1",0)
    Poti = sensores.add_variable(OPC_server["index"],"Poti1",0)
    sensor_Umidade = sensores.add_variable(OPC_server["index"],"Umidade1",0)
    atuador = sensores.add_variable(OPC_server["index"], "Atuador1", 0)
    myDataDatetime = sensores.add_variable(OPC_server["index"], "MyDataDatetime", None)

    '''potentiometer = objects.add_object(OPC_server["index"], "MyObject")
    pot1 = potentiometer.add_variable(OPC_server["index"], "MyData1", 0)'''


    sensor_Temp1.set_writable()    # Set MyVariable to be writable by clients
    sensor_Temp2.set_writable()
    sensor_Press.set_writable()
    Poti.set_writable()
    sensor_Umidade.set_writable()
    myDataDatetime.set_writable()    # Set MyVariable to be writable by clients 
    atuador.set_writable()  

def startHttp():
    app.run(host="0.0.0.0")
    run = False




# Rotas HTTP

@app.route('/sensor_value')
def getWebSensorData():
    global OPC_server
    BMPTemp1 = OPC_server["server"].get_node("ns=2;i=2").get_value()
    BMPpress = OPC_server["server"].get_node("ns=2;i=3").get_value()
    DHT11Temp1 = OPC_server["server"].get_node("ns=2;i=4").get_value()
    Potenciometro = OPC_server["server"].get_node("ns=2;i=5").get_value()
    DHT11_Umi = OPC_server["server"].get_node("ns=2;i=6").get_value()
    atuador = OPC_server["server"].get_node("ns=2;i=7")
    Data = OPC_server["server"].get_node("ns=2;i=8").get_value().timestamp()
    if(Data == None):
        print('Aguardando Conexão Client')
    if DHT11_Umi == 0:
        DHT11_Umi = OPC_server["server"].get_node("ns=2;i=6").get_value()
    
    sensor_data={
            'dadosgraficoT': dadosArrayT,         #Coloca os dados do vetor no JSON
            'dadosgraficoU': dadosArrayU,
            'dadosgraficoP': dadosArrayP,
            'dadosgraficoL':dadosArrayL,
            'myDate': Data #variavel que será encapsulada no json
        
    }
    return jsonify(sensor_data)


@app.route('/index', methods=['GET'])
def index():
    return render_template('index_new.html')

#TESTEE 
@app.route('/login', methods=["POST", "GET"])
def login():
    return render_template('login.html')


@app.route('/actuator', methods=['POST'])
def setActuator():
    global atuador

    if request.is_json:
        payload = request.get_json()

        if payload["shouldEnable"] is not None:
            atuador.set_value(1 if payload["shouldEnable"] else 0)
            return jsonify({'msg': "Success", 'status': payload["shouldEnable"]})
        else:
            return "Invalid value", 400
    else:
        return "No JSON found", 400


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
        sensor_Temp1 = root.get_child(["0:Objects", "2:MyObject", "2:Temp1"])
        sensor_Temp2 = root.get_child(["0:Objects", "2:MyObject", "2:Temp2"])
        sensor_Press = root.get_child(["0:Objects", "2:MyObject", "2:Press1"])
        Potenciometro = root.get_child(["0:Objects", "2:MyObject", "2:Poti1"])
        sensor_Umidade = root.get_child(["0:Objects", "2:MyObject", "2:Umidade1"])
        atuador = root.get_child(["0:Objects", "2:MyObject", "2:Atuador1"])
        myDataDatetime = root.get_child(["0:Objects", "2:MyObject", "2:MyDataDatetime"])
        sensor = root.get_child(["0:Objects", "2:MyObject"])

        '''root1 = OPC_server["server"].get_root_node()
        pot1 = root1.get_child(["1:Objects", "2:MyObject", "2:MyData1"])'''

        #rodar os dois servidores ao mesmo tempo
        print("Iniciando servidor HTTP")
        while True:
            '''print((OPC_server["server"].get_node(myDataDatetime).get_value()))
            print("myDataDatetime = ", OPC_server["server"].get_node("ns=2;i=4").get_value())'''
            '''time.sleep(1)'''
            time.sleep(3)   
            
            
            lastDatetime = OPC_server["server"].get_node(myDataDatetime).get_value()
            lastTempS1 = OPC_server["server"].get_node(sensor_Temp1).get_value()
            lastTempS2 = OPC_server["server"].get_node(sensor_Temp2).get_value()
            lastPress = OPC_server["server"].get_node(sensor_Press).get_value()
            lastPoti = OPC_server["server"].get_node(Potenciometro).get_value()
            lastUmid = OPC_server["server"].get_node(sensor_Umidade).get_value()

            if lastTempS2 == 0:
                lastTempS2 = OPC_server["server"].get_node(sensor_Temp2).get_value()


            if(lastDatetime != None):
                #dadosArrayG.append([lastDatetime.strftime("%Y-%m-%d     %H:%M:%S"), lastTempS1, lastTempS2])
                if lastTempS2 == 0 or lastUmid == 0:
                    lastTempS2 = OPC_server["server"].get_node(sensor_Temp2).get_value()
                    lastUmid = OPC_server["server"].get_node(sensor_Umidade).get_value()
                dadosArrayT.append([lastDatetime.strftime("%Y-%m-%d     %H:%M:%S"), lastTempS1, lastTempS2])
                dadosArrayU.append([lastDatetime.strftime("%Y-%m-%d     %H:%M:%S"), lastUmid])
                dadosArrayP.append([lastDatetime.strftime("%Y-%m-%d     %H:%M:%S"), lastPress])
                dadosArrayL.append([lastDatetime.strftime("%Y-%m-%d     %H:%M:%S"), lastPoti])


            #corta a mensagem se for muito grande
            if len(dadosArrayT) > 1500:
                dadosArrayT.pop(1) #Tirar dados antigo do começo da fila
            if len(dadosArrayU) > 1500:
                dadosArrayU.pop(1) #Tirar dados antigo do começo da fila
            if len(dadosArrayP) > 1500:
                dadosArrayP.pop(1)
            if len(dadosArrayL) > 1500: 
                dadosArrayL.pop(1)



            # if len(dadosArray1['series1']) > 22:
                
            #   dadosArray1['series1'].pop(0) #Tirar dados antigo do começo da fila
            #   dadosArray1['labels1'].pop(0) #Tirar dados antigo do começo da fila

    finally:
        #close connection, remove subcsriptions, etc
        OPC_server["server"].stop()