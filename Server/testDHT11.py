# Programa : Sensor de temperatura DHT11 com Raspberry Pi
# Autor : FILIPEFLOP

# Carrega as bibliotecas
import dht11
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

# Define a GPIO conectada ao pino de dados do sensor
pino_sensor = 22

# Define o tipo de sensor
sensor = dht11.DHT11(pino_sensor)
#sensor = Adafruit_DHT.DHT22

# Informacoes iniciais
print("*** Lendo os valores de temperatura e umidade")

while(1):
    # Efetua a leitura do sensor
    dados = sensor.read()
    # Caso leitura esteja ok, mostra os valores na tela
    if dados is not None:
        print(dados.temperature, dados.humidity)
        time.sleep(5)
    else:
        # Mensagem de erro de comunicacao com o sensor
        print("Falha ao ler dados do DHT11 !!!")
