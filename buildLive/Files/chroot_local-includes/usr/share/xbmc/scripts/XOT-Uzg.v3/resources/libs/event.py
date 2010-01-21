#===============================================================================
# LICENSE XOT-Framework - CC BY-NC-ND
#===============================================================================
# This work is licenced under the Creative Commons 
# Attribution-Non-Commercial-No Derivative Works 3.0 Unported License. To view a 
# copy of this licence, visit http://creativecommons.org/licenses/by-nc-nd/3.0/ 
# or send a letter to Creative Commons, 171 Second Street, Suite 300, 
# San Francisco, California 94105, USA.
#===============================================================================

class Event:
    def __init__(self):
        self.eventHandlers = set()

    # Adding EventHandlers
    def AddEventHandler(self, handler):
        self.eventHandlers.add(handler)
        return self

    # Removing EventHandlers
    def RemoveEventHandler(self, handler):
        try:
            self.eventHandlers.remove(handler)
        except:
            raise ValueError("This event is not handled by the eventhandler (handler).")
        return self
    
    # Trigger the eventhandlers with the supplied arguments
    def TriggerEvent(self, *args, **kargs):
        for handler in self.eventHandlers:
            handler(*args, **kargs)

    # get the number of registered eventhandlers
    def GetNumberOfRegisteredHandlers(self):
        return len(self.eventHandlers)

    # define the short-hand methods. Only these are needed for the rest of the code
    __iadd__ = AddEventHandler                  # for Event += EventHandler
    __isub__ = RemoveEventHandler               # for Event -= EventHandler
    __call__ = TriggerEvent                     # for triggering the Event
    __len__  = GetNumberOfRegisteredHandlers    # for len(Event)
