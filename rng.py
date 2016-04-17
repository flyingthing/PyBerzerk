
# random number generator
class RNG(object):
    seed = 0

    @staticmethod
    def randomNumber(newseed):
        RNG.seed = (newseed * 7) + 0x3153
        return (RNG.seed >> 8) & 0xFF

    @staticmethod
    def getRandomNumber():
        return RNG.randomNumber(RNG.seed)