from opcua import Client
import time
import sys
import datetime
import random
import smbus

sys.path.insert(0, "..")

# Get I2C bus
bus = smbus.SMBus(1)
# BMP280 address, 0x76(118)
# Read data back from 0x88(136), 24 bytes
b1 = bus.read_i2c_block_data(0x76, 0x88, 24)
address = 0x48
def read (control):
    write = bus.write_byte_data (address, control, 0)
    read = bus.read_byte (address)
    return read

def leituraBmp280():
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
    # BMP280 address, 0x76(118)
    # Select Control measurement register, 0xF4(244)
    # 0x27(39) Pressure and Temperature Oversampling rate = 1
    # Normal mode
    bus.write_byte_data(0x76, 0xF4, 0x27)
    # BMP280 address, 0x76(118)
    # Select Configuration register, 0xF5(245)
    # 0xA0(00) Stand_by time = 1000 ms
    bus.write_byte_data(0x76, 0xF5, 0xA0)
    time.sleep(0.5)
    # BMP280 address, 0x76(118)
    # Read data back from 0xF7(247), 8 bytes
    # Pressure MSB, Pressure LSB, Pressure xLSB, Temperature MSB, Temperature LSB
    # Temperature xLSB, Humidity MSB, Humidity LSB
    data = bus.read_i2c_block_data(0x76, 0xF7, 8)
        # Convert pressure and temperature data to 19-bits
    adc_p = ((data[0] * 65536) + (data[1] * 256) + (data[2] & 0xF0)) / 16
    adc_t = ((data[3] * 65536) + (data[4] * 256) + (data[5] & 0xF0)) / 16
        # Temperature offset calculations
    var1 = ((adc_t) / 16384.0 - (dig_T1) / 1024.0) * (dig_T2)
    var2 = (((adc_t) / 131072.0 - (dig_T1) / 8192.0) * ((adc_t)/131072.0 - (dig_T1)/8192.0)) * (dig_T3)
    t_fine = (var1 + var2)
    cTemp = (var1 + var2) / 5120.0
    fTemp = cTemp * 1.8 + 32
    # Pressure offset calculations
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






if __name__ == "__main__":
    OPCClient = Client("opc.tcp://192.168.0.164:4840")
    

try:
        # connecting!
    OPCClient.connect()
        # Client has a few methods to get proxy to UA nodes that should always be in address space
    #Rotas da TEMPERATURA
    root = OPCClient.get_root_node()
    sensor_Temp1 = root.get_child(["0:Objects", "2:MyObject", "2:MyData1"])
    sensor_Press = root.get_child(["0:Objects", "2:MyObject", "2:MyData2"])
    sensor_Light = root.get_child(["0:Objects", "2:MyObject", "2:MyData3"])
    myDataDatetime = root.get_child(["0:Objects", "2:MyObject", "2:MyDataDatetime"])
    sensor = root.get_child(["0:Objects", "2:MyObject"])
    obj = root.get_child(["0:Objects", "2:MyObject"])


    '''root1 = OPCClient.get_root_node()
    pot1 = root1.get_child(["0:Objects", "2:MyObject", "2:MyData1"])
    obj1 = root1.get_child(["0:Objects", "2:MyObject"])'''

        #debug SUELEM
    #print("myobj is: ", obj1) 
    print("myobj is: ", sensor) 
    '''print("myData1 is: ", sensor_Temp1)
    print("myData2 is: ", sensor_Temp2)
    print("myDataDatetime is: ", myDataDatetime)'''
        
    while True:


        sensorBMP280 = leituraBmp280()
        light = read (0x41)
        
        time.sleep(2)
        #dadosS1Temp = random.randrange(1,100)
        #dadosS2Temp = random.randrange(50,100)
        myDataDatetime.set_value(datetime.datetime.now())
        sensor_Temp1.set_value(sensorBMP280[0])
        sensor_Press.set_value(sensorBMP280[2])
        sensor_Light.set_value(light)
        #pot1.set_value(poti)

        '''print("Sensor1 = %4.1f" %OPCClient.get_node(sensor_Light).get_value())
        print("Sensor1 _Fahrenheit = %4.1f" %OPCClient.get_node("ns=2;i=3").get_value())
        print("myDataDatetime = ", client.get_node("ns=2;i=3").get_value().strftime("%Y-%m-%d     %H:%M:%S"))
        time.sleep(0.4)'''            
finally:
    OPCClient.disconnect()