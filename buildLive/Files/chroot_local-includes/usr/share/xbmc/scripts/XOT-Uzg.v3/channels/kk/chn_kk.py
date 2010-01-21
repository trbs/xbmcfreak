#===============================================================================
# Import the default modules
#===============================================================================
import chn_class
import xbmc, xbmcgui
import re, sys, os, random, copy

#===============================================================================
# Make global object available
#===============================================================================
import common
import mediaitem
import config
import controls
import contextmenu
#import chn_class

logFile = sys.modules['__main__'].globalLogFile
uriHandler = sys.modules['__main__'].globalUriHandler

#===============================================================================
# register the channels
#===============================================================================
if (sys.modules.has_key('progwindow')):
    register = sys.modules['progwindow']
elif (sys.modules.has_key('plugin')):
    register = sys.modules['plugin']
#register.channelButtonRegister.append(106)
register.channelRegister.append('chn_kk.Channel("uzg-channelwindow.xml", config.rootDir, config.skinFolder)')

#===============================================================================
# main Channel Class
#===============================================================================
class Channel(chn_class.Channel):
    
    #===============================================================================
    def InitialiseVariables(self):
        """
        Used for the initialisation of user defined parameters. All should be 
        present, but can be adjusted
        """
        # call base function first to ensure all variables are there
        chn_class.Channel.InitialiseVariables(self)
        
        self.guid = "8F932D18-42F3-11DD-85FF-7DF255D89593"
        self.icon = "kkicon.png"
        self.iconLarge = "kklarge.png"
        self.noImage = "kkimage.png"
        self.channelName = "KanalenKiezer"
        self.channelDescription = "A collection of online streams and channels from all over the world."
        self.moduleName = "chn_kk.py"
        self.maxXotVersion = "3.2.0"
        self.onUpDownUpdateEnabled = False
        
        self.mainListUri = "http://www.kanalenkiezer.nl"
        self.baseUrl = "http://www.kanalenkiezer.nl"
        self.playerUrl = ""
        
        self.requiresLogon = False
        
        self.episodeItemRegex = '<a[^>]+id[^>]+href="(/tv/[^"]+)"[^>]*>([^<]+)</a>'  # used for the ParseMainList
        self.videoItemRegex = '<tr><td><a[^>]+href="(/tv/[^"]+)"[^>]*>([^<]+)</a></td><td>([^<]+)[^=]+<div class="star(\d+)">'   # used for the CreateVideoItem 
        self.folderItemRegex = ''  # used for the CreateFolderItem
        #232|Adventure Free TV|http://www.adventurefree.tv/unicast_mov/AFTVAdventureH264500.mov|0|mov|http://www.adventurefree.tv/|#|
        self.mediaUrlRegex = '\d+\|[^|]+\|([^|]+)\|[^|]+\|[^|]+\|[^|]+\|[^|]+'    # used for the UpdateVideoItem
        
        #========================================================================== 
        # non standard items
        self.descriptionListKK = []
        self.channelCategories = [] # for storing which category has which channels
        self.descriptionRegex = '([^|]*)\|'

        return True
      
    #============================================================================== 
    def initPlugin(self):
        self.pluginMode = True
        logFile.debug("initPlugin::Creating Categories")
        self.CreateCategories()
            
    #==============================================================================
    def CreateEpisodeItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        #logFile.info('starting CreateEpisodeItem for %s', self.channelName)
        item = mediaitem.MediaItem(resultSet[1], "http://www.kanalenkiezer.nl%s" % (resultSet[0],))
        item.icon = self.icon
        item.complete = True
        return item
    
    #============================================================================= 
    def CreateVideoItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        item = mediaitem.MediaItem(resultSet[1],"http://www.kanalenkiezer.nl%s" % (resultSet[0],))
        item.description = resultSet[2]
        item.icon = self.icon
        item.rating = int(resultSet[3])
        item.complete = True
        item.type = "video"
        return item
    
    #============================================================================= 
    def ProcessFolderList(self, url):
        """
            Only added for sorting
        """
        items = chn_class.Channel.ProcessFolderList(self, url)
        items.sort();
        return items
    
    #============================================================================= 
    def UpdateVideoItem(self, item):
        """
        Accepts an item. It returns an updated item. 
        """
        logFile.debug('starting UpdateVideoItem for %s (%s)',item.name, self.channelName)
        
        item.thumb = ""
        item.complete = True
        return item
