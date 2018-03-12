import binascii
from pycom import nvs_set, nvs_get
# Need to make a few changes on the memory limits 
class NvsStore():
#   this class basically stores the string and topic provided in the nvram
#    given the fact that the string sizes can be variable. Using a variety of
#    functions to convert string in to int and int back to string we use this
#    class to store a topic and string in a series of nvram cells

    def __init__(self, topic, stringToStore):

        self.string = stringToStore
        self.topic = topic
        self.__Init(self.string, self.topic)

    def __Init(self, string, topic):
        # step 1: split string into a list of strings each of maximum 4 chars
        # step 2: store the topic and string in the nvram cell and use str2int
        #         to shift each list componenent into nvram
        self.strSplit(string)
        self.store(topic)

    def str2int(self, string):
        x = binascii.hexlify(string)
        x = int(x, 16)
        x = x + 0x200
        return x

    def store(self, topic):
        # store list values into nvram topic spaces
        for i in range(len(self.strlist)):
            nvs_set(topic+str(i), self.str2int(self.strlist[i]))

    def strSplit(self, string):
        # split string into 4 chars each and put it in a list
        self.strlist = []
        temp = string
        while temp != "":
            if len(temp) < 4 or len(temp) == 4:
                self.strlist.append(temp)
                break
            self.strlist.append(temp[len(temp)-4:len(temp)])
            temp = temp[:len(temp)-4]

    def intcount(self, val):
        # old function used for debugging
        y = val
        i = 0
        while int(y/10) != 0:
            y = y / 10
            i+=1
        return i


class NvsExtract():
#   This class will be used to extract and return string values back to
#   pycom for their use in lora, wifi, LTE services. The topic keys are
#   constant hence we can find the strings yet we need to use try/except
#   to catch error for finding limit of a certain topic string

    def __init__(self, topic):
        self.topic = topic
        self.__Init(self.topic)

    def __Init(self, topic):
        self.extractInt(topic)

    def extractInt(self, topic):
        # extract integer from nvram topic and put string in self.string
        cnt = 0
        self.string = ""
        x = []
        while True:
            if nvs_get(topic+str(cnt)) == None:
                break
            else:
                x.append(self.int2str(nvs_get(topic+str(cnt))).decode("utf-8"))
                cnt += 1
        while len(x) > 0:
            self.string = self.string + x[len(x) -1]
            x = x[:len(x)-1]
        temp = self.string

    def retval(self):
        return self.string

    def int2str(self, integer):
        # convert integer obtained into character string
        integer = integer - 0x200
        integer = hex(integer)
        return binascii.unhexlify(integer[2:])

test = False
if test == True:
    NvsStore("ssid", "one")
    NvsExtract("ssid")
