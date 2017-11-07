#import libraries
from itertools import ifilter 
import requests
import RPi.GPIO as GPIO
import time

class Colour():
    RED = 1
    YELLOW = 2
    BLUE = 3

# declare variables

# open weather map's endpoint
URL = "http://api.openweathermap.org/data/2.5/weather?q="
# the authorisation key
KEY = "&APPID=9caeab719c222439d4a2747fc6591523"
# an array of cities to cycle through, default is London
CITIES = ["London,uk", "New York,us", "Houston", "Miama,us", "Aberdeen,uk"]


# function that gets the raw weather data from the API
def getData(city):
    # sends the GET request to the URL (including the token) with the authorization header.
    rGet = requests.get(URL + city + KEY)
    return rGet


# gets the ID of the weather condition
def getWeatherID(city):
    weatherData = getData(city)  # calls getData to get raw weather data
    if ("weather" in (weatherData.json()) and
        "id" in (weatherData.json()["weather"][0])):
        # parses the JSON to obtain the ID
        return weatherData.json()["weather"][0]["id"]
    else:
        # error handling, in case the API does not return an ID
        return 0


# gets the main weather condition
def getWeatherMain(city):
    weatherData = getData(city)  # calls getData to get raw weather data
    if ("weather" in (weatherData.json()) and 
        "main" in (weatherData.json()["weather"][0])):
        # parses the JSON to obtain the main weather condition
        return weatherData.json()["weather"][0]["main"]
    else:
        # error handling, in case the API does not return a main weather condition
        return "none"


# gets the weather description
def getWeatherDescription(city):
    weatherData = getData(city)  # calls getData to get raw weather data
    if ("weather" in (weatherData.json()) and 
        "description" in (weatherData.json()["weather"][0])):
        # parses the JSON to obtain the weather description
        return weatherData.json()["weather"][0]["description"]
    else:
        # error handling, in case the API does not return a weather description
        return "none"


# gets the wind speed
def getWindSpeed(city):
    weatherData = getData(city)  # calls getData to get raw weather data
    if ("wind" in (weatherData.json()) and "speed" in (weatherData.json()["wind"])):  
        # parses the JSON to obtain the wind speed
        return weatherData.json()["wind"]["speed"]
    else:
        # error handling, in case the API does not return a wind speed
        return 0


# gets the wind direction (in degrees)
def getWindDirection(city):
    weatherData = getData(city)  # calls getData to get raw weather data
    if ("wind" in (weatherData.json()) and
        "deg" in (weatherData.json()["wind"])):
        # parses the JSON to obtain the wind direction
        return weatherData.json()["wind"]["deg"]
    else:
        # error handling, in case the API does not return a wind direction
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
def LEDColourForWeatherID(weatherID):

    rangesAndColours = [
        [[200,299], Colour.RED], 
        [[300,399], Colour.BLUE], 
        [[500,599], Colour.BLUE], 
        [[600,699], Colour.BLUE], 
        [[700,799], Colour.RED], 
        [[800,899], Colour.YELLOW], 
        [[900,906], Colour.RED], 
        [[951,956], Colour.YELLOW], 
        [[957,962], Colour.YELLOW]
    ]
    def within(rangeAndColour):
        r, c = rangeAndColour
        return (weatherID >= r[0] and weatherID <= r[1])

    v = next(ifilter(within, rangesAndColours), None)
    if (v == None):
        return Colour.BLUE
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
    #Cycles through 0..3, although there are 5 cities, so 0..4 correct!
    # (Maintaining previous behaviour pre-refactoring)
    return (pos + 1) % 4 

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
    return {
        Colour.YELLOW: 13, Colour.BLUE: 19, Colour.RED: 26
    }.get(colour, 19)

def main():
    cityPosition = 0  # initialises cityPosition to 0

    while (True):
        currentCity = CITIES[cityPosition]
        colour = LEDColour(currentCity)
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
            rotateTurntable(18, motorDirection(currentCity))
            printData(currentCity)  # outputs all the data
            LEDOn(num)
            cityPosition = nextCityPosition(cityPosition)
            # time.sleep(3)

    print("Program finished.")

if __name__ == "__main__":
    main()
