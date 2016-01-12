from threading import Thread
from threading import Event
import time
import spi

class HotTubAPI:
    def __init__(self):
        # Mode 0, default speed
        spi.openSPI()
        
        self.temperature = 0
        self.pump_led = 0
        self.heater_led = 0
        self.heat_led = 0
        self.light_led = 0
        self.temp_led = 0
        self.temperature_led = 0
        self.curTemp = 0
        self.setPoint = 0
        self.clients = {}
        self.MAX_TEMP = 40
        self.COOL_TEMP = 30
        
        # Setup the threading callback
        self.refreshThreadStop = Event()
        self.refreshThread = Thread(target = self.refreshThread, args=(self.refreshThreadStop,))
        self.refreshThread.start()

    def registerClient(self, object, callback):
        self.clients[object] = callback
        
    def deregisterClient(self, object):
        if object in self.clients:
            del self.clients[object]
            
    def refreshThread(self, stop_event):
        while(not stop_event.is_set()):
            time.sleep(0.250)
            self.refresh()
        stop_event.clear()
    
    def doRefresh(self):
        self.refresh(doRefresh=True)
        
    # For Text Part
    def getCurTemp(self):
        if self.curTemp == 0:
            # Wait 10 seconds for refresh
            for i in xrange(20):
                time.sleep(0.5)
                if self.curTemp != 0:
                    break
        return self.curTemp
    
    # Set Point
    def getSetPoint(self):
        if self.setPoint == 0:
            for i in xrange(20):
                self.pressTempUpButton()
                time.sleep(0.150) # 150 ms
                self.pressTempDownButton()
                # Hang out
                time.sleep(0.5)
                print "Tried to get set point"
                if self.setPoint != 0:
                    break
        
        return self.setPoint
    
    # Heat up, return when setPoint is at correct temperature
    def heatUp(self):
        self.getSetPoint()
        while(self.getSetPoint() < self.MAX_TEMP):
            self.pressTempUpButton()
            time.sleep(0.5) # Wait half second
            
    def coolDown(self):
        while(self.getSetPoint() > self.COOL_TEMP):
            self.pressTempDownButton()
            time.sleep(0.5)
        
    # Time to heat up from curTemp to setPoint
    def estimateDelay(self):
        if self.curTemp < self.setPoint:
            # Assume linear for 10 degree gradient, this will get better
            return 120 * (self.setPoint-self.curTemp) / (10)
    
    def refresh(self, doRefresh=False):
        temp = self.getTemperature()
        status = self.getStatus()
        pump_led = status & 0x01
        heater_led = (status >> 2) & 0x01
        heat_led = (status >> 3) & 0x01
        light_led = (status >> 1) & 0x01
        temp_led = (status >> 4) & 0x01
        if temp_led:
            setPoint = temp
            if self.setPoint != setPoint and setPoint != 0:
                self.setPoint = setPoint
        else:
            curTemp = temp
            if self.curTemp != curTemp and curTemp != 0:
                self.curTemp = curTemp
                
        if self.pump_led != pump_led:
            self.pump_led = pump_led
            doRefresh = True
            
        if self.heater_led != heater_led:
            self.heater_led = heater_led
            doRefresh = True
            
        if self.heat_led != heat_led:
            self.heat_led = heat_led
            doRefresh = True
            
        if self.light_led != light_led:
            self.light_led = light_led
            doRefresh = True
        
        if self.temp_led != temp_led:
            self.temp_led = temp_led
            doRefresh = True
        
        # display temperature
        if self.temperature != temp and temp != 0:
            self.temperature = temp
            doRefresh = True
       
        # Only actually do the GUI refresh if necessary
        if doRefresh:
            print "Refresh"
            self.__updateLedCallbacks()
    
    def __updateLedCallbacks(self):
        for callback in self.clients.values():
            callback('updateLeds', dict(
                temperature=self.temperature,
                pump_led=self.pump_led,
                heater_led=self.heater_led,
                heat_led=self.heat_led,
                light_led=self.light_led,
                temp_led=self.temp_led
            ))

    def pressLightButton(self):
        spi.transfer((0x14,))
    
    def pressPumpButton(self):
        print "Pump Button Pressed"
        spi.transfer((0x13,))
    
    def pressTempUpButton(self):
        print "Temp Up Button Pressed"
        spi.transfer((0x11,))
    
    def pressTempDownButton(self):
        print "Temp Down Button Pressed"
        spi.transfer((0x12,))
        
    def getTemperature(self):
        spi.transfer((0x22,))
        time.sleep(0.001) # 1ms
        return spi.transfer((0x00,))[0] # Null
        
    def getStatus(self):
        spi.transfer((0x23,))
        time.sleep(0.001) # 1ms
        return spi.transfer((0x00,))[0]
        
    def getControl(self):
        spi.transfer((0x21,))
        time.sleep(0.001) # 1ms
        return spi.transfer((0x00,))[0]
        
    def close(self):
        self.refreshThreadStop.set()
        # Wait for thread to stop
        while(self.refreshThreadStop.is_set()):
            pass
        spi.closeSPI()