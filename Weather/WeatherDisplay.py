import requests, json
import time
from rpi_ws281x import *
import argparse
from csv import DictReader
import numpy as np
import random
from multiprocessing import Process
import _thread

##################################################################################################################
# Service Class
#-----------------------------------------------------------------------------------------------------------------
class Service:
    def __init__(self):
        self.arrayOfLeds = np.zeros(shape=(100,3), dtype=int)
        self.ledAxis = 0
        self.xAxis = 1
        self.yAxis = 2
        with open('coordinates.csv', 'r') as read_obj:
            csv_dict_reader = DictReader(read_obj)
            for row in csv_dict_reader:
                self.arrayOfLeds[int(row['Led Number'])] = self.loadDataSet(self.arrayOfLeds, row['Led Number'], row['Front Profile'])

    def loadDataSet(self, dataSet,ledNumber, entry):
        passedComma = False
        x = ''
        y = ''
        for element in range(1, len(entry) - 1):
            #print(entry[element]
            if(entry[element]  is ',' or entry[element]  is ' '):
                passedComma = True
            else: 
                if(passedComma == False):
                    x = x + entry[element]
                else:
                    y = y + entry[element]
        temp = [int(ledNumber), int(x), int(y)]
        #print(temp)
        return temp

    def getLedList(self, sortedList):
        ledList = sortedList[:, self.ledAxis]
        return ledList
    def getXList(self, sortedList):
        xList = sortedList[:, self.xAxis]
        return xList
    def getYList(self, sortedList):
        yList = sortedList[:, self.yAxis]
        return yList

    def sortByLed(self):
        sortedList = self.arrayOfLeds[np.argsort(self.arrayOfLeds[:, self.ledAxis])]
        return sortedList
    def sortByX(self):
        sortedList = self.arrayOfLeds[np.argsort(self.arrayOfLeds[:, self.xAxis])]
        return sortedList
    def sortByY(self):
        sortedList = self.arrayOfLeds[np.argsort(self.arrayOfLeds[:, self.yAxis])]
        return sortedList

    def randomNumber(self, bottom, top, interval):
        return random.randrange(bottom, top, interval)
##################################################################################################################
# Open Weather API Class
#-----------------------------------------------------------------------------------------------------------------
class Weather:
    #------------------------------------------------------------------------------------------- Global Parameters
    # TODO - remove key before commiting to a public repo
    api_key = "302e70e118f7ec149428d51ce6fa7459"
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    #------------------------------------------------------------------------------------------- Call Paramters
    units = "imperial"

    def __init__(self, city_name):
        self.city_name = city_name
        self.url = self.base_url + "appid=" + self.api_key + "&q=" + self.city_name + "&units=" + self.units

    def getWeatherData(self):
        response = requests.get(self.url)
        response_json = response.json()

        if response_json["cod"] != "404":
            #Main Body
            main = response_json["main"]

            #Weather Body
            self.weather = response_json["weather"]
            self.weather_id = self.weather[0]["id"]
            self.weather_main = self.weather[0]["main"]
            self.weather_description = self.weather[0]["description"]

            #Print Values
            print("\n - WEATHER DATA ------------------" +
                    "\n      Main Weather = " +
                            str(self.weather_main) +
                    "\n      Weather Description = " +
                            str(self.weather_description) +
                    "\n      Corresponding ID = " +
                            str(self.weather_id)+ "\n")

        elif response_json["cod"] != "401":
            print("Key error")

        else:
            print(" City Not Found ")

