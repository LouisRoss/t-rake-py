import RPi.GPIO as GPIO
import time

RESETPin = 23   # Broadcom pin 23 (Pi pin 16)
BUSYPin = 24    # Broadcom pin 24 (Pi pin 18)
CONVSTPin = 25  # Broadcom pin 25 (Pi pin 22)

SPICS0Pin = 8   # Broadcom pin 8  (Pi pin 24)
SPISCLKPin = 11 # Broadcom pin 11 (Pi pin 23)
SPIMOSIPin = 10 # Broadcom pin 10 (Pi pin 19)
SPIMISOPin = 9  # Broadcom pin 9  (Pi pin 21)
SPIMISO0Pin = 22 # Broadcom pin 22 (Pi pin 15)

GPIO.setmode(GPIO.BCM)

GPIO.setup(RESETPin, GPIO.OUT)
GPIO.setup(BUSYPin, GPIO.IN)
GPIO.setup(CONVSTPin, GPIO.OUT)
GPIO.setup(SPICS0Pin, GPIO.OUT)
GPIO.setup(SPISCLKPin, GPIO.OUT)
GPIO.setup(SPIMOSIPin, GPIO.OUT)
GPIO.setup(SPIMISOPin, GPIO.IN)
GPIO.setup(SPIMISO0Pin, GPIO.IN)

SPIClockPeriod = 0.0001    # Seconds per clock cycle


def spi_idle():
    # Set defaults for output pins
    GPIO.output(RESETPin, GPIO.HIGH)
    GPIO.output(CONVSTPin, GPIO.LOW)
    GPIO.output(SPICS0Pin, GPIO.HIGH)
    GPIO.output(SPISCLKPin, GPIO.HIGH)
    GPIO.output(SPIMOSIPin, GPIO.LOW)
    time.sleep(.1)
    
def spi_xfer(data):
    # Always start with a conversion.
    GPIO.output(CONVSTPin, GPIO.HIGH)
    GPIO.output(CONVSTPin, GPIO.LOW)
    while GPIO.input(BUSYPin):
        time.sleep(.1)

    GPIO.output(SPIMOSIPin, GPIO.HIGH)
    GPIO.output(SPICS0Pin, GPIO.LOW)

    results = []
    for value in data:
        print('Sending: ' + hex(value), end=" ")
        result = 0
        result0 = 0
        bitmask = 1 << 15
        sentlog = []
        receivedlog = []
        received0log = []
        for _ in range(16):
            if (value & bitmask) != 0:
                sentlog.append('1')
            else:
                sentlog.append('0')
            bit_setting = GPIO.HIGH if (value & bitmask) != 0 else GPIO.LOW
            GPIO.output(SPIMOSIPin, bit_setting)
            GPIO.output(SPISCLKPin, GPIO.LOW)
            time.sleep(SPIClockPeriod / 2)
            if GPIO.input(SPIMISOPin):
                result |= bitmask
                receivedlog.append('1')
            else:
                receivedlog.append('0')
            if GPIO.input(SPIMISO0Pin):
                result0 |= bitmask
                received0log.append('1')
            else:
                received0log.append('0')
            GPIO.output(SPISCLKPin, GPIO.HIGH)
            time.sleep(SPIClockPeriod / 2)

            bitmask = bitmask >> 1
        for bit in sentlog:
            print(bit, end=" ")
        print()

        results.append(result)
        print('Receiving 1: ' + hex(result), end=" ")
        for bit in receivedlog:
            print(bit, end=" ")
        print()
        print('Receiving 0: ' + hex(result0), end=" ")
        for bit in received0log:
            print(bit, end=" ")
        print()
        
    spi_idle()
    return results
    

try:
    print('Resetting the A/D')
    GPIO.output(RESETPin, GPIO.LOW)
    time.sleep(.1)
    GPIO.output(RESETPin, GPIO.HIGH)
    time.sleep(.1)

    spi_idle()
    response = spi_xfer([0x86bb])
    response = spi_xfer([0x0400, 0x0600, 0x0800])
    response = spi_xfer([0x0000, 0x0000, 0x0000])
    
except KeyboardInterrupt:
    print('Interrupt')
    
GPIO.cleanup()
    


