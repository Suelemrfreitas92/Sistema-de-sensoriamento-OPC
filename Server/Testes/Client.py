from opcua import Client
from flask import Flask, render_template, url_for, Response, flash, request, send_file

import threading
import time
import sys
import json 

sys.path.insert(0, "..") #Saber de onde vai importar os arquivos do flask

app = Flask(__name__) #Aplicativo http de servidor

#Variáveis Globais
OPC_client = None
run = True

#Vetor de dados para o gráfico 
dadosArray = {
    'series': [],
    'labels': []
}
dadosArray1 = {
    'series1': [],
    'labels1': []
}


# Rotas HTTP
@app.route('/')
def HelloWorld():
    global OPC_client
    if OPC_client != None:
        return str(OPC_client.get_node("ns=2;i=2").get_value()) + str("    ") + str(OPC_client.get_node("ns=2;i=3").get_value().strftime("%Y-%m-%d     %H:%M:%S"))
    else:
        return "Sem Valor"

#Rota http para requisito de dados - Retorna um json. 
@app.route('/sensor_value')
def getWebSensorData():
    global OPC_client
    if OPC_client != None:

       
        sensor_data={

            
            'dadosgrafico': dadosArray,         #Coloca os dados do vetor no JSON
            'dadosgrafico1':dadosArray1,
            'sensor1': str(OPC_client.get_node("ns=2;i=2").get_value()), #variavel que será encapsulada no json
            'sensor2': str(OPC_client.get_node("ns=2;i=3").get_value().strftime("%Y-%m-%d     %H:%M:%S")), #variavel que será encapsulada no json
            'sensor3': str(OPC_client.get_node("ns=2;i=5").get_value()), #variavel que será encapsulada no json
            'sensor4': str(OPC_client.get_node("ns=2;i=6").get_value().strftime("%Y-%m-%d     %H:%M:%S")) #variavel que será encapsulada no json
                
            
        }


        return json.dumps(sensor_data)
    else:
        return json.dumps({"ERROR!":"Client não iniciado"})

#Retorna a página HTML
@app.route('/index', methods=['GET'])
def index():

  return render_template('index.html')
    
# Inicia o servidor em uma thread separada
def startServer():
    global run
    global OPC_client
    # Inicia o cliente OPCUA
    OPC_client = Client("opc.tcp://192.168.0.150:4840")
    
    try:
        # conectando OPC
        OPC_client.connect()
        root = OPC_client.get_root_node() #Objeto principal do NÓ do OPC ( espeficicado no server)
        myData1 = root.get_child(["0:Objects", "2:MyObject", "2:MyData1"]) #identifica um filho do Nó principal
        myDataDatetime = root.get_child(["0:Objects", "2:MyObject", "2:MyDataDatetime"])#identifica um filho do Nó principal
        #(NÓ, OBJETO DO NÓ,FILHO)
        obj = root.get_child(["0:Objects", "2:MyObject"])
        print("myobj is: ", obj)
        print("myData1 is: ", myData1)
        print("myDataDatetime is: ", myDataDatetime)


        myData2 = root.get_child(["0:Objects", "2:MyObject1", "2:MyData2"]) #identifica um filho do Nó principal
        myDataDatetime1 = root.get_child(["0:Objects", "2:MyObject1", "2:MyDataDatetime1"])#identifica um filho do Nó principal
        #(NÓ, OBJETO DO NÓ,FILHO)
        obj1 = root.get_child(["0:Objects", "2:MyObject1"])
        print("myobj1 is: ", obj1)
        print("myData2 is: ", myData2)
        print("myDataDatetime1 is: ", myDataDatetime1)

        while run:
            print("myData1 = %4.1f" %OPC_client.get_node(myData1).get_value())
            print("myDataDatetime = ", OPC_client.get_node(myDataDatetime).get_value().strftime("%Y-%m-%d     %H:%M:%S"))
            
            print("myData2 = %4.1f" %OPC_client.get_node(myData2).get_value())
            print("myDataDatetime1 = ", OPC_client.get_node(myDataDatetime1).get_value().strftime("%Y-%m-%d     %H:%M:%S"))
            
            
            time.sleep(2)   
            dadosArray['series'].append(OPC_client.get_node(myData1).get_value()) #adiciona os dados no final da fila conforme é atualizado e salva em series para o chartist entender
            dadosArray['labels'].append(OPC_client.get_node(myDataDatetime).get_value().strftime("%Y-%m-%d     %H:%M:%S"))#adiciona os dados no final da fila conforme é atualizado e salva em labels para o chartist entender


            dadosArray1['series1'].append(OPC_client.get_node(myData2).get_value()) #adiciona os dados no final da fila conforme é atualizado e salva em series para o chartist entender
            dadosArray1['labels1'].append(OPC_client.get_node(myDataDatetime1).get_value().strftime("%Y-%m-%d     %H:%M:%S"))#adiciona os dados no final da fila conforme é atualizado e salva em labels para o chartist entender



            #corta a mensagem se for muito grande
            if len(dadosArray['series']) > 22:
                
                dadosArray['series'].pop(0) #Tirar dados antigo do começo da fila
                dadosArray['labels'].pop(0) #Tirar dados antigo do começo da fila


            if len(dadosArray1['series1']) > 22:
                
                dadosArray1['series1'].pop(0) #Tirar dados antigo do começo da fila
                dadosArray1['labels1'].pop(0) #Tirar dados antigo do começo da fila


    finally:
        OPC_client.disconnect()
    
if __name__ == "__main__":

    #Onde fica salvo o objeto que controla a thread - Handler
    threadOpc = threading.Thread(target=startServer)
    #inicia o client OPC
    threadOpc.start()

    #rodar os dois servidores ao mesmo tempo
    print("Iniciando servidor HTTP")
    app.run(host="0.0.0.0")
    run = False
    threadOpc.join()
   



