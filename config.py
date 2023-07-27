class config:
    def __init__(self, configSettings):
        self.configSettings = configSettings
        # Yes, I am aware that I could just use the keys of properType to check... 
        self.properConfigHeaders = ['BotActive', 'BotColor', 'BlackTime', 'WhiteTime', 'StockfishLevel'] 
        self.properType = {'BotActive': True, 
                            'BotColor' : -1,
                            'BlackTime' : 1,
                            'WhiteTime': 1,
                            'StockfishLevel': 1
                        }
        self.properValue = {'BotColor' : [-1, 1],
                            'BlackTime' : 1,
                            'WhiteTime': 1,
                            'StockfishLevel': 1
                        }
        

    def checkConfig(self):
        if sorted(list(self.configSettings.keys())) != sorted(self.properConfigHeaders):
            self.throwErrorMesssage("Error: Missing config setting in config file")
            return False
        else:
            for i, e in enumerate(self.configSettings):
                if isinstance(self.configSettings[e], type(self.properType[e])) == False:
                    self.throwErrorMesssage(f'TypeError: Config setting of {e} has invalid type\nExpected {type(self.properType[e])}\nRecieved {type(self.configSettings[e])}')
                    return False
            for i, e in enumerate(self.properValue):
                content = self.properValue[e]
                if isinstance(content, type([])):
                    if self.configSettings[e] not in content:
                        self.throwErrorMesssage(f'ValueError: Config setting of {e} has improper value\nExpected {" or ".join([str(j) for j in content])}\nRecieved {self.configSettings[e]}')
                        return False
                elif self.configSettings[e] < content:
                    self.throwErrorMesssage(f'ValueError: Config setting of {e} has improper value\nExpected value greater than {content}\nRecieved {self.configSettings[e]}')
                    return False
        return True # Wow, somehow the end user was smart enough to figure out the config file!
    
    '''
    
    Yes, I am aware that this is a garbage way to throw error messages for end user.
    But I am way too lazy to care about it.
    This entire project already is garbage anyways.
    One of more piece of garbage won't matter.  
    Therefore, this will be the system in place until I change it to something else.

    '''
    def throwErrorMesssage(self, errorMessage):
        print(f'\033[91m{errorMessage}\033[0m')
        #return False
    
    def parseConfigs(self):
        configs = [self.configSettings[i] for i in self.properConfigHeaders]
        return configs