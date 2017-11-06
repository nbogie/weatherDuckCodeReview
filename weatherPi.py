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
def changeCities():
    global cityPosition
    if(cityPosition < 4):  # there are 5 cities to cycle through; if the current position is < 4 (so it is 0, 1, 2 or 3) simply increase it by 1
        cityPosition = cityPosition + 1
    else:  # otherwise, we have reached the end of the cycle and must begin again; therefore, set position to 0
        cityPosition = 0


# function to assign a direction (to move the motors in) based on the degree returned by the API
def motorDirection(city):
    deg = getWindDirection(city)

    # Gives angle for servo motor to turn the turntable the correct amount; ratio is 1:2+2/7
    direction = 0

    # gives ranges in degrees for each direction
    if (deg >= 0 and deg <= 45):
        direction = 0
    elif (deg >= 45 and deg <= 90):
        direction = 16.2
    elif (deg >= 90 and deg <= 135):
        direction = 32.4
    elif (deg >= 135 and deg <= 180):
        direction = 48.6
    elif (deg >= 180 and deg <= 225):
        direction = 64.8
    elif (deg >= 225 and deg <= 270):
        direction = 81
    elif (deg >= 270 and deg <= 315):
        direction = 97.2
    elif (deg >= 315 and deg < 360):
        direction = 113.4
    else:
        direction = 0

    print(direction)
    return(direction)


# rotates the turntable (connected to a servo motor)
def rotateTurntable(num, angle):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(num, GPIO.OUT)
    pwm = GPIO.PWM(18, 100)
    duty = float(angle) / 10.0 + 2.5
    pwm.ChangeDutyCycle(duty)


def runDuck():
    cityPosition = 0  # initialises cityPosition to 0

    num = 19  # sets "num" (the LED colour) to 19 (blue) for default

    while (True):
        # assigns the correct GPIO port for depending on the correct LED colour
        if (LEDColour(cities[cityPosition]) == 0):
            num = 13
        elif (LEDColour(cities[cityPosition]) == 1):
            num = 19
        elif (LEDColour(cities[cityPosition]) == 2):
            num = 26
        else:
            num = 19

        # waits for button to be pressed, then lights up the correct LED (as decided earlier)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        inputState = GPIO.input(17)
        if (inputState == False):
            LEDOff(13)  # resets all LEDs
            LEDOff(19)
            LEDOff(26)
            # turns the servo motor the correct number of degrees for that city's wind direction, as worked out in motorDirection()
            rotateTurntable(18, motorDirection(cities[cityPosition]))
            printData(cities[cityPosition])  # outputs all the data
            LEDOn(num)
            changeCities()
            # time.sleep(3)

    print("Program finished.")

runDuck()