##################################################################################################################
# Color Class
#-----------------------------------------------------------------------------------------------------------------
class RGB:
    def __init__(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue
        self.color = Color(self.green, self.red, self.blue)

    def convert(self, red, green, blue):
        return Color(green, red, blue)

##################################################################################################################
# LED Light Class
#-----------------------------------------------------------------------------------------------------------------
class Lights:
    def __init__(self,
                    LED_COUNT,
                    LED_PIN = 18,
                    LED_FREQ_HZ = 800000,
                    LED_DMA = 10,
                    LED_INVERT = False,
                    LED_BRIGHTNESS = 255,
                    LED_CHANNEL = 0):
        self.LED_COUNT = LED_COUNT
        self.strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        self.strip.begin()

    def clear(self):
        self.colorWipe(RGB(0,0,0).color, 10)

    def fill(self, color):
        for i in range(self.LED_COUNT):
            self.strip.setPixelColor(i, color)
        self.strip.show()

    def spotFill(self, color, maxNumLeds):
        service = Service()
        spotStart = service.randomNumber(0, 100, 1)       #Where on the line it starts
        length = service.randomNumber(0, maxNumLeds, 1)   #How many light can light up
        for i in range(length):
            self.strip.setPixelColor(spotStart + i, color)
        self.strip.show()

    def fadeIn(self, rgb, leds, pulseAmount, wait_ms=0):
        startingRed = rgb.red - pulseAmount
        startingGreen = rgb.green - pulseAmount
        startingBlue = rgb.blue - pulseAmount
        # Pulse in...
        for i in range(0, pulseAmount, 1):
            if startingRed < 0:
                displayRed = 0
            else:
                displayRed = startingRed
            if startingGreen < 0:
                displayGreen = 0
            else:
                displayGreen = startingGreen
            if startingBlue < 0:
                displayBlue = 0
            else:
                displayBlue = startingBlue

            #Printing block to show what values are being sent to the leds
            # print(displayRed)
            # print(displayGreen)
            # print(displayBlue)
            for x in leds:
                self.strip.setPixelColor(int(x), RGB(displayRed, displayGreen, displayBlue).color)
            self.strip.show()

            startingRed += 1
            startingGreen += 1
            startingBlue += 1
        time.sleep(wait_ms/1000)
    def fadeOut(self, rgb, leds, pulseAmount, wait_ms=0):
        startingRed = rgb.red
        startingGreen = rgb.green
        startingBlue = rgb.blue
        # Pulse out...
        for i in range(pulseAmount, 0, -1):
            if startingRed < 0:
                displayRed = 0
            else:
                displayRed = startingRed
            if startingGreen < 0:
                displayGreen = 0
            else:
                displayGreen = startingGreen
            if startingBlue < 0:
                displayBlue = 0
            else:
                displayBlue = startingBlue

            #Printing block to show what values are being sent to the leds
            # print(displayRed)
            # print(displayGreen)
            # print(displayBlue)

            for x in leds:
                self.strip.setPixelColor(int(x), RGB(displayRed, displayGreen, displayBlue).color)
            self.strip.show()

            startingRed -= 1
            startingGreen -= 1
            startingBlue -= 1
        time.sleep(wait_ms/1000)

    def pulse(self, rgb, firstLed, lastled, wait_ms=25):
        for i in range(150, 255, 1):
            for x in range(firstLed, lastled):
                self.strip.setPixelColor(x, RGB(i - 10, i - 60, 0).color)
            self.strip.show()
            time.sleep(wait_ms/1000)
        for i in range(255, 150, -1):
            for x in range(firstLed, lastled):
                self.strip.setPixelColor(x, RGB(i - 10, i - 60, 0).color)
            self.strip.show()
            time.sleep(wait_ms/1000)

    def smartPulse(self, rgb, leds, pulseAmount, wait_ms=0):
        startingRed = rgb.red - pulseAmount
        startingGreen = rgb.green - pulseAmount
        startingBlue = rgb.blue - pulseAmount

        # Pulse in...
        for i in range(0, pulseAmount, 1):
            if startingRed < 0:
                displayRed = 0
            else:
                displayRed = startingRed
            if startingGreen < 0:
                displayGreen = 0
            else:
                displayGreen = startingGreen
            if startingBlue < 0:
                displayBlue = 0
            else:
                displayBlue = startingBlue

            #Printing block to show what values are being sent to the leds
            # print(displayRed)
            # print(displayGreen)
            # print(displayBlue)
            for x in leds:
                self.strip.setPixelColor(int(x), RGB(displayRed, displayGreen, displayBlue).color)
            self.strip.show()

            startingRed += 1
            startingGreen += 1
            startingBlue += 1
        time.sleep(wait_ms/1000)

        # Pulse out...
        for i in range(pulseAmount, 0, -1):
            if startingRed < 0:
                displayRed = 0
            else:
                displayRed = startingRed
            if startingGreen < 0:
                displayGreen = 0
            else:
                displayGreen = startingGreen
            if startingBlue < 0:
                displayBlue = 0
            else:
                displayBlue = startingBlue

            #Printing block to show what values are being sent to the leds
            # print(displayRed)
            # print(displayGreen)
            # print(displayBlue)

            for x in leds:
                self.strip.setPixelColor(int(x), RGB(displayRed, displayGreen, displayBlue).color)
            self.strip.show()

            startingRed -= 1
            startingGreen -= 1
            startingBlue -= 1
        time.sleep(wait_ms/1000)

    def colorWipe(self, color, wait_ms=50):
        """Wipe color across display a pixel at a time."""
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color)
            self.strip.show()
            time.sleep(wait_ms/1000.0)

    def sectionWipe(self, color, maxNumLeds):
        """Wipe color across display a pixel at a time."""
        spotStart = service.randomNumber(0, 100, 1)      #Where on the line it starts
        length = service.randomNumber(0, maxNumLeds, 1)  #How many light can light up`
        for i in range(length):
            self.strip.setPixelColor(spotStart + i, color)
            self.strip.show()
            time.sleep(.001)

    # Pulse single led wihtin range at a given interval
    def precipitationAnimation(self, rgb, leds, pulseAmount=200):
        subset = []

        #Find random number to determine how many droplets will be displayed at once
        dropslets = service.randomNumber(0, len(leds), 1)

        #Create new array of random elements from the passed in leds array
        for i in range(dropslets):
            subset.append(random.choice(leds))

        #Pulse the subset of leds to simulate precipitation
        self.smartPulse(rgb, subset, pulseAmount)

        #Wait a random amount of time after the animation to create some randomness between the effects
        wait = service.randomNumber(0, 500, 1)
        time.sleep(wait/1000)

    # Pulse group of leds wihtin range at a given interval
    def cloudAnimation(self, rgb, leds, wait_ms=50):
        for i in range(rgb.blue - 50, rgb.blue, 1):
            for x in leds:
                self.strip.setPixelColor(int(x), RGB(i ,i ,i).color)
            self.strip.show()
            time.sleep(wait_ms/1000)
        for i in range(rgb.blue, rgb.blue - 50, -1):
            for x in leds:
                self.strip.setPixelColor(int(x), RGB(i, i, i).color)
            self.strip.show()
            time.sleep(wait_ms/1000)