#    #==============================================================================
#    def CreateCategories(self):
#        del self.descriptionListKK[:]
#        del self.channelCategories[:]
#    
#        #===============================================================================
#        # first get the descriptions and then add them in the list while parsing. 
#        #===============================================================================
#        _data = uriHandler.Open('http://www.kanalenkiezer.nl/cache/indexDESC.txt')
#        _descriptions = common.DoRegexFindAll(self.descriptionRegex, _data)
#        count = 0
#        for _description in _descriptions:
#            logFile.debug("adding description %s:%s", count, _description)
#            self.descriptionListKK.append(_description)
#            count = count + 1
#                    
#        #===============================================================================
#        # now get the html and fill the items
#        #===============================================================================
#        _data = uriHandler.Open(self.baseUrl)
#    
#        #now split data on the categories and get the channels
#        _split = re.split(self.folderItemRegex, _data)
#        
#        #result will be: first part, then value inbetween () then value, then value inbetween () etc...
#        _i = 0
#        for _value in _split:
#            #logFile.debug("%s:", _value)
#            if _i%2 ==0 and _i > 0:
#                # add channel to category
#                _channels = common.DoRegexFindAll(self.episodeItemRegex, _split[_i])
#                for _channel in _channels:
#                    _tmp = self.channelCategories.pop()
#                    
#                    #create custom listitem here, with url, description and name, add that to _tmp.channels
#                    url = "http://www.kanalenkiezer.nl/ajax/getSTREAM.php?id=%s&db=1" % (_channel[1])
#                    logFile.debug("Adding channel: %s (id=%s, desc=%s) to %s", _channel[2],_channel[1], _channel[0], _tmp.name)
#                    logFile.debug("Url = %s", url)
#                    logFile.debug("Desc=%s", self.descriptionListKK[int(_channel[0])])
#                    item = mediaitem.MediaItem(_channel[2], url)
#                    item.description = self.descriptionListKK[int(_channel[0])]
#                    item.icon = self.icon
#                    item.thumb = self.noImage;
#                    item.type = 'video'
#                    
#                    _tmp.channels.append(item)
#                    _tmp.icon = self.icon
#                    self.channelCategories.append(_tmp)
#            elif _i%2 == 1:
#                # add a new category and store position in urlfield
#                logFile.debug("Adding %s as item #%s", _split[_i], (_i-1)/2)
#                _tmp = mediaitem.MediaItem(_split[_i], (_i-1)/2)
#                _tmp.icon = self.icon
#                self.channelCategories.append(_tmp)
#                
#            _i += 1
#    
#        self.channelCategories.pop() #remove erotic because of popups        
#        return
#    
#    #==============================================================================
#    def ParseMainList(self):
#        """ 
#        accepts an url and returns an list with items of type CListItem
#        Items have a name and url. This is used for the filling of the progwindow
#        """
#        logFile.info('Parsing kanalenkiezer')
#        items = []
#        
#        if len(self.channelCategories) < 1:
#            logFile.debug("ParseMainList::Creating Categories")
#            self.CreateCategories()
#    
#        # copy the object in order to sort the items
#        items = copy.copy(self.channelCategories)
#        # because lists are downloaded according to date (else some programs will be missing), a sort on name is performed.
#        items.sort(lambda x, y: cmp(x.name,y.name))
#                
#        return items
#    
#    #==============================================================================
#    def ProcessFolderList(self, url):
#        """ NOT USER EDITABLE
#        Accepts an URL and returns a list of items with at least name & url set
#        Each item can be filled using the ParseFolderItem and ParseVideoItem 
#        Methodes
#        """
#        _items = []
#        logFile.info("Opening caterogy %s with name %s", url, self.channelCategories[int(url)].name)
#                
#        return self.channelCategories[int(url)].channels
#
#    #===============================================================================
#    def PlayVideoItem(self, item, player="defaultplayer"):
#        try:
#            if item.complete == False:
#                item = chn_class.Channel.UpdateVideoItem(self, item)
#            
#            # Check if perhaps a http page is requested:
#            # in order to do a uriHandler.Open it must be HTTP!!!
#            _stream = item.mediaurl
#            if _stream.find('http:')>=0:
#                logFile.info('Checking %s for Content-Type (First Time)', _stream)
#                (_strmHeader, _realUrl) = uriHandler.Header(_stream)
#                logFile.debug('Content-Type: '+ _strmHeader)
#                
#                # start figuring out what type it is....and handle them
#                if _strmHeader.find("video/x-ms-asf")>=0:
#                    item.mediaurl = self.ParseAsxAsf(item.mediaurl)
#                
#            logFile.info('Opening stream in player %s', item.mediaurl)
#            # pass on to main channel class
#            chn_class.Channel.PlayVideoItem(self, item, player)
#        except:
#            logFile.critical("Cannot playback URL: %s", item.mediaurl)