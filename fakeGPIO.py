BCM = 'bcm'
OUT = 'out'
IN = 'in'
PUD_UP = 'pud_up'


def setwarnings(b):
    return


def setmode(numbering):
    return


def setup(num, mode, pull_up_down=PUD_UP):
    return


def output(num, state):
    return


class FakePWM():
    def ChangeDutyCycle(self, duty):
        return


def PWM(a, b):
    return FakePWM()


def input(num):
    return True
