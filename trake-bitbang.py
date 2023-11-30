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
    # Change channel register to select the self-test channel (0xbbbb and 0x5555)
    response0, response1 = spi.xfer2([0x86bb])

    # Read all registers back, just for display
    response0, response1 = spi.xfer2([0x0400, 0x0600, 0x0800, 0x0a00, 0x0c00, 0x0e00, 0x0e00])

    # Read the selected self-test conversion a few times
    response0, response1 = spi.xfer2([0x0000, 0x0000, 0x0000])
    
    # Change channel register to select the channel 0 for both A and B
    response0, response1 = spi.xfer2([0x8600])
    response0, response1 = spi.xfer2([0x0000, 0x0000, 0x0000, 0x0000])

    # Set up a sequence to read all 8 pairs of registers.  Enable burst mode (all conversion with one CONVST) and sequnce mode (sequencer enabled)
    response0, response1 = spi.xfer2([0xc000, 0xc211, 0xc422, 0xc633, 0xc844, 0xca55, 0xcc66, 0xcf77, 0x8460])

    # Read the selected conversion continuously
    while True:
        response0, response1 = spi.xfer2([0x0000, 0x0000, 0x0000, 0x0000,   0x0000, 0x0000, 0x0000, 0x0000])
        time.sleep(.1)

except KeyboardInterrupt:
    print('Interrupt')
    
GPIO.cleanup()
    


