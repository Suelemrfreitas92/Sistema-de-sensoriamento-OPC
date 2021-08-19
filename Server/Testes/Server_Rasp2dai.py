# -*- coding: utf-8 -*-
from opcua import ua, Server
import sys
import time
import datetime
import random
sys.path.insert(0, "..")
 
if __name__ == "__main__":
   
    server = Server() #contrução de objeto na classe server
    server.set_endpoint("opc.tcp://10.244.40.88:4840") #Aponta o IP do Rasp
    
    uri = "Suelem Regina de Freitas"
    idx = server.register_namespace(uri)
  
    objects = server.get_objects_node() #Nó principal do OPCUA
   
    myobj = objects.add_object(idx, "MyObject") #Primeiro objeto do Nó
    myData1 = myobj.add_variable(idx, "MyData1", 0) #Adiciona a variável MyData no NÓ principal na posição 2
    myDataDatetime = myobj.add_variable(idx, "MyDataDatetime", 0)#Adiciona a variável MyData no NÓ principal na posição 2
    myData1.set_writable()    #permissão para gravar na variável
    myDataDatetime.set_writable()    
    # starting!
    server.start()
    try:
        rand = 0
        while True:
            time.sleep(2)
            rand = myData1.get_value()
            rand = random.randrange(1,100) #Gera um valor aleatório de 1 a 100
            myDataDatetime.set_value(datetime.datetime.now())
            myData1.set_value(rand)
    finally:
        #fecha a conexão com o OPC
        server.stop()