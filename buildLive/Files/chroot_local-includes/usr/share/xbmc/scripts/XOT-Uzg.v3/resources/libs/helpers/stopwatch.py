#===============================================================================
# LICENSE XOT-Framework - CC BY-NC-ND
#===============================================================================
# This work is licenced under the Creative Commons 
# Attribution-Non-Commercial-No Derivative Works 3.0 Unported License. To view a 
# copy of this licence, visit http://creativecommons.org/licenses/by-nc-nd/3.0/ 
# or send a letter to Creative Commons, 171 Second Street, Suite 300, 
# San Francisco, California 94105, USA.
#===============================================================================

import time

class StopWatch:
    def __init__(self, name, logger):
        if name == None or name == "" or logger == None:
            raise ValueError("Name or logger not specified")
        
        self.logger = logger
        self.name = name
        
        self.Set()        
        return
    
    def Stop(self):
        self.stopTime = time.time()
        secondsTaken = self.stopTime - self.startTime
        self.logger.debug("Stopwatch :: Stop (%s): %s ms", self.name, secondsTaken*1000)
        return
        
    def Set(self):
        self.startTime = time.time()
        self.logger.debug("Stopwatch :: Set (%s): %s", self.name, self.startTime)
        return
        
    def Lap(self):
        secondsTaken = time.time() - self.startTime
        self.logger.debug("Stopwatch :: Lap (%s): %s ms", self.name, secondsTaken*1000)
           
    def __str__(self):
        return self.name