#----------------------------------------------------------------------------------------------- Weather Effects -
    def thunderStorm(self):
        service = Service()
        #Thunder represented as all lights flashing a bit lighter
        amountOfThunder = service.randomNumber(1, 6, 1)
        time.sleep(5)
        for x in range(amountOfThunder):
            self.spotFill(RGB(255, 255, 255).color, 15)
            time.sleep(.15)
            self.fill(RGB(38, 16, 99).color)
            wait = service.randomNumber(1, 10, 1)
            time.sleep(wait/20)
        #Lightning will be a random number of leds in a row lighting up in sequence
        amountOfLightning = service.randomNumber(0, 3, 1)
        for i in range(amountOfLightning):
            self.sectionWipe(RGB(255, 255, 255).color, 30)
            time.sleep(.1)
            self.fill(RGB(38, 16, 99).color)
            wait = service.randomNumber(1, 10, 1)
            time.sleep(wait/20)

    def snow(self, service):
        sortedList = service.sortByY()
        yValues = service.getYList(sortedList)
        ledValues = service.getLedList(sortedList)
        cloudLayer = []
        cloudColor = RGB(110, 110, 110)
        snowLayer = []
        snowColor = RGB(230, 230, 230)
        # Assign sections for different animations ie cloud layer and rain layer
        for x in yValues:
            if x < 135:
                for k in ledValues[np.where(yValues == x)]:
                    if k not in cloudLayer:
                        cloudLayer.append(k)
            else:
                for k in ledValues[np.where(yValues == x)]:
                    if k not in snowLayer:
                        snowLayer.append(k)
        #_thread.start_new_thread(self.precipitationAnimation, (snowColor, snowLayer, 10))
        # _thread.start_new_thread(self.cloudAnimation, (cloudColor, cloudLayer, 10))

        #Temp code until I figure out multithreading
        for x in cloudLayer:
            self.strip.setPixelColor(int(x), cloudColor.color)
        self.strip.show()
        self.precipitationAnimation(snowColor, snowLayer, 255)
        # self.cloudAnimation(cloudColor, cloudLayer, 10)

    def rain(self, service):
        sortedList = service.sortByY()
        yValues = service.getYList(sortedList)
        ledValues = service.getLedList(sortedList)
        cloudLayer = []
        cloudColor = RGB(110, 110, 110)
        rainLayer = []
        rainColor = RGB(0, 182, 255)
        # Assign sections for different animations ie cloud layer and rain layer
        for x in yValues:
            if x < 135:
                for k in ledValues[np.where(yValues == x)]:
                    if k not in cloudLayer:
                        cloudLayer.append(k)
            else:
                for k in ledValues[np.where(yValues == x)]:
                    if k not in rainLayer:
                        rainLayer.append(k)
        #_thread.start_new_thread(self.precipitationAnimation, (rainColor, rainLayer, 10))
        # _thread.start_new_thread(self.cloudAnimation, (cloudColor, cloudLayer, 10))

        #Temp code until I figure out multithreading
        for x in cloudLayer:
            self.strip.setPixelColor(int(x), cloudColor.color)
        self.strip.show()
        self.precipitationAnimation(rainColor, rainLayer)
        # self.cloudAnimation(cloudColor, cloudLayer, 10)

    def sunny(self, service):
        leds = service.getLedList(service.arrayOfLeds)
        sunnyColor = RGB(255, 234, 0)
        secondarySun = RGB(244, 224, 20)
        #secondarySun = RGB(255, 200, 0)

        self.precipitationAnimation(sunnyColor, leds, 100)

        #self.fill(sunnyColor.color)
        #self.fadeIn(secondarySun, leds, 100)

    def partlyCloudy(self):
        rgb = RGB(255, 255, 255)
    
    def cloudy(self):
        rgb = RGB(255, 255, 255)

