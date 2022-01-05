from opcua import Client
import time
import sys
import datetime
import asyncio
import smbus
import dht11
import RPi.GPIO as GPIO

sys.path.insert(0, "..")


#configurações barramento I2C
I2C_BUS = None
b1 = None
I2C_ADDRESS = 0x48

# configurações gpio
GPIO_PIN = 13
ACTUATOR_LO = True
ACTUATOR_HI = False

def readDHT11():
    GPIO.setmode(GPIO.BOARD)
    pino_sensor = 22
    sensor = dht11.DHT11(pino_sensor)
    dados = sensor.read()

    return [dados.temperature, dados.humidity]

def read_i2c (control):
    global I2C_ADDRESS
    global I2C_BUS

    write = I2C_BUS.write_byte_data(I2C_ADDRESS, control, 0)
    read = I2C_BUS.read_byte(I2C_ADDRESS)
    return read

def leituraBmp280():
    global b1

    dig_T1 = b1[1] * 256 + b1[0]
    dig_T2 = b1[3] * 256 + b1[2]
    if dig_T2 > 32767 :
        dig_T2 -= 65536
    dig_T3 = b1[5] * 256 + b1[4]
    if dig_T3 > 32767 :
        dig_T3 -= 65536
    
    # Pressure coefficents
    dig_P1 = b1[7] * 256 + b1[6]
    dig_P2 = b1[9] * 256 + b1[8]
    if dig_P2 > 32767 :
        dig_P2 -= 65536
    dig_P3 = b1[11] * 256 + b1[10]
    if dig_P3 > 32767 :
        dig_P3 -= 65536
    dig_P4 = b1[13] * 256 + b1[12]
    if dig_P4 > 32767 :
        dig_P4 -= 65536
    dig_P5 = b1[15] * 256 + b1[14]
    if dig_P5 > 32767 :
        dig_P5 -= 65536
    dig_P6 = b1[17] * 256 + b1[16]
    if dig_P6 > 32767 :
        dig_P6 -= 65536
    dig_P7 = b1[19] * 256 + b1[18]
    if dig_P7 > 32767 :
        dig_P7 -= 65536
    dig_P8 = b1[21] * 256 + b1[20]
    if dig_P8 > 32767 :
        dig_P8 -= 65536
    dig_P9 = b1[23] * 256 + b1[22]
    if dig_P9 > 32767 :
        dig_P9 -= 65536
    
    # Endereço BMP280, 0x76(118)
    I2C_BUS.write_byte_data(0x76, 0xF4, 0x27)
    I2C_BUS.write_byte_data(0x76, 0xF5, 0xA0)
    time.sleep(0.5)
    
    # BMP280 address, 0x76(118)
    # Read data back from 0xF7(247), 8 bytes
    data = I2C_BUS.read_i2c_block_data(0x76, 0xF7, 8)
    
    # Convert pressure and temperature data to 19-bits
    adc_p = ((data[0] * 65536) + (data[1] * 256) + (data[2] & 0xF0)) / 16
    adc_t = ((data[3] * 65536) + (data[4] * 256) + (data[5] & 0xF0)) / 16
    
    # Calculo Temperatura
    var1 = ((adc_t) / 16384.0 - (dig_T1) / 1024.0) * (dig_T2)
    var2 = (((adc_t) / 131072.0 - (dig_T1) / 8192.0) * ((adc_t)/131072.0 - (dig_T1)/8192.0)) * (dig_T3)
    t_fine = (var1 + var2)
    cTemp = (var1 + var2) / 5120.0
    fTemp = cTemp * 1.8 + 32
    
    # Calculo Pressão
    var1 = (t_fine / 2.0) - 64000.0
    var2 = var1 * var1 * (dig_P6) / 32768.0
    var2 = var2 + var1 * (dig_P5) * 2.0
    var2 = (var2 / 4.0) + ((dig_P4) * 65536.0)
    var1 = ((dig_P3) * var1 * var1 / 524288.0 + ( dig_P2) * var1) / 524288.0
    var1 = (1.0 + var1 / 32768.0) * (dig_P1)
    p = 1048576.0 - adc_p
    p = (p - (var2 / 4096.0)) * 6250.0 / var1
    var1 = (dig_P9) * p * p / 2147483648.0
    var2 = p * (dig_P8) / 32768.0
    pressure = (p + (var1 + var2 + (dig_P7)) / 16.0) / 100

    return [cTemp, fTemp, pressure]

