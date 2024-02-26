import RPi.GPIO as GPIO
import time
import spidev

bus = 1      # 0 or 1 for SPI0 or SPI1
device = 0   # 0 or 1 for CE0 or CE1

RESETPin = 23   # Broadcom pin 23 (Pi pin 16)
BUSYPin = 24    # Broadcom pin 24 (Pi pin 18)
CONVSTPin = 25  # Broadcom pin 25 (Pi pin 22)
SER1WPin = 4    # Broadcom pin 4  (Pi pin 7) Low for all data on one MISO pin.

GPIO.setmode(GPIO.BCM)
GPIO.setup(RESETPin, GPIO.OUT)
GPIO.setup(BUSYPin, GPIO.IN)
GPIO.setup(CONVSTPin, GPIO.OUT)
GPIO.setup(SER1WPin, GPIO.OUT)

# Enable SPI
spi = spidev.SpiDev()

# Open a connection to a specific bus and device (chip select pin)
spi.open(bus, device)

# Set SPI speed and mode
spi.max_speed_hz = 500000
spi.mode = 0   # 0000 00<polarity><phase>  2 LSBs determine polarity and phase of clock.

spi.bits_per_word = 16
print('Bits per word: ' + str(spi.bits_per_word))



GPIO.cleanup()
    

        
