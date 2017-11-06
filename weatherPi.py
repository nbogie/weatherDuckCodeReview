#import libraries
from itertools import ifilter 
import requests
import RPi.GPIO as GPIO
import time

# declare variables

# open weather map's endpoint
URL = "http://api.openweathermap.org/data/2.5/weather?q="
# the authorisation key
KEY = "&APPID=9caeab719c222439d4a2747fc6591523"
# an array of cities to cycle through, default is London
cities = ["London,uk", "New York,us", "Houston", "Miama,us", "Aberdeen,uk"]


# function that gets the raw weather data from the API
def getData(city):
    # sends the GET request to the URL (including the token) with the authorization header.
    rGet = requests.get(URL + city + KEY)
    return rGet


# gets the ID of the weather condition
def getWeatherID(city):
    weatherData = getData(city)  # calls getData to get raw weather data
    if ("weather" in (weatherData.json())):  # error handling, in case the API does not return an ID
        if ("id" in (weatherData.json()["weather"][0])):
            # parses the JSON to obtain the ID
            weatherID = weatherData.json()["weather"][0]["id"]
            return weatherID
        else:
            return 000
    else:
        return 000


# gets the main weather condition
def getWeatherMain(city):
    weatherData = getData(city)  # calls getData to get raw weather data
    # error handling, in case the API does not return a main weather condition
    if ("weather" in (weatherData.json())):
        if ("main" in (weatherData.json()["weather"][0])):
            # parses the JSON to obtain the main weather condition
            weatherMain = weatherData.json()["weather"][0]["main"]
            return weatherMain
        else:
            return "none"
    else:
        return "none"


# gets the weather description
def getWeatherDescription(city):
    weatherData = getData(city)  # calls getData to get raw weather data
    # error handling, in case the API does not return a weather description
    if ("weather" in (weatherData.json())):
        if ("description" in (weatherData.json()["weather"][0])):
            # parses the JSON to obtain the weather description
            weatherDescription = weatherData.json(
            )["weather"][0]["description"]
            return weatherDescription
        else:
            return "none"
    else:
        return "none"


# gets the wind speed
def getWindSpeed(city):
    weatherData = getData(city)  # calls getData to get raw weather data
    if ("wind" in (weatherData.json())):  # error handling, in case the API does not return a wind speed
        if ("speed" in (weatherData.json()["wind"])):
            # parses the JSON to obtain the wind speed
            windSpeed = weatherData.json()["wind"]["speed"]
            return windSpeed
        else:
            return 0
    else:
        return 0


# gets the wind direction (in degrees)
def getWindDirection(city):
    weatherData = getData(city)  # calls getData to get raw weather data
    # error handling, in case the API does not return a wind direction
    if ("wind" in (weatherData.json())):
        if ("deg" in (weatherData.json()["wind"])):
            # parses the JSON to obtain the wind direction
            windDirection = weatherData.json()["wind"]["deg"]
            return windDirection
        else:
            return 0
    else:
        return 0


def printData(city):
    # prints the raw weather data, and each specific part of the data we isolated
    print("")  # blank lines just make the data easier to read
    print(getData(city).text)  # outputs the full raw data as JSON
    print("")
    print(city)
    print(getWeatherID(city))
    print(getWeatherMain(city))
    print(getWeatherDescription(city))
    print(getWindSpeed(city))
    print(getWindDirection(city))

    # prints the number for the LED colour
    print(LEDColour(city))
    print("")


# function to decide which colour LED to light up, depending on the type of weather in the response
def LEDColour(city):
    weatherID = getWeatherID(city)  # calls getData to get raw weather data
    return LEDColourForWeatherID(weatherID)


#Calc which colour of LED should light up for a given weather ID. 
# 0 is for yellow, 1 is for blue (default) and 2 is for red
def LEDColourForWeatherID(weatherID):

    rangesAndColours = [
        [[200,299], 2], 
        [[300,399], 1], 
        [[500,599], 1], 
        [[600,699], 1], 
        [[700,799], 2], 
        [[800,899], 0], 
        [[900,906], 2], 
        [[951,956], 0], 
        [[957,962], 0]
    ]
    def within(rangeAndColour):
        r, c = rangeAndColour
        return (weatherID >= r[0] and weatherID <= r[1])

    v = next(ifilter(within, rangesAndColours), None)
    if (v == None):
        return 1
    else:
        return v[1]

# function to turn an LED on. "num" is the exact GPIO port to use
def LEDOn(num):
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(num, GPIO.OUT)
    GPIO.output(num, True)


# function to turn an LED off. "num" is the exact GPIO port to use
def LEDOff(num):
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(num, GPIO.OUT)
    GPIO.output(num, False)


# function to change to the next city in the array (set up at the start of the program)
def nextCityPosition(pos):
    if(pos < 4):  # there are 5 cities to cycle through; if the current position is < 4 (so it is 0, 1, 2 or 3) simply increase it by 1
        return pos + 1
    else:  # otherwise, we have reached the end of the cycle and must begin again; therefore, set position to 0
        return 0


# function to assign a direction (to move the motors in) based on the degree returned by the API
def motorDirection(city):
    deg = getWindDirection(city)
    direction = motorDirectionForWindDirection(deg)
    print(direction)
    return(direction)


# Gives angle for servo motor to turn the turntable the correct amount; ratio is 1:2+2/7
def motorDirectionForWindDirection(deg):
    direction = 0

    # gives ranges in degrees for each direction
    limitsAndDirections = [
        [45, 0],
        [90, 16.2],
        [135, 32.4],
        [180, 48.6],
        [225,64.8],
        [270, 81],
        [315, 97.2],
        [359.9999, 113.4],
        [360, 0]
    ]
    if (deg < 0):
        return 0 # TODO: raise an exception here.

    val = next(ifilter(lambda pair: deg <= pair[0], limitsAndDirections), None)
    if (val == None):
        return 0
    else:
        return val[1]


# rotates the turntable (connected to a servo motor)
def rotateTurntable(num, angle):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(num, GPIO.OUT)
    pwm = GPIO.PWM(18, 100)
    duty = float(angle) / 10.0 + 2.5
    pwm.ChangeDutyCycle(duty)


# assigns the correct GPIO port for depending on the correct LED colour
#defaults to pin for blue if colour not found
def pinForLEDColour(colour):
    return {0: 13, 1: 19, 2: 26}.get(colour, 19)
    #TODO: throw exception if illegal colour

def runDuck():
    cityPosition = 0  # initialises cityPosition to 0

    while (True):
        colour = LEDColour(cities[cityPosition])
        num = pinForLEDColour(colour)

        # waits for button to be pressed, then lights up the correct LED (as decided earlier)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        buttonHigh = GPIO.input(17)
        if (not buttonHigh):
            LEDOff(13)  # resets all LEDs
            LEDOff(19)
            LEDOff(26)
            # turns the servo motor the correct number of degrees for that city's wind direction, as worked out in motorDirection()
            rotateTurntable(18, motorDirection(cities[cityPosition]))
            printData(cities[cityPosition])  # outputs all the data
            LEDOn(num)
            cityPosition = nextCityPosition(cityPosition)
            # time.sleep(3)

    print("Program finished.")

runDuck()
