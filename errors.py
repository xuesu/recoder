class InvalidParameterException(Exception):
    def __init__(self, name):
        self.name = name
        self.message = "{} is not a valid parameter!".format(name)
        super(InvalidParameterException, self).__init__()


class VolumeExceedException(Exception):
    def __init__(self):
        self.message = "Task Volume exceeds!"
        super(VolumeExceedException, self).__init__()


class GoldenExceedException(Exception):
    def __init__(self):
        self.message = "The Bank is empty!"
        super(GoldenExceedException, self).__init__()


class RequiredArgEmptyException(Exception):
    def __init__(self, name):
        self.message = "{} should not be None!".format(name)


class UnknownOpException(Exception):
    def __init__(self, name):
        self.message = "Unknown op {}!".format(name)