def configGPIO():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(GPIO_PIN, GPIO.OUT)
    GPIO.output(GPIO_PIN, ACTUATOR_LO)
    print("GPIO initialized")

if __name__ == "__main__":
    OPCClient = Client("opc.tcp://18.116.26.203:4840")
    timerSensorRefresh = time.time()
    try:
        # Get I2C bus
        I2C_BUS = smbus.SMBus(1)
        print("I2C inicializado!")
        # BMP280 address, 0x76(118)
        # Read data back from 0x88(136), 24 bytes
        b1 = I2C_BUS.read_i2c_block_data(0x76, 0x88, 24)
        
        configGPIO()

        # connecting!
        print("Conectando...")
        OPCClient.connect()
        print("Conectado ao Servidor OPCUA")

        #Informações vindas do servidor
        datasensor = OPCClient.get_root_node()
        date = datasensor.get_child(["0:Objects", "2:MyObject", "2:MyDataDatetime"])
        sensor_Temp1 = datasensor.get_child(["0:Objects", "2:MyObject", "2:Temp1"])
        sensor_Temp2 = datasensor.get_child(["0:Objects", "2:MyObject", "2:Temp2"])
        sensor_Press = datasensor.get_child(["0:Objects", "2:MyObject", "2:Press1"])
        Poti = datasensor.get_child(["0:Objects", "2:MyObject", "2:Poti1"])
        sensor_Umidade = datasensor.get_child(["0:Objects", "2:MyObject", "2:Umidade1"])
        atuador = datasensor.get_child(["0:Objects", "2:MyObject", "2:Atuador1"])
        sensor = datasensor.get_child(["0:Objects", "2:MyObject"])
        obj = datasensor.get_child(["0:Objects", "2:MyObject"])
        
        print("Setup complete!")

    except Exception as ex:
        print(ex)
        print("FALHA NA INICIALIZAÇÃO! Saindo...")
        sys.exit(-1)

    ultimoValorAtuador = False
    while True:
        try:
            timeNow = time.time()
            if timeNow - timerSensorRefresh > 3:
                print("[SENSOR] Update sensor values")
                sensorDHT11 = readDHT11()
                sensorBMP280 = leituraBmp280()
                Potenciometro = read_i2c(0x41)
                print(sensorDHT11[1])

                if sensorDHT11[0] == 0 or sensorDHT11[1] == 0:
                    sensorDHT11 = readDHT11()
                
                date.set_value(datetime.datetime.now())
                sensor_Temp1.set_value(sensorBMP280[0])
                sensor_Temp2.set_value(sensorDHT11[0])
                sensor_Press.set_value(sensorBMP280[2])
                Poti.set_value(Potenciometro)
                sensor_Umidade.set_value(sensorDHT11[1])
                timerSensorRefresh = timeNow
            
            # Ler valor do atuador
            valorAtuador = atuador.get_value()
            if valorAtuador != ultimoValorAtuador:
                GPIO.output(GPIO_PIN, 0 if valorAtuador else 1)
                ultimoValorAtuador = valorAtuador
                print("Atuador set:", 0 if valorAtuador else 1)
            
            time.sleep(0.1)


        except (BrokenPipeError, asyncio.TimeoutError, asyncio.CancelledError) as ex:
            print(ex)
            print("Erro: conexão OPCUA perdida. Saindo...")
            try:
                OPCClient.disconnect()
            finally:
                sys.exit(-1)

        # except Exception as ex:
        #     print(ex)

