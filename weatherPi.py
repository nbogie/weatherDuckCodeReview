#import libraries
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
    rGet = requests.get(URL + city + KEY)  # sends the GET request to the URL (including the token) with the authorization header.
    return rGet


# gets the ID of the weather condition
def getWeatherID(city):
    weatherData = getData(city)  # calls getData to get raw weather data
    if ("weather" in (weatherData.json())):  # error handling, in case the API does not return an ID
        if ("id" in (weatherData.json()["weather"][0])):
            weatherID = weatherData.json()["weather"][0]["id"]  # parses the JSON to obtain the ID
            return weatherID
        else:
            return 000
    else:
        return 000


# gets the main weather condition
def getWeatherMain(city):
    weatherData = getData(city)  # calls getData to get raw weather data
    if ("weather" in (weatherData.json())):  # error handling, in case the API does not return a main weather condition
        if ("main" in (weatherData.json()["weather"][0])):
            weatherMain = weatherData.json()["weather"][0]["main"]  # parses the JSON to obtain the main weather condition
            return weatherMain
        else:
            return "none"
    else:
        return "none"


# gets the weather description
def getWeatherDescription(city):
    weatherData = getData(city)  # calls getData to get raw weather data
    if ("weather" in (weatherData.json())):  # error handling, in case the API does not return a weather description
        if ("description" in (weatherData.json()["weather"][0])):
            weatherDescription = weatherData.json()["weather"][0]["description"]  # parses the JSON to obtain the weather description
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
            windSpeed = weatherData.json()["wind"]["speed"]  # parses the JSON to obtain the wind speed
            return windSpeed
        else:
            return 0
    else:
        return 0


# gets the wind direction (in degrees)
def getWindDirection(city):
    weatherData = getData(city)  # calls getData to get raw weather data
    if ("wind" in (weatherData.json())):  # error handling, in case the API does not return a wind direction
        if ("deg" in (weatherData.json()["wind"])):
            windDirection = weatherData.json()["wind"]["deg"]  # parses the JSON to obtain the wind direction
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
    colour = 1  # variable to store which colour of LED should light up. 0 is for yellow, 1 is for blue (default) and 2 is for red

    # goes through all possible weather IDs, and assigns an LED colour for each
    if (weatherID >= 200 and weatherID < 300):
        colour = 2
    elif (weatherID >= 300 and weatherID < 400):
        colour = 1
    elif (weatherID >= 500 and weatherID < 600):
        colour = 1
    elif (weatherID >= 600 and weatherID < 700):
        colour = 1
    elif (weatherID >= 700 and weatherID < 800):
        colour = 2
    elif (weatherID >= 800 and weatherID < 900):
        colour = 0
    elif (weatherID >= 900 and weatherID <= 906):
        colour = 2
    elif (weatherID >= 951 and weatherID <= 956):
        colour = 0
    elif (weatherID >= 957 and weatherID <= 962):
        colour = 0
    else:
        colour = 1

    return colour


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
        cityPosition = 0;


# function to assign a direction (to move the motors in) based on the degree returned by the API
def motorDirection(city):
    deg = getWindDirection(city)
    global direction  # Gives angle for servo motor to turn the turntable the correct amount; ratio is 1:2+2/7
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
        rotateTurntable(18, motorDirection(cities[cityPosition]))  # turns the servo motor the correct number of degrees for that city's wind direction, as worked out in motorDirection()
        printData(cities[cityPosition])  # outputs all the data
        LEDOn(num)
        changeCities()
        # time.sleep(3)

print("Program finished.")
