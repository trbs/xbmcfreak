#===============================================================================
# LICENSE XOT-Framework - CC BY-NC-ND
#===============================================================================
# This work is licenced under the Creative Commons 
# Attribution-Non-Commercial-No Derivative Works 3.0 Unported License. To view a 
# copy of this licence, visit http://creativecommons.org/licenses/by-nc-nd/3.0/ 
# or send a letter to Creative Commons, 171 Second Street, Suite 300, 
# San Francisco, California 94105, USA.
#===============================================================================

import os, sys
import time, string, re 
import traceback, inspect, datetime

#===============================================================================
# Define levels (same as Python's loglevels)
#===============================================================================
CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0
#===============================================================================
# Custom Logger
#===============================================================================
class Customlogger:
    def __init__(self, logFileName, minLogLevel, logDual, append=False):
        """
        Log Holder class to make it appear as a default Python logger. Has
        a subclass Write that does the work!
        """
        self.logFileName = logFileName
        self.fileMode = "a"
        self.fileFlags = os.O_WRONLY|os.O_APPEND|os.O_CREAT
        
        self.minLogLevel = minLogLevel
        self.logDual = logDual
        self.logEntryCount = 0
        self.flushInterval = 5
        #self.logHandle = -1
        
        self.logLevelNames = {
            CRITICAL : 'CRITICAL',
            ERROR : 'ERROR',
            WARNING : 'WARNING',
            INFO : 'INFO',
            DEBUG : 'DEBUG',
            NOTSET : 'NOTSET',
            'CRITICAL' : CRITICAL,
            'ERROR' : ERROR,
            'WARN' : WARNING,
            'WARNING' : WARNING,
            'INFO' : INFO,
            'DEBUG' : DEBUG,
            'NOTSET' : NOTSET,
        }
        
        if not append:
            self.CleanUpLog()
            
        # now open the file
        self.OpenLog()
    
    #============================================================================== 
    def OpenLog(self):
        """
        Creates a filedescriptor and then a filehandle
        """
        self.fileDescriptor = os.open(self.logFileName, self.fileFlags)
        self.logHandle = os.fdopen(self.fileDescriptor, self.fileMode)
    
    def CloseLog(self):
        """
        Close the logfile. Calling close() on a filehandle also 
        closes the FileDescriptor
        """
        self.logHandle.close()
        
    #============================================================================== 
    def FindCaller(self):
        """
        Find the stack frame of the caller so that we can note the source
        file name, line number and function name.
        """
        returnValue = ("Unknown", 0)
        
        # get the current frame and descent down until the correct one is found
        currentFrame = sys._getframe(3) # could be _getframe(#) with # from () to (3)
        while hasattr(currentFrame, "f_code"):
            co = currentFrame.f_code
            sourceFile = os.path.normcase(co.co_filename)
            # if currentFrame belongs to this logger.py or equals <string> continue
            if sourceFile == "<string>" or sourceFile == os.path.normcase(__file__):
                currentFrame = currentFrame.f_back
                continue
            else:
                # get the sourcePath and sourceFile
                (sourcePath, sourceFile) = os.path.split(sourceFile)
                returnValue = (sourceFile, currentFrame.f_lineno)       
                break

        return returnValue
    
    #==============================================================================     
    def CleanUpLog(self):
        #create old.log file
        try:
            wasOpen = True
            self.CloseLog()
        except:
            wasOpen = False
            
        _oldFileName = string.replace(self.logFileName, ".log", ".old.log")
        if os.path.exists(self.logFileName):
            if os.path.exists(_oldFileName):
                os.remove(_oldFileName)
            os.rename(self.logFileName, _oldFileName)
            
        if wasOpen:
            self.OpenLog()
        return            
            
    #============================================================================== 
    def Write(self, msg, *args, **kwargs):
        try:
            self.logFormat = '%s - %-8s - %-16s - %-3d - %s\n'
            self.timeFormat = "%Y%m%d %H:%M:%S"
            self.logLevel = kwargs["level"]
            #determine if write is needed:
            if self.logLevel < self.minLogLevel:
                return
            
            # convert possible tupple to string:
            msg = str(msg)
            
            # Fill the message with it's content
            if len(args)>0:
                #print "# of args: %s" % (len(args[0]))
                _msg = msg % args
            else:
                _msg = msg
                
            # get frame information
            (_sourceFile, _sourceLineNumber) = self.FindCaller()
            
            # get time information
            _datetime = datetime.datetime.today().strftime(self.timeFormat)
            
            # check for exception info, if present, add to end of string:
            if kwargs.has_key("exc_info"):
                if self.logDual:
                    traceback.print_exc()
                _msg = "%s\n%s" % (_msg, traceback.format_exc())
            
            # now split lines and write everyline into the logfile:
            _result = re.compile("[\r\n]+", re.DOTALL + re.IGNORECASE)
            _lines = _result.split(_msg)
            
            # check if multiline
            if len(_lines)>1:
                for _line in _lines:
                    if len(_line) > 0:
                        # if last line:
                        if _line == _lines[-1]:
                            _line = '+ %s' %(_line)
                        elif _line == _lines[0]:
                            _line = _line
                        else:
                            _line = '| %s' %(_line)
                        _formattedMessage = self.logFormat % (_datetime, self.logLevelNames.get(self.logLevel),_sourceFile, _sourceLineNumber, _line)
                        self.logHandle.write(_formattedMessage)
            else:
                _formattedMessage = self.logFormat % (_datetime,self.logLevelNames.get(self.logLevel),_sourceFile, _sourceLineNumber, _msg)
                self.logHandle.write(_formattedMessage)
            
            # Finally close the filehandle
            self.logEntryCount = self.logEntryCount + 1
            if self.logEntryCount % self.flushInterval == 0:
                #self.logHandle.write("Saving")
                self.logEntryCount = 0
                self.logHandle.flush()
            return
        except:
            print("Error logging in Logger.py")
            traceback.print_exc()
            
    #====================== Dummy's for consistency with original logging format
    def info(self, msg, *args, **kwargs):
        self.Write(msg, level=INFO, *args, **kwargs)
        return
    
    def error(self, msg, *args, **kwargs):
        self.Write(msg, level=ERROR, *args, **kwargs)
        return
    
    def warning(self, msg, *args, **kwargs):
        self.Write(msg, level=WARNING, *args, **kwargs)
        return
    
    def debug(self, msg, *args, **kwargs):
        self.Write(msg, level=DEBUG, *args, **kwargs)
        return
    
    def critical(self, msg, *args, **kwargs):
        self.Write(msg, level=CRITICAL, *args, **kwargs)
        return