import RPi.GPIO as GPIO
import time
import spibang

# Enable SPI
spi = spibang.SpiBang()

# Open a connection to a specific bus and device (chip select pin)
spi.open(bus=0, device=0)

# Set SPI speed and mode
spi.max_speed_hz = 10000
spi.mode = 0   # 0000 00<polarity><phase>  2 LSBs determine polarity and phase of clock.


try:
    response0, response1 = spi.xfer2([0x86bb])
    response0, response1 = spi.xfer2([0x0400, 0x0600, 0x0800])
    response0, response1 = spi.xfer2([0x0000, 0x0000, 0x0000])
    
except KeyboardInterrupt:
    print('Interrupt')
    
GPIO.cleanup()
    


