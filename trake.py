import RPi.GPIO as GPIO
import time
import spidev

bus = 0      # 0 or 1 for SPI0 or SPI1
device = 0   # 0 or 1 for CE0 or CE1

RESETPin = 23  # Broadcom pin 23 (Pi pin 16)
CONVSTPin = 25 # Broadcom pin 25 (Pi pin 22)

GPIO.setmode(GPIO.BCM)
GPIO.setup(CONVSTPin, GPIO.OUT)
GPIO.setup(RESETPin, GPIO.OUT)

# Enable SPI
spi = spidev.SpiDev()

# Open a connection to a specific bus and device (chip select pin)
spi.open(bus, device)

# Set SPI speed and mode
spi.max_speed_hz = 500000
spi.mode = 0   # 0000 00<polarity><phase>  2 LSBs determine polarity and phase of clock.

print('Bits per word: ' + str(spi.bits_per_word))

TestCommand = [0x86, 0xbb]
StatusReg = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00]


print('Setting RESET high and CONVST Low')
GPIO.output(RESETPin, GPIO.HIGH)
GPIO.output(CONVSTPin, GPIO.LOW)

try:
    print('Resetting the A/D')
    GPIO.output(RESETPin, GPIO.LOW)
    time.sleep(.1)
    GPIO.output(RESETPin, GPIO.HIGH)
    
    while True:
        print('Loop')
        GPIO.output(CONVSTPin, GPIO.LOW)
        time.sleep(.1)
        GPIO.output(CONVSTPin, GPIO.HIGH)
        time.sleep(1)

        TestCommand = [0x86, 0xbb]
        spi.xfer2(TestCommand)

        ChannelA = [0x00, 0x00]
        ChannelB = [0x00, 0x00]
        spi.xfer2(ChannelA)
        spi.xfer2(ChannelB)
        print('Conversion A: ' + str(ChannelA[0]) + ' ' + str(ChannelA[1]) + ' B:' + str(ChannelB[0]) + ' ' + str(ChannelB[1]))
except KeyboardInterrupt:
    GPIO.cleanup()
    

        
