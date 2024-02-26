import RPi.GPIO as GPIO
import time

RESETPin = 23   # Broadcom pin 23 (Pi pin 16)
BUSYPin = 24    # Broadcom pin 24 (Pi pin 18)
CONVSTPin = 25  # Broadcom pin 25 (Pi pin 22)
SER1WPin = 4    # Broadcom pin 4  (Pi pin 7) Low for all data on one MISO pin.

# Pins for SPI1
SPICS0Pin = 18  # Broadcom pin 18 (Pi pin 12)
SPISCLKPin = 21 # Broadcom pin 21 (Pi pin 40)
SPIMOSIPin = 20 # Broadcom pin 20 (Pi pin 38)
SPIMISOPin = 19 # Broadcom pin 19 (Pi pin 35)
SPIMISO1Pin = 22 # Broadcom pin 22 (Pi pin 15)

GPIO.setmode(GPIO.BCM)

GPIO.setup(RESETPin, GPIO.OUT)
GPIO.setup(BUSYPin, GPIO.IN)
GPIO.setup(CONVSTPin, GPIO.OUT)
GPIO.setup(SER1WPin, GPIO.OUT)
GPIO.setup(SPICS0Pin, GPIO.OUT)
GPIO.setup(SPISCLKPin, GPIO.OUT)
GPIO.setup(SPIMOSIPin, GPIO.OUT)
GPIO.setup(SPIMISOPin, GPIO.IN)
GPIO.setup(SPIMISO1Pin, GPIO.IN)

SPIClockPeriod = 0.1 # 0.0001    # Seconds per clock cycle


def spi_idle():
    # Set defaults for output pins
    GPIO.output(SER1WPin, GPIO.HIGH)   # Low for all output on one MISO, High to use both MISO pins.
    GPIO.output(CONVSTPin, GPIO.LOW)
    GPIO.output(SPICS0Pin, GPIO.HIGH)
    GPIO.output(SPISCLKPin, GPIO.HIGH)
    GPIO.output(SPIMOSIPin, GPIO.LOW)
    time.sleep(.1)		# Let inputs stabilize before latched by high-going reset-.
    GPIO.output(RESETPin, GPIO.HIGH)
    time.sleep(.1)
    
def spi_readreg(addresses):
    # Always start with a conversion.
    GPIO.output(CONVSTPin, GPIO.HIGH)
    GPIO.output(CONVSTPin, GPIO.LOW)
    while GPIO.input(BUSYPin):
        time.sleep(.1)

    GPIO.output(SPIMOSIPin, GPIO.HIGH)

    # Return the register values in this array.  The first read value is thrown away.
    registervalues = []
    throwaway = True
    for address in addresses:
        (registervalue, _) = spi_readregister(address)
        if (not throwaway):
            registervalues.append(registervalue)
        throwaway = False

    # We retrieve the last register value with a no-op read.
    (registervalue, _) = spi_readregister(0)
    registervalues.append(registervalue)
    
    return registervalues


def spi_readregister(address):
    print('Reading register: ' + hex(address), end=" ")
    result = 0
    result1 = 0
    bitmask = 1 << 15
    sentlog = []
    receivedlog = []
    received1log = []
    senddata = (address & 0x3f) << 9
    print ('(' + hex(senddata) + ')', end=" ")
    
    GPIO.output(SPICS0Pin, GPIO.LOW)
    for _ in range(16):
        if (senddata & bitmask) != 0:
            sentlog.append('1')
        else:
            sentlog.append('0')
        bit_setting = GPIO.HIGH if (senddata & bitmask) != 0 else GPIO.LOW
        GPIO.output(SPIMOSIPin, bit_setting)
        GPIO.output(SPISCLKPin, GPIO.LOW)
        time.sleep(SPIClockPeriod / 2)
        if GPIO.input(SPIMISOPin):
            result |= bitmask
            receivedlog.append('1')
        else:
            receivedlog.append('0')
        if GPIO.input(SPIMISO1Pin):
            result1 |= bitmask
            received1log.append('1')
        else:
            received1log.append('0')
        GPIO.output(SPISCLKPin, GPIO.HIGH)
        time.sleep(SPIClockPeriod / 2)

        bitmask = bitmask >> 1
    GPIO.output(SPICS0Pin, GPIO.HIGH)

    for bit in sentlog:
        print(bit, end=" ")
    print()
    
    print('Receiving 0: ' + hex(result), end=" ")
    for bit in receivedlog:
        print(bit, end=" ")
    print()
    print('Receiving 1: ' + hex(result1), end=" ")
    for bit in received1log:
        print(bit, end=" ")
    print()

    spi_idle()
    return (result, result1)
    
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
            if GPIO.input(SPIMISO1Pin):
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
    #GPIO.output(RESETPin, GPIO.HIGH)
    #time.sleep(.1)

    spi_idle()
    response = spi_xfer([0x86bb])
    response = spi_readreg([0x02, 0x03, 0x04, 0x05, 0x06, 0x07])
    response = spi_xfer([0x0400, 0x0600, 0x0800])
    response = spi_xfer([0x0000, 0x0000, 0x0000])
    
except KeyboardInterrupt:
    print('Interrupt')
    
GPIO.cleanup()
    

