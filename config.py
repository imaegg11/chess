class config:
    def __init__(self, configSettings):
        self.configSettings = configSettings
        # Yes, I am aware that I could just use the keys of properType to check... 
        self.properConfigHeaders = ['BotActive', 'BotColor', 'BlackTime', 'WhiteTime', 'StockfishELO', 'AutoFlip', 'BlackTimeIncrement', 'WhiteTimeIncrement', 'Board'] 
        self.properConfigHeadersSet = set(self.properConfigHeaders)
        self.properType = {'BotActive': True, 
                            'AutoFlip': True,
                            'BotColor' : -1,
                            'BlackTime' : 1,
                            'WhiteTime': 1,
                            'StockfishELO': 1,
                            'BlackTimeIncrement': 0,
                            'WhiteTimeIncrement': 0, 
                            'Board': "I have no clue on how any of my code works ngl"
                        }
        self.properValue = {'BotColor' : [-1, 1],
                            'BlackTime' : 1,
                            'WhiteTime': 1,
                            'StockfishELO': 1,
                            'BlackTimeIncrement': 0,
                            'WhiteTimeIncrement': 0,
                            'Board': "I have no clue on how any of my code works ngl"
                        }
        

    def checkConfig(self):
        if sorted([i for i in list(self.configSettings.keys()) if i in self.properConfigHeadersSet]) != sorted(self.properConfigHeaders):
            missingConfigs = [i for i in self.properConfigHeaders if i not in self.configSettings.keys()]
            self.throwErrorMesssage("Error: Missing config" + ("s" if len(missingConfigs) > 1 else "") + " - Could not find following config" + ("s:" if len(missingConfigs) > 1 else ":"))
            for i in missingConfigs:
                self.throwErrorMesssage("       " + i)
            return False
        else:
            for i, e in enumerate(self.configSettings):
                if e not in self.properConfigHeadersSet:
                    continue
                if isinstance(self.configSettings[e], type(self.properType[e])) == False:
                    self.throwErrorMesssage(f'TypeError: Config setting of {e} has invalid type\nExpected {type(self.properType[e])}\nRecieved {type(self.configSettings[e])}')
                    return False
            for i, e in enumerate(self.properValue):
                if e not in self.properConfigHeadersSet:
                    continue
                content = self.properValue[e]
                if isinstance(content, type([])):
                    if self.configSettings[e] not in content:
                        self.throwErrorMesssage(f'ValueError: Config setting of {e} has improper value\nExpected {" or ".join([str(j) for j in content])}\nRecieved {self.configSettings[e]}')
                        return False
                elif self.configSettings[e] < content:
                    self.throwErrorMesssage(f'ValueError: Config setting of {e} has improper value\nExpected value greater than or equal to {content}\nRecieved {self.configSettings[e]}')
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