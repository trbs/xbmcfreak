#===============================================================================
# LICENSE XOT-Framework - CC BY-NC-ND
#===============================================================================
# This work is licenced under the Creative Commons 
# Attribution-Non-Commercial-No Derivative Works 3.0 Unported License. To view a 
# copy of this licence, visit http://creativecommons.org/licenses/by-nc-nd/3.0/ 
# or send a letter to Creative Commons, 171 Second Street, Suite 300, 
# San Francisco, California 94105, USA.
#===============================================================================
import os, platform, sys, xbmc, types

class EnvController:
    def __init__(self, logger = None):
        """
            Class to determine platform depended stuff
        """
        self.logger = logger
        pass
    
    def GetEnvironment(self, displayOnly = False):
        """
            Get the environment type of the current Python
        """
        #print "os.environ"
        #print platform.architecture()
        env = os.environ.get( "OS", "win32" )
        #print env
        
        if env == "Linux":
            (bits, type) = platform.architecture()
            if bits.count("64") > 0:
                # first the bits of platform.architecture is checked
                return "Linux64"
            elif sys.maxint >> 33:
                # double check using the sys.maxint
                # and see if more than 32 bits are present
                return "Linux64"
            else:
                return "Linux"
        elif env == "OS X":
            return "OS X"
        else: 
            if displayOnly and not env == "win32":
                print "Setting XOT Environment to %s" % env
                return env
            else:
                print "Setting XOT Environment to Win32"
                return "win32"
    
    #===============================================================================
    def JoinXOTBasedXBMCPath(self, *args):
        """
            return a correct XBMC path relative to the XOT path
        """
        
        # if the args is passed on to from another method, it will be a single argument of
        # type typle that holds the original args
        if len(args) == 1 and type(args[0]) == types.TupleType:
            args = args[0]
        
        raise NotImplementedError('JoinXOTBasedXBMCPath :: This most be fixed to not point to /home/scripts all the time')
        
        scriptName = os.path.split(os.getcwd())[-1]
        parts = ('special://home/scripts',scriptName)
        parts = parts + args
        
        try:
            # first try new parsing
            path = '/'.join(parts)
            # check if it is supported
            seeIfSpecialPathsAreAvailable = xbmc.translatePath(path)
        except:
            path = os.path.join(parts)
            if self.logger != None:
                self.logger.debug('Falling back to old non "special://"-paths', exc_info = True)
            else:
                print 'Falling back to old non "special://"-paths'
            
#        if self.logger == None:
#            print 'XOT found path: %s' % (path,)
#            pass
#        else:
#            self.logger.debug("XOT found path %s", path)
            
        return path 
    
    #===============================================================================
    def JoinXOTBasedOSPath(self, *args):
        """
            return a correct OS path relative to the XOT path
        """
        path = self.JoinXOTBasedXBMCPath(args[:])
        return self.GetOSPathFromXBMCPath(path)
    
    #===============================================================================
    def GetOSPathFromXBMCPath(self, xbmcPath):
        """
            returns the OS path
        """
        if xbmcPath.startswith('special://'):
            osPath = xbmc.translatePath(xbmcPath)
#            if self.logger != None:
#                self.logger.debug("Converting %s to %s", xbmcPath, osPath)
            return osPath
        else:
            return xbmcPath