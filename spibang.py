import RPi.GPIO as GPIO
import time

RESETPin = 23   # Broadcom pin 23 (Pi pin 16)

ADC_BUSY_Pin = 24     # Broadcom pin 24 (Pi pin 18)
ADC_CONVST_Pin = 25   # Broadcom pin 25 (Pi pin 22)
ADC_SER1W_Pin = 23    # Broadcom pin 23 (Pi pin 16)

SPI0_CS0_Pin = 8      # Broadcom pin 8  (Pi pin 24)
SPI0_CS1_Pin = 7      # Broadcom pin 7  (Pi pin 26)
SPI0_SCLK_Pin = 11    # Broadcom pin 11 (Pi pin 23)
SPI0_MOSI_Pin = 10    # Broadcom pin 10 (Pi pin 19)
SPI0_MISO_Pin = 9     # Broadcom pin 9  (Pi pin 21)
ADC_SDOB_Pin = 22     # Broadcom pin 22 (Pi pin 15)

SPI1_CS0_Pin = 18     # Broadcom pin 18 (Pi pin 12)
SPI1_CS1_Pin = 17     # Broadcom pin 17 (Pi pin 11)
SPI1_SCLK_Pin = 21    # Broadcom pin 21 (Pi pin 40)
SPI1_MOSI_Pin = 20    # Broadcom pin 20 (Pi pin 38)
SPI1_MISO_Pin = 19    # Broadcom pin 19 (Pi pin 35)

class SpiBang:
    def __init__(self):
        # Default to bus 0, device 0
        self.spi_cs_pin = SPI0_CS0_Pin
        self.spi_sclk_pin = SPI0_SCLK_Pin
        self.spi_mosi_pin = SPI0_MOSI_Pin
        self.spi_miso_pin = SPI0_MISO_Pin

        self.max_speed_hz = 10000
        self.min_period_sec = 1 / self.max_speed_hz
        self.mode = 0   # 0000 00<polarity><phase>  2 LSBs determine polarity and phase of clock.
        GPIO.setmode(GPIO.BCM)

        print('Resetting the A/D')
        GPIO.setup(RESETPin, GPIO.OUT)

        GPIO.output(RESETPin, GPIO.LOW)
        time.sleep(.1)
        GPIO.output(RESETPin, GPIO.HIGH)
        time.sleep(.1)


    def open(self, bus, device):
        if bus == 0:
            if device == 0:
                self.spi_cs_pin = SPI0_CS0_Pin
            else:
                self.spi_cs_pin = SPI0_CS1_Pin
            self.spi_sclk_pin = SPI0_SCLK_Pin
            self.spi_mosi_pin = SPI0_MOSI_Pin
            self.spi_miso_pin = SPI0_MISO_Pin
        else:
            if device == 0:
                self.spi_cs_pin = SPI1_CS0_Pin
            else:
                self.spi_cs_pin = SPI1_CS1_Pin
            self.spi_sclk_pin = SPI1_SCLK_Pin
            self.spi_mosi_pin = SPI1_MOSI_Pin
            self.spi_miso_pin = SPI1_MISO_Pin

        GPIO.setup(ADC_BUSY_Pin, GPIO.IN)
        GPIO.setup(ADC_CONVST_Pin, GPIO.OUT)
        GPIO.setup(self.spi_cs_pin, GPIO.OUT)
        GPIO.setup(self.spi_sclk_pin, GPIO.OUT)
        GPIO.setup(self.spi_mosi_pin, GPIO.OUT)
        GPIO.setup(self.spi_miso_pin, GPIO.IN)
        GPIO.setup(ADC_SER1W_Pin, GPIO.IN)

        self.spi_idle()


    def spi_idle(self):
        # Set defaults for output pins
        GPIO.output(ADC_CONVST_Pin, GPIO.LOW)
        GPIO.output(self.spi_cs_pin, GPIO.HIGH)
        GPIO.output(self.spi_sclk_pin, GPIO.HIGH)
        GPIO.output(self.spi_mosi_pin, GPIO.LOW)
    

    def xfer2(self, outbuffer):
        # Always start with a conversion.
        GPIO.output(ADC_CONVST_Pin, GPIO.HIGH)
        GPIO.output(ADC_CONVST_Pin, GPIO.LOW)
        while GPIO.input(ADC_BUSY_Pin):
            time.sleep(.001)

        GPIO.output(self.spi_mosi_pin, GPIO.HIGH)
        GPIO.output(self.spi_cs_pin, GPIO.LOW)

        result0buffer = []
        result1buffer = []
        for value in outbuffer:
            print('Sending: ' + hex(value), end=' ')
            result0 = 0
            result1 = 0

            bitmask = 1 << 15
            for _ in range(16):
                bit_setting = GPIO.HIGH if (value & bitmask) != 0 else GPIO.LOW
                GPIO.output(self.spi_mosi_pin, bit_setting)
                GPIO.output(self.spi_sclk_pin, GPIO.LOW)
                time.sleep(self.min_period_sec / 2)
                if GPIO.input(self.spi_miso_pin):
                    result0 |= bitmask
                if GPIO.input(ADC_SDOB_Pin):
                    result1 |= bitmask
                GPIO.output(self.spi_sclk_pin, GPIO.HIGH)
                time.sleep(self.min_period_sec / 2)

                bitmask = bitmask >> 1
            print()

            result0buffer.append(result0)
            result1buffer.append(result1)
            print('   Receiving   0: ' + hex(result0) + '   1: ' + hex(result1))
            
        self.spi_idle()
        return result0buffer, result1buffer

