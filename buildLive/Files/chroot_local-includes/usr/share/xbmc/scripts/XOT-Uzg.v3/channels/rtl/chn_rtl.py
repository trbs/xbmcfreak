import sys, re, urllib, math, time,types
import urlparse
#===============================================================================
# Make global object available
#===============================================================================
import common
import mediaitem
import config
import controls
import contextmenu
import chn_class
import helpers 
from helpers import mmshelper

logFile = sys.modules['__main__'].globalLogFile
uriHandler = sys.modules['__main__'].globalUriHandler
#===============================================================================
# register the channels
#===============================================================================
if (sys.modules.has_key('progwindow')):
    register = sys.modules['progwindow']
elif (sys.modules.has_key('plugin')):
    register = sys.modules['plugin']
#register.channelButtonRegister.append(105)
register.channelRegister.append('chn_rtl.Channel("uzg-channelwindow.xml", config.rootDir, config.skinFolder)')

#===============================================================================
# main Channel Class
#===============================================================================
class Channel(chn_class.Channel):
    #===============================================================================
    # define class variables
    #===============================================================================
    def InitialiseVariables(self):
        """
        Used for the initialisation of user defined parameters. All should be 
        present, but can be adjusted
        """
        # call base function first to ensure all variables are there
        chn_class.Channel.InitialiseVariables(self)
        
        self.guid = "15D92364-42F4-11DD-AF9B-7BFF55D89593"
        self.mainListUri = "http://www.rtl.nl/(vm=/service/miMedia/rtl_gemist.xml/)/system/video/menu/videomenu.xml"
        self.baseUrl = "http://www.rtl.nl"
        self.icon = "rtlthumb.png"
        self.iconLarge = "rtllarge.png"
        self.noImage = "rtlimage.png"
        self.channelName = "RTL 4,5&7"
        self.channelDescription = "Uitzendingen van de zenders RTL 4,5,7 & 8."
        self.moduleName = "chn_rtl.py"
        self.maxXotVersion = "3.2.0"
        
        self.backgroundImage = "background-rtl.png"
        self.backgroundImage16x9 = "background-rtl-16x9.png"
        self.requiresLogon = False
        self.sortOrder = 5
        
        self.episodeItemRegex = '<li class="folder" rel="([^"]+)videomenu.xml">([^<]+)</li>'
        self.videoItemRegex = '<li class="video" (thumb="([^"]+)" ){0,1}(thumb_id="([^"]+)" ){0,1}(ctime="([^"]+)" ){0,1}rel="([^"]*/)([^"]+)" (link="([^"]+)"){0,1}>([^<]+)</li>' 
        self.folderItemRegex = '<li class="folder" rel="([^"]*/)([^"]+)">([^<]+)</li>'
        self.mediaUrlRegex = "file:'([^']+_)(\d+)(K[^']+.wmv)'"
        
        self.contextMenuItems = []
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play lowest bitrate stream", "CtMnPlayLow", itemTypes="video", completeStatus=True))            
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play highest bitrate stream", "CtMnPlayHigh", itemTypes="video", completeStatus=True))
        
        #============================================================================== 
        # non standard items
        self.PreProcessRegex = '<ul title="([^"]*)" rel="([^"]*)videomenu.xml"'
        self.progTitle = ""
        self.videoMenu = ""
        #self.parseWvx = True

        return True
    
    #==============================================================================
    def ParseMainList(self):
        # call the main list
        items = []
        if len(self.mainListItems) > 1:
            return self.mainListItems
        
        items = chn_class.Channel.ParseMainList(self)
        
        # get more items:
        url = "http://www.rtl.nl/service/gemist/home/"
        data = uriHandler.Open(url, pb=True)         

        number = 0
        if data != None and data != "":
            moreItems = common.DoRegexFindAll('\["([^"]+)","([^"]+)","[^"]+","([^"]+)"\]', data)
            #                                        0          1                2
            previousNumber = len(items)
            for item in moreItems:
                # check if item2 is present, if so, use that one.
                #logFile.debug(item)
                if item[2] != "" and item[2].endswith("index_video.xml"):
                    url = urlparse.urljoin(self.baseUrl, item[2])
                elif item[2] != "" and item[1].endswith("home/"):
                    #reality/defrogers/home/
                    #http://www.rtl.nl/components/reality/defrogers/index_video.xml
                    url = "%s/components/%s" % (self.baseUrl, item[1].replace("home/","index_video.xml"))                    
                else:
                    url = self.RtlFolderUri("/%s" % item[1], "videomenu.xml")
                moreItem = mediaitem.MediaItem(item[0], url)
                moreItem.icon = self.folderIcon
                moreItem.thumb = self.noImage
                if items.count(moreItem) == 0:
                    number = number + 1
                    items.append(moreItem)
        
        logFile.debug("Added %s more RTL Items to the already existing %s", number, previousNumber)
        
        # sort by name
        if self.episodeSort:
            items.sort(lambda x, y: cmp(x.name.lower(),y.name.lower()))
        
        return items
        
    #==============================================================================
    def CreateEpisodeItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        item = mediaitem.MediaItem(resultSet[1], "http://www.rtl.nl/(vm="+ resultSet[0] + ")/system/video/menu" + resultSet[0] + "videomenu.xml")
        item.icon = self.folderIcon
        return item
    
    #==============================================================================
    def PreProcessFolderList(self, data):
        """
        Accepts an data from the ProcessFolderList Methode, BEFORE the items are
        processed. Allows setting of parameters (like title etc). No return value!
        """
        _items = []
        
        # For this channel there are 2 different options for URLs: the real videomenu.xml (that will result in items)
        # or video_menu.xml (xhtml) that holds the real url to videomenu.xml
        if data.startswith('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">'):
            videomenuUrls = []
            videomenuUrls = common.DoRegexFindAll("prefix\W+'([^']+)'\W+[^']+location[^']+'([^']+)'", data)
            if len(videomenuUrls) > 0:
                data = uriHandler.Open("%s%s%s" % (self.baseUrl, videomenuUrls[0][0], videomenuUrls[0][1]), pb=True)
        
        if len(self.folderHistory)==1:
            # The first folder to be processed
            matches = common.DoRegexFindAll('<ul title="([^"]*)" rel="([^"]*)videomenu.xml"', data)
            self.progTitle = matches[0][0]
            self.videoMenu = matches[0][1]
            
        return (data, _items)
    
    #==============================================================================
    def CreateFolderItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        logFile.debug('starting CreateFolderItem for %s', self.channelName)
        item = mediaitem.MediaItem(resultSet[2], self.RtlFolderUri(resultSet[0],resultSet[1]))
        if len(self.folderHistory)==1:
            item.description = "%s \n%s \n" %(self.progTitle ,item.name)
        else:
            item.description = "%s \n%s \n" %(self.folderHistory[-1].description ,item.name)
        item.icon = self.folderIcon
        item.type = 'folder'
        item.thumb = self.noImage
        item.complete = True
        return item
    
    #============================================================================= 
    def CreateVideoItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        logFile.debug('starting FormatVideoItem for %s', self.channelName)
        #logFile.debug(resultSet)
        #                       0      1               2                     3      4            5   6             7 
        #<li class="video" (thumb="([^"]+)" ){0,1}(ctime="\d+" ){0,1}rel="([^"]*/)([^"]+)" (link="([^"]+)"){0,1}>([^<]+)</li>
        
        #                           0      1              2      3       4        5                    6      7        8      9             10          
        #<li class="video" (thumb="([^"]+)" ){0,1}(thumb_id="([^"]+)" )(ctime="([^"]+)" ){0,1}rel="([^"]*/)([^"]+)" (link="([^"]+)"){0,1}>([^<]+)</li>
     
        item = mediaitem.MediaItem(resultSet[10], self.RtlVideoUri(self.videoMenu, resultSet[6] + resultSet[7]))
        if len(self.folderHistory)>1:
            item.description = self.folderHistory[-1].description + item.name
        else:
            item.description = item.name
        item.icon = self.icon
        item.thumb = self.noImage
        item.thumbUrl = urlparse.urljoin(self.baseUrl, resultSet[1])
        item.type = 'video'
        
        if resultSet[5] != '':
            logFile.debug('ctime=%s (%s)', resultSet[5], time.ctime(int(resultSet[5])))
            item.date = time.strftime('%d-%m-%Y',time.localtime(int(resultSet[5])))
            
        item.complete = False
        
        return item
    
    #============================================================================= 
    def UpdateVideoItem(self, item):
        """
        Accepts an item. It returns an updated item. 
        """
        logFile.debug('starting UpdateVideoItem for %s (%s)',item.name, self.channelName)
        
        if not item.HasMediaListItems():
            data = uriHandler.Open(item.url, pb=False)
            matches = common.DoRegexFindAll(self.mediaUrlRegex, data)
            logFile.debug("Possible Matches for mediaUrl: %s",matches)
    
            if len(matches) > 0:        
                # sort mediaurl -> get highest quality
                matches.sort(lambda x, y: int(y[1])-int(x[1]))
    
                for match in matches:
                    item.AppendMediaListItem("%s%s%s" % match)
            
                logFile.debug("Sorted Matches: %s", item)                
            else:
                logFile.error("Cannot find media URL")
        
        # now we should try to parse them using the MMS helper
        for mediaItem in item.MediaListItems:
            mediaItem.Url = mmshelper.MmsHelper.GetMmsFromHtml(mediaItem.Url)            
        
        logFile.info('finishing UpdateVideoItem: %s.', item)
        
        if item.thumbUrl != "":
            item.thumb = self.CacheThumb(item.thumbUrl)
        item.complete = True
        return item
    
    #============================================================================== 
    def CtMnPlayLow(self, selectedIndex):
        item = self.listItems[selectedIndex]
        self.PlayVideoItem(item, lowBitrate=True)

    def CtMnPlayHigh(self, selectedIndex):
        item = self.listItems[selectedIndex]
        self.PlayVideoItem(item, lowBitrate=False)

    #============================================================================== 
    def PlayVideoItem(self, item, lowBitrate=False, player=""):
        # overriding the default playvideoitem to allow selection of low and high bitrate
        
        if item.HasMediaListItems():
            # create dummy item for playback
            dummy = mediaitem.MediaItem(item.name, item.url, item.type)
            dummy.complete = True
            
            logFile.debug("Created dummy record for playback: %s", dummy)
            
            #select the right url
            if not lowBitrate:                
                dummy.AppendMediaListItem(item.MediaListItems[0].Url)
                logFile.debug("Starting playback of the high bitrate mediaUrl (%s)", item.MediaListItems[0].Url)
            else:
                dummy.AppendMediaListItem(item.MediaListItems[-1].Url)
                logFile.debug("Starting playback of the low bitrate mediaUrl (%s)", item.MediaListItems[-1].Url)
            
            chn_class.Channel.PlayVideoItem(self, dummy, player)            
        else:
            logFile.debug("Starting playback of the only available url in item %s", item)
            
            chn_class.Channel.PlayVideoItem(self, item, player)
            

    #===============================================================================
    def RtlFolderUri(self, folder, filename):
        return 'http://www.rtl.nl/(vm='+ folder + ')/system/video/menu' + folder + filename

    #===============================================================================    
    def RtlVideoUri(self, videoMenu, videoURL):
        return 'http://www.rtl.nl/(vm'+ videoMenu + ')' + videoURL