##################################################################################################################
# Main Code
#-----------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    #------------------------------------------------------------------------------------------- Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    print ('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    #------------------------------------------------------------------------------------------- initialize Service Class
    service = Service()
    #------------------------------------------------------------------------------------------- initialize LED Strip
    lights = Lights(100)
    #------------------------------------------------------------------------------------------- Get Weather Data
    weather = Weather("Cleveland")
    weather.getWeatherData()
    print(weather.weather_main)

    try:
        #Initialize color for following animation
        #------------------------------------------------------------------------------------------- Thunderstorm
        if weather.weather_main == "Thunderstorm":
            lights.fadeIn(RGB(38, 16, 99), service.getLedList(service.arrayOfLeds), 250)
        #------------------------------------------------------------------------------------------- Drizzle
        elif weather.weather_main == "Drizzle":
            lights.fadeIn(RGB(110, 110, 110), service.getLedList(service.arrayOfLeds), 250)
        #------------------------------------------------------------------------------------------- Rain
        elif weather.weather_main == "Rain":
            lights.fadeIn(RGB(110, 110, 110), service.getLedList(service.arrayOfLeds), 250)
        #------------------------------------------------------------------------------------------- Snow
        elif weather.weather_main == "Snow":
            lights.fadeIn(RGB(110, 110, 110), service.getLedList(service.arrayOfLeds), 250)
        #------------------------------------------------------------------------------------------- Atmosphere
        elif weather.weather_main == "Atmosphere":
            lights.fadeIn(RGB(255, 234, 0), service.getLedList(service.arrayOfLeds), 250)
        #------------------------------------------------------------------------------------------- Clear
        elif weather.weather_main == "Clear":
            lights.fadeIn(RGB(155, 134, 0), service.getLedList(service.arrayOfLeds), 250)
        #------------------------------------------------------------------------------------------- Clouds
        elif weather.weather_main == "Clouds":
            lights.fadeIn(RGB(110, 110, 110), service.getLedList(service.arrayOfLeds), 250)
        #------------------------------------------------------------------------------------------- Fail Safe
        else:
            lights.fadeIn(RGB(255, 234, 0), service.getLedList(service.arrayOfLeds), 250)
        while True:
            #------------------------------------------------------------------------------------------- Thunderstorm
            if weather.weather_main == "Thunderstorm":
                lights.thunderStorm()
            #------------------------------------------------------------------------------------------- Drizzle
            elif weather.weather_main == "Drizzle":
                lights.rain(service)
            #------------------------------------------------------------------------------------------- Rain
            elif weather.weather_main == "Rain":
                lights.rain(service)
            #------------------------------------------------------------------------------------------- Snow
            elif weather.weather_main == "Snow":
                lights.snow(service)
            #------------------------------------------------------------------------------------------- Atmosphere
            elif weather.weather_main == "Atmosphere":
                lights.snow(service)
            #------------------------------------------------------------------------------------------- Clear
            elif weather.weather_main == "Clear":
                lights.sunny(service)
            #------------------------------------------------------------------------------------------- Clouds
            elif weather.weather_main == "Clouds":
                lights.rain(service)
            #------------------------------------------------------------------------------------------- Fail Safe
            else:
                lights.sunny(service)
    except KeyboardInterrupt:
        if args.clear:
            lights.clear()