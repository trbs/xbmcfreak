#===============================================================================
# LICENSE XOT-Framework - CC BY-NC-ND
#===============================================================================
# This work is licenced under the Creative Commons 
# Attribution-Non-Commercial-No Derivative Works 3.0 Unported License. To view a 
# copy of this licence, visit http://creativecommons.org/licenses/by-nc-nd/3.0/ 
# or send a letter to Creative Commons, 171 Second Street, Suite 300, 
# San Francisco, California 94105, USA.
#===============================================================================

#===============================================================================
# Import the default modules
#===============================================================================
from logging import thread
from mediaitem import MediaListItem
import urlparse
import threading
import xbmc, xbmcgui 
import sys, os, types
#===============================================================================
# Make global object available
#===============================================================================
import common
import mediaitem
import config
import controls
import contextmenu
import settings
import guicontroller
from helpers import htmlentityhelper
#import chn_class

logFile = sys.modules['__main__'].globalLogFile
uriHandler = sys.modules['__main__'].globalUriHandler

#===============================================================================
# register the channels
#===============================================================================
# register = sys.modules['progwindow']
# register.channelRegister.append('chn_rtl.Channel("uzg-channelwindow.xml", config.rootDir, config.skinFolder)')

#===============================================================================
# main Channel Class
#===============================================================================
class Channel(xbmcgui.WindowXML):
    """
    main class from which all channels inherit
    """
    
    #============================================================================== 
    def __init__(self, *args, **kwargs):
        """ NOT USER EDITABLE
        Initialisation of the class. All class variables should be instantiated here
        """
        self.listItems = []    #holds the items in the list
        self.mainListItems = []
        self.folderHistory = []                  # top one contains selected position in PREVIOUS Folder
        self.folderHistorySelectedPosition = []  # top one contains the url of the CURRENT Folder
        self.currentPosition = 0;
        self.parentItem = None
        self.folderIcon = "xot_defaultfolder.png"
        self.appendIcon = "xot_DefaultAppend.png"
        if kwargs.has_key("channelCode"):
            self.channelCode = kwargs["channelCode"]
            #logFile.debug("ChannelCode present: %s", self.channelCode)
        else:
            self.channelCode = ""
            #logFile.debug("No channelCode present")
        self.initialUri = "" #uri that is used for the episodeList. NOT mainListUri
        self.proxy = None
        
        self.windowInitialised = False
        #self.keysLocked = 0 #0=False, 1=True, >1 True and already new commands
        self.loggedOn = False
        
        # set timer timeout for keyupdown
        self.timerTimeOut = 0.5
        self.videoUpdateLock = threading.Lock()
        self.focusControlID = 0
        
        # initialise user defined variables
        self.InitialiseVariables()
        
        # update image file names: point to local folder if not present in skin
        self.icon = self.GetImageLocation(self.icon)
        self.iconLarge = self.GetImageLocation(self.iconLarge)
        self.folderIcon = self.GetImageLocation(self.folderIcon)
        self.appendIcon = self.GetImageLocation(self.appendIcon)
        self.noImage = self.GetImageLocation(self.noImage)
        self.backgroundImage = self.GetImageLocation(self.backgroundImage)
        self.backgroundImage16x9 = self.GetImageLocation(self.backgroundImage16x9)
        
        # plugin stuff
        self.pluginMode = False
        logFile.debug("Initialized: %s", self)
                
    #===============================================================================
    # define class variables
    #===============================================================================
    def InitialiseVariables(self):
        """
        Used for the initialisation of user defined parameters. All should be 
        present, but can be adjusted
        """
        #logFile.debug("Starting IntialiseVariables from chn_class.py")
        # call base function first to ensure all variables are there
        # chn_class.Channel.InitialiseVariables(self)
        
        self.guid = "00000000-0000-0000-0000-000000000000"
        self.icon = ""
        self.iconLarge = ""
        self.noImage = ""
        self.backgroundImage = ""  # if not specified, the one defined in the skin is used
        self.backgroundImage16x9 = ""  # if not specified, the one defined in the skin is used
        self.channelName = "Channel Class"
        self.channelDescription = "This is the channelclass on which all channels are based"
        self.moduleName = "chn_class.py"
        self.maxXotVersion = "1.0.0"
        self.sortOrder = 255 #max 255 channels
        self.buttonID = 0
        self.onUpDownUpdateEnabled = True
        self.contextMenuItems = []
        
        self.mainListUri = ""
        self.baseUrl = ""
        self.playerUrl = ""
        self.defaultPlayer = 'defaultplayer' #(defaultplayer, dvdplayer, mplayer)
        
        self.passWord = ""
        self.userName = ""
        self.logonUrl = ""
        self.requiresLogon = False
        
        self.asxAsfRegex = '<[^\s]*REF href[^"]+"([^"]+)"' # default regex for parsing ASX/ASF files
        
        self.episodeItemRegex = '' # used for the ParseMainList
        self.videoItemRegex = ''   # used for the CreateVideoItem 
        self.folderItemRegex = ''  # used for the CreateFolderItem
        self.mediaUrlRegex = ''    # used for the UpdateVideoItem
        
        """ 
            The ProcessPageNavigation method will parse the current data using the pageNavigationRegex. It will
            create a pageItem using the CreatePageItem method. If no CreatePageItem method is in the channel,
            a default one will be created with the number present in the resultset location specified in the 
            pageNavigationRegexIndex and the url from the combined resultset. If that url does not contain http://
            the self.baseUrl will be added. 
        """
        self.pageNavigationIndicationRegex = '' 
        self.pageNavigationRegex = '' 
        self.pageNavigationRegexIndex = 0 
       
        self.episodeSort = True
        
        #========================================================================== 
        # non standard items
        
        return True
      
    #==============================================================================
    # Inherited from xbmcgui.WindowXML
    #==============================================================================
    def onInit(self):
        """ NOT USER EDITABLE
        Initialisation of class after the GUI has been loaded. This happens every
        time. Triggered by doModal in the ShowEpisodeWindow Methode
        """
        try:
            logFile.info("onInit(): Window Initalized for %s", self.moduleName)
            if not self.windowInitialised:
                logFile.debug("Initializing %s Gui for the first time", self.channelName)
                guiController = guicontroller.GuiController(self)
                
                # set background
                if self.getResolution() in controls.RESOLUTION_16x9 and self.backgroundImage16x9!="":
                    self.getControl(controls.EP_BACKGROUND).setImage(self.backgroundImage16x9)
                    logFile.debug("Resolution=%s, %s", self.getResolution(), self.backgroundImage16x9)
                
                elif self.getResolution() in controls.RESOLUTION_4x3 and self.backgroundImage!="":
                    self.getControl(controls.EP_BACKGROUND).setImage(self.backgroundImage)
                    logFile.debug("Resolution=%s, %s", self.getResolution(), self.backgroundImage)
                            
                # make sure the history is cleared!
                logFile.debug("Clearing Folder History")
                del self.folderHistory[:]
                del self.folderHistorySelectedPosition [:]
                
                # add initialUri to root and give it the default image and no description.
                # the latter two are used for clearing the fields while loading a new list
                _tmpItem = mediaitem.MediaItem("", self.initialUri)
                _tmpItem.description = "Please wait while loading data"
                _tmpItem.thumb = self.noImage
                guiController.ShowData(_tmpItem)
                self.folderHistory.append(_tmpItem)
                self.folderHistorySelectedPosition.append(0)
            
                # logging on
                logFile.debug("LogonCheck")
                self.loggedOn = self.LogOn(self.userName, self.passWord)
            
                #make sure keys are unlocked upon init
                #self.keysLocked = 0
                
                if not self.loggedOn:
                    logFile.error('Not logged on...exiting')
                    self.close()
                else:
                    # create new rootItem and fetch it's items
                    rootItem = mediaitem.MediaItem("root", self.initialUri)
                    rootItem.items = self.ProcessFolderList(self.initialUri)
                    rootItem.thumb = self.noImage
                    
                    # clear history and add the rootitem
                    del self.folderHistory[:]
                    self.folderHistory.append(rootItem)
                    
                    # now display the items.
                    self.listItems = rootItem.items
                    
                    guiController = guicontroller.GuiController(self)
                    guiController.DisplayPageNavigation(self.listItems)
                    guiController.DisplayFolderList(self.listItems, 0)
                    
                    self.windowInitialised = True
                    
                logFile.debug("%s Gui has been initialised for the first time", self.channelName)
            else:
                logFile.debug("%s GUI window already Initialized", self.channelName)
                
                if self.getControl(controls.EP_LIST).size() < 1:
                    logFile.info("Somehow the list was cleared...filling it again")
                    guiController = guicontroller.GuiController(self)
                    guiController.DisplayPageNavigation(self.listItems)
                    guiController.DisplayFolderList(self.listItems, self.currentPosition)

        except:
            logFile.critical("Error initialising the %s Window.", self.channelName , exc_info=True)
    
    #===============================================================================
    #    Init for plugin
    #===============================================================================
    def initPlugin(self):
        """
            Special initialisation for plugin version
        """
        # create dummy history item
        self.folderHistory.append(mediaitem.MediaItem("Dummy Plugin item", ""))
        self.pluginMode = True
    
    #============================================================================== 
    def onAction(self, action):
        """ NOT USER EDITABLE
        Action Method for handling all actions except the clicking. This one should
        only be inherited, not overwriten
        """
        try:
            if not action.getId() in controls.ACTION_MOUSE_MOVEMENT:
                logFile.debug("onAction (with buttonid=%s and id=%s) detected (ThrdID=%s)", action.getButtonCode(), action.getId(),thread.get_ident())
            
            if action in controls.ACTION_UPDOWN:
                if (self.getFocusId() == controls.EP_LIST):
                    try:
                        logFile.debug("Cancelling and starting onKeyUpDown timer")
                        # cancel the timer is present
                        try:
                            self.timerUpDown.cancel()
                        except:
                            pass
                        # start a new one
                        self.timerUpDown = threading.Timer(self.timerTimeOut, self.onUpDown)
                        self.timerUpDown.start()
                    except:
                        logFile.critical("Error in locking mechanism")

            elif action == controls.ACTION_PARENT_DIR or action == controls.ACTION_PREVIOUS_MENU:
                try:
                    logFile.debug("Removing items from historystack")
                    self.folderHistory.pop()
                    
                    # release the video update lock if present
                    try:
                        self.videoUpdateLock.release()
                    except:
                        # if it wasn't locked, pass the exception
                        pass
                    
                    if self.folderHistory == []:
                        self.onExit()
                    else:
                        # go back an folder, clear list, process the folder and stuff the 
                        # content back in the list
                        self.listItems = self.folderHistory[-1].items
                        if len(self.listItems) < 1:
                            # the caching did not work. Start retrieving it
                            self.listItems = self.ProcessFolderList(self.folderHistory[-1].url)

                        guiController = guicontroller.GuiController(self)
                        guiController.DisplayFolderList(self.listItems, self.folderHistorySelectedPosition.pop())
                        guiController.DisplayPageNavigation(self.listItems)
                    
                except:
                    logFile.critical("Cannot perform a good BACK action. Closing!", exc_info=True)
                    self.onExit()
                    
#            elif action == controls.ACTION_SELECT_ITEM:
#                self.onClick(self.getFocusId())
            
            elif action in controls.ACTION_CONTEXT_MENU_CONTROLS: # and self.keysLocked < 1:
                logFile.debug("showing contextmenu")
                self.onActionFromContextMenu()
            
            else:
                pass
                #logFile.warning("Action %s on ControlID %s was not recognised! No action taken", action, self.getFocus())
        except:
            logFile.warning('Action Failed, or could not determine action', exc_info=True)
        
    #===============================================================================
    # Customizable actions    
    #===============================================================================
    def onFocus(self, controlID):
        """"
        onFocus(self, int controlID)
        This function has been implemented and works
        """
        self.focusControlID = controlID
    
    #============================================================================== 
    def onClick(self, controlID):
        """
        Catching of clicking (Select/OK)
        """
        logFile.debug("OnClick detected on controlID = %s", controlID)
        
        try:
            # check if the Episode List is active
            logFile.debug("Trying to determine what to do with the onClick")
            guiController = guicontroller.GuiController(self)
                
            if controlID == controls.EP_LIST or controlID == controls.PG_LIST:
                # get the episodelist position
                position = self.getCurrentListPosition()
                
                # store the position
                self.currentPosition = position
                    
                if controlID == controls.PG_LIST:
                    # a page was clicked! 
                    logFile.debug("OnClick detected on pageList")
                    pagePos = self.getControl(controls.PG_LIST).getSelectedPosition()
                    
                
                    # get the item, therefore we need to filter the items for pageitems
                    pageItems = []
                    for item in self.listItems:
                        if item.type == "page":
                            pageItems.append(item)
                
                    item = pageItems[pagePos]
                else:
                    logFile.debug("OnClick detected on EPList")
                    item = self.listItems[position]
                    
                # Determine type of item
                if item.type == 'video':
                    # if not complete, update
                    logFile.debug("Detected Video file")
                    if not item.complete:
                        item = self.UpdateVideoItem(item)
                        # if the mediaUrl is not filled: item is not complete
                        if not item.HasMediaListItems():
                            item.complete = False
                        
                        # check if the list has not changed during upate:
                        #if item.guid == self.listItems[position].guid:
                        if item.Equals(self.listItems[position]):
                            logFile.info("Updating item (GUIDs match)")                
                            self.listItems[position] = item
                        else:
                            logFile.error("Aborting Update because of GUID mismatch")
                    logFile.info("Starting playback of %s (mediaItem=%s)", item)
                    guiController.ShowData(item)
                    self.PlayVideoItem(item)
                elif item.type == 'folder' or item.type == 'page':
                    logFile.debug("Detected Folder or Page\nAppending current selected position (%s) to history.", position)

                    # remember the selected position 
                    self.folderHistorySelectedPosition.append(position)
                    
                    # append the item to the history
                    self.folderHistory.append(item)
                    
                    # add content items to the selected item
                    item.items = self.ProcessFolderList(item.url)
                    
                    # make those items the listItems
                    self.listItems = item.items
        
                    # display items
                    guiController.DisplayPageNavigation(self.listItems)
                    guiController.DisplayFolderList(self.listItems, 0)
                        
                elif item.type == 'append':
                    logFile.debug("Detected Appendable Folder on position %s", position)
                    
                    #read the currently showing parentitem and it's childitems 
                    parentItem = self.folderHistory[-1]
                    
                    #get new items
                    items = self.ProcessFolderList(item.url)
                    
                    #append them to the childitems of the parentitem
                    self.AppendItemsAt(parentItem.items, items, position)
                                        
                    #sort them or not
                    
                    #show them and highlight the current selection
                    self.listItems = parentItem.items
                    guiController.DisplayFolderList(self.listItems, position)
                    self.onUpDown(True)                
                else:
                    logFile.warning("Error updating %s (%s) for %s", item.name, item.type, self.channelName)
                        
            else:
                logFile.warning("ControlID (%s) was not recognised! No action taken", controlID)
        except:
            logFile.critical("On Click error showing episodes", exc_info=True)
     
    #============================================================================== 
    def onUpDown(self, ignoreDisabled = False):
        """ NOT USER EDITABLE
        Action Method for handling selecting. If the ignoreDisalbe is set to True
        it makes the script ignore self.onUpDownUpdateEnabled and update anyway! 
        """
        logFile.debug("OnKeyUp/KeyDown Detected")
        try:
            # get the item that is focused
            position = self.getCurrentListPosition()
            item = self.listItems[position]
            guiController = guicontroller.GuiController(self)
            
            if item.complete:
                #item is complete. Just show
                logFile.debug("No OnKeyUp/KeyDown for a complete item")
                guiController.ShowData(self.listItems[position])
                return
            
            if item.type == "folder" or item.type == "append":
                #item is folder. 
                logFile.debug("No OnKeyUp/KeyDown for a folder or append item")
                guiController.ShowData(self.listItems[position])
                return
            
            if item.complete == False and item.type == "video" and (not self.onUpDownUpdateEnabled and not ignoreDisabled):
                # item is not complete, but the onupdown is disabled and we don't have to ignore that
                # just show the data
                logFile.debug("Item is not complete, but the onupdown is disabled and we don't have to ignore that. Only showing data")
                guiController.ShowData(self.listItems[position])
                return
            
            if item.complete == False and item.type == "video" and (self.onUpDownUpdateEnabled or ignoreDisabled):
                # if video item and not complete, do an update if not already busy
                
                #===============================================================================
                # Locking block 
                #===============================================================================
                # aquire lock so that all new timers in the keyUp/Down actions will
                # be blocked! A timer is set to call the onUpDown again after waiting
                logFile.debug("1.==== Trying to acquire a lock")
                if (not self.videoUpdateLock.acquire(0)):
                    logFile.debug("2.==== Lock was already active")
                    try:
                        self.timerUpDown.cancel()
                    except:
                        pass
                    logFile.debug("Resetting the timer from within onUpDown")
                    self.timerUpDown = threading.Timer(self.timerTimeOut, self.onUpDown)
                    self.timerUpDown.start()
                    return
                logFile.debug("2.==== Lock Acquired")
                #============================================================================== 
                # Actual action happens now:
                logFile.debug("Item '%s' not completed yet. Updating Video", item.name)
                
                #display please wait:
                guiController.ShowData(self.folderHistory[0])
                
                item = self.UpdateVideoItem(item)
                # if the mediaUrl is not filled: item is not complete
                if not item.HasMediaListItems():
                    item.complete = False
                
                # check if the list has not changed during upate:
                if item.Equals(self.listItems[position]):
                    logFile.info("Updating item (GUIDs match)")                
                    self.listItems[position] = item
                else:
                    logFile.error("Aborting Update because of GUID mismatch\n(%s and %s)", item.guid, self.listItems[position].guid)
                
                # release lock
                logFile.debug("3.==== UnLocking the lock")
                
                guiController.ShowData(self.listItems[position]) 
                self.videoUpdateLock.release()    
                #===============================================================================
                # Locking block End 
                #===============================================================================
            else:
                #if nothing matched
                logFile.debug("OnUpDown: does not know what to do")
                return
        except:
            try:
                # release lock
                logFile.debug("3.==== Unlocking the lock after an excpetion")
                self.videoUpdateLock.release()
            except:
                pass
                
            logFile.critical("Cannot handle KeyUp/Down", exc_info=True)
            
    
    #============================================================================== 
    def onExit(self):
        """
        Action Method for handling exiting
        """
        self.listItems = []
        self.getControl(controls.EP_LIST).reset()
        self.close()
    
    #==============================================================================
    # ContextMenu functions
    #==============================================================================
    def onActionFromContextMenu(self):
        """ NOT USER EDITABLE
            Using of the ContextMenu. 
        """
        try:
            position = self.getCurrentListPosition()
            item = self.listItems[position]
            contextMenuItems = []
            
            if item.type == 'folder':
                contextMenuItems.append(contextmenu.ContextMenuItem("Add to favorites", "CtMnAddToFavorites"))
            elif item.type == 'video':
                pass
            else:
                return None
            
            logFile.debug(self.contextMenuItems)
            
            for menuItem in self.contextMenuItems:
                logFile.debug("%s (%s), %s %s", menuItem.label, menuItem.functionName, menuItem.itemTypes, menuItem.completeStatus)
                if menuItem.itemTypes == None or menuItem.itemTypes == item.type:
                    if menuItem.completeStatus == None or menuItem.completeStatus == item.complete:
                        contextMenuItems.append(menuItem)
                
            if len(contextMenuItems) == 0:
                return None 
            
            # build menuitems
            contextMenu = contextmenu.GUI(config.contextMenuSkin, config.rootDir, config.skinFolder, parent=self.getFocus(), menuItems = contextMenuItems)
            selectedItem = contextMenu.selectedItem
            del contextMenu
            
            # handle function from items
            if (selectedItem is not None):    
                selectedMenuItem = contextMenuItems[selectedItem]
                functionString = "self.%s(%s)" % (selectedMenuItem.functionName, position)
                logFile.debug("Calling %s", functionString)
                try:
                    exec(functionString)
                except:
                    logFile.error("onActionFromContextMenu :: Cannot execute '%s'.", functionString, exc_info = True)
            
            return None
        except:
            logFile.error("onActionFromContextMenu :: Error on contextmenu action", exc_info = True)
            return None
    
    #============================================================================== 
    def CtMnAddToFavorites(self, selectedIndex):
        """
            Add to favorites
        """
        item = self.listItems[selectedIndex]
        
        if item.type != 'folder':
            logFile.error("AddToFavorites :: Can only add folder items. Got %s-item", item.type)
            return 
        
        settings.AddToFavorites(item, self)        
        return      
      
    #==============================================================================
    # Custom Methodes, in chronological order   
    #==============================================================================
    def ParseMainList(self):
        """ 
        accepts an url and returns an list with items of type CListItem
        Items have a name and url. This is used for the filling of the progwindow
        """
        items = []
        if len(self.mainListItems) > 1:
            return self.mainListItems
        
        _data = uriHandler.Open(self.mainListUri, proxy = self.proxy)
        
        # first process folder items.
        _episodeItems = common.DoRegexFindAll(self.episodeItemRegex, _data)
        for _episode in _episodeItems:
            _tmpItem = self.CreateEpisodeItem(_episode)
            # catch the return of None
            if _tmpItem and items.count(_tmpItem) == 0:
                items.append(_tmpItem)
        
        # sort by name
        if self.episodeSort:
            items.sort(lambda x, y: cmp(x.name.lower(), y.name.lower()))
        
        self.mainListItems = items
        return items
    
    #==============================================================================
    def SearchSite(self):
        """
        Creates an list of items by searching the site
        """
        items = []
        
        item = mediaitem.MediaItem("Search Not Implented","", type="video")
        item.icon = self.icon
        items.append(item)
    
        return items
    
    #==============================================================================
    def CreateEpisodeItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        logFile.debug('starting CreateEpisodeItem for %s', self.channelName)
        
        # dummy class
        _item = mediaitem.MediaItem("No CreateEpisode Implented!", "")
        _item.complete = True
        return _item
    
    #==============================================================================
    def ShowEpisodeWindow(self, url):
        """ NOT USER EDITABLE
        shows the epsiode window and thus triggers the onInit
        """
        self.initialUri = url
        self.windowInitialised = False
        self.doModal()
    
    #==============================================================================
    def PreProcessFolderList(self, data):
        """
        Accepts an data from the ProcessFolderList Methode, BEFORE the items are
        processed. Allows setting of parameters (like title etc). No return value!
        """
        logFile.info("Performing Pre-Processing")
        _items = []
        logFile.debug("Pre-Processing finished")
        return (data, _items)
          
    #==============================================================================
    def ProcessFolderList(self, url):
        """ NOT USER EDITABLE
        Accepts an URL and returns a list of items with at least name & url set
        Each item can be filled using the ParseFolderItem and ParseVideoItem 
        Methodes
        """
        
        if not self.pluginMode:
            guiController = guicontroller.GuiController(self)
            guiController.ClearEpisodeLists()
            guiController.ShowData(self.folderHistory[0])
        
        preItems = []
        folderItems = []
        videoItems = []
        pageItems = []
        
        if (url == "searchSite"):
            logFile.debug("Starting to search")
            return self.SearchSite()
                        
        
        data = uriHandler.Open(url, proxy = self.proxy)
        
        # first of all do the Pre handler
        (data, preItems) = self.PreProcessFolderList(data)
        
        # then process folder items.
        if not self.folderItemRegex == '':
            folders = common.DoRegexFindAll(self.folderItemRegex, data)
            for folder in folders:
                folderItems.append(self.CreateFolderItem(folder))
            
        # sort by name
        folderItems.sort(lambda x, y: cmp(x.name.lower(), y.name.lower()))
        
        # now process video items
        if not self.videoItemRegex =='':
            videos = common.DoRegexFindAll(self.videoItemRegex, data)
            for video in videos:
                videoItems.append(self.CreateVideoItem(video))
        
        # sort 
        #videoItems.sort()
        
        # now process page navigation if a pageNavigationIndication is present
        if not self.pageNavigationRegex == '':
            pageItems = self.ProcessPageNavigation(data)

        return preItems + folderItems + videoItems + pageItems

    #============================================================================== 
    def ProcessPageNavigation(self, data):
        """ NOT USER EDITABLE
            Generates a list of pageNavigation items. Could also be used in the
            future to add a pageNav control or something (but not for plugin)
        """
        logFile.debug("Starting ProcessPageNavigation")
        
        pageItems = []
        #indication = common.DoRegexFindAll(self.pageNavigationIndicationRegex, data)
        #pagesPresent = len(indication) > 0
        
        #if not pagesPresent:
        #    logFile.debug("No pagenavigation found")
        #    return pageItems
        
        #logFile.debug("Pagenavigation found")
        
        # try the regex on the current data
        pages = common.DoRegexFindAll(self.pageNavigationRegex, data)
        if len(pages) == 0:
            logFile.debug("No pages found.")
            return pageItems
        
#            logFile.debug(pages)
#            
#            # create a possible Url
#            pageNavUrl = ''
#            for part in indication[-1]:
#                pageNavUrl = '%s%s' % (pageNavUrl, part)
#            
#            if not pageNavUrl.startswith("http:"):
#                if pageNavUrl.startswith("/") and self.baseUrl.endswith("/"):
#                    pageNavUrl = pageNavUrl.lstrip("/")
#                if not pageNavUrl.startswith("/") and not self.baseUrl.endswith("/"):
#                    pageNavUrl = "/%s" % (pageNavUrl)
#                pageNavUrl = "%s%s" % (self.baseUrl, pageNavUrl)
#            
#            # Add the current item as page number 1
#            firstPage = mediaitem.MediaItem("1", pageNavUrl)
#            firstPage.type = "page"
#            pageItems.append(firstPage)
#            
#            data = uriHandler.Open(pageNavUrl)
        pages = common.DoRegexFindAll(self.pageNavigationRegex, data)
        
        for page in pages:
            item = self.CreatePageItem(page)
            pageItems.append(item)
        
        # filter double items
        for item in pageItems:
            if pageItems.count(item) > 1:
                logFile.debug("Removing duplicate for '%s'", item.name)
                pageItems.remove(item)
        
        #logFile.debug(pageItems)
        return pageItems
    
    #==============================================================================
    def CreatePageItem(self, resultSet):
        """
        Accepts an resultset
        """
        logFile.debug("Starting CreatePageItem")
        total = ''
        
        for set in resultSet:
            total = "%s%s" % (total,set)
        
        total = htmlentityhelper.HtmlEntityHelper.StripAmp(total)
        
        if not self.pageNavigationRegexIndex == '':
            item = mediaitem.MediaItem(resultSet[self.pageNavigationRegexIndex], urlparse.urljoin(self.baseUrl, total))
        else:
            item = mediaitem.MediaItem("0")            
        
        item.type = "page"
        logFile.debug("Created '%s' for url %s", item.name, item.url)
        return item 
        
    #==============================================================================
    def CreateFolderItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        logFile.debug('starting CreateFolderItem for %s', self.channelName)
        
        item = mediaitem.MediaItem("No CreateFolderItem Implented!", "")
        item.complete = True
        return item
    
    #============================================================================= 
    def CreateVideoItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        logFile.debug('starting CreateVideoItem for %s', self.channelName)
        
        item = mediaitem.MediaItem("No CreateVideoItem Implented!", "")
        item.complete = True
        return item
    
    #============================================================================= 
    def UpdateVideoItem(self, item):
        """
        Accepts an item. It returns an updated item. Usually retrieves the MediaURL 
        and the Thumb! It should return a completed item. 
        """
        logFile.info('starting UpdateVideoItem for %s (%s)', item.name, self.channelName)
        
        _data = uriHandler.Open(item.url, pb=False, proxy = self.proxy)

        url = common.DoRegexFindAll(self.mediaUrlRegex, _data)[-1]
        item.MediaListItems.append(mediaitem.MediaListItem(item.name, url))
        
        logFile.info('finishing UpdateVideoItem. MediaItems are %s', item)
        
        item.thumb = self.noImage
        if not item.HasMediaListItems():
            item.complete = False
        else:
            item.complete = True
        return item
    
    #==============================================================================
    def DownloadVideoItem(self, item):
        """ 
        Accepts an item and starts the download process
        """
        if item.type != 'video':
            logFile.error("Cannot download a folder item.")
            return item
        
        if item.type == 'video':
            if item.complete == False:
                logFile.info("Fetching MediaUrl for VideoItem")
                item = self.UpdateVideoItem(item)
    
            if item.complete == False or not item.HasMediaListItems():
                logFile.error("Cannot download incomplete item or item without MediaListItems")
                return item
        
            for mediaListItem in item.MediaListItems:
                logFile.debug("Trying to download %s", mediaListItem)
                downloadUrl = mediaListItem.Url 
                if downloadUrl.find(".divx") > 0:
                    saveFileName = "%s.divx" % (item.name)
                elif downloadUrl.find(".flv") > 0:
                    saveFileName = "%s.flv" % (item.name)
                elif downloadUrl.find(".avi") > 0:
                    saveFileName = "%s.avi" % (item.name)
                else:
                    saveFileName = item.name
                
                logFile.debug(saveFileName)
                #saveFileName = xbmc.makeLegalFilename(saveFileName)
                #saveFileName = uriHandler.CorrectFileName(saveFileName)
                uriHandler.Download(mediaListItem.Url, saveFileName)
                item.downloaded = True               
        
        return item
    #==============================================================================
    def AppendItemsAt(self, source, appendix, position):
        """ NOT USER EDITABLE
            appends a list of items at a certain position
        """
        #reverse the 'appendix' items for easier insertion
        appendix.reverse()
        
        # remove the item which is replaced
        removedItem = source.pop(position)
        
        for item in appendix:
            # do not add more pages or double items
            if source.count(item) == 0 and item.type != 'append':
                source.insert(position, item)
                    
        return
        
    #============================================================================== 
    def LogOn(self, *args):
        """
        Logs on to a website, using an url. Returns True on success
        """
        if not self.requiresLogon:
            logFile.info("No login required of %s", self.channelName)
            return True
        
        if self.loggedOn:
            logFile.info("Already logged in")
            return True
        
        _rtrn = False
        _passWord = args["userName"]
        _userName = args["passWord"]
        return _rtrn
    
    #============================================================================== 
    def ParseAsxAsf(self, url):
        """
        Parses an ASX/ASF and returns the real media url.
        """
        try:
            logFile.debug('Starting ASF/ASX Parsing for %s', url)
            _data = uriHandler.Open(url, pb=True, proxy = self.proxy)
            logFile.debug("Opened the ASF/ASX: \n%s", _data)
            _mediaUrl = common.DoRegexFindAll(self.asxAsfRegex, _data)
            logFile.debug("%s", _mediaUrl)
            _mediaUrl = _mediaUrl[0]
            logFile.info("Discovered ASX/ASF URL: %s", _mediaUrl)
        except:
            logFile.warning("Error Parsing the ASX/ASF", _mediaUrl, exc_info=True)
            # but give it a try anyway
            _mediaUrl = url
        
        return _mediaUrl
    
    #============================================================================== 
    def PlayVideoItem(self, item, player=""):
        """ NOT USER EDITABLE
        Accepts an item with or without MediaUrl and playback the item. If no 
        MediaUrl is present, one will be retrieved.
        """
        
        try:
            playList = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
            playList.clear()
            
            if player == "":
                player = self.defaultPlayer
            
            logFile.info("Starting Video Playback using the %s", player)
                    
            playList = item.GetXBMCPlayList()
            
            if player=="dvdplayer":
                logFile.info("Playing using DVDPlayer")
                xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(playList)
            elif player=="mplayer":
                logFile.info("Playing using Mplayer")
                xbmc.Player(xbmc.PLAYER_CORE_MPLAYER).play(playList)
            else:
                logFile.info("Playing using default player")
                xbmc.Player(xbmc.PLAYER_CORE_AUTO).play(playList)
        except:
            dialog = xbmcgui.Dialog()
            dialog.ok(config.appName, "Kan dit programma niet afspelen.")
            logFile.critical("Could not playback the url", exc_info=True)
    
    #============================================================================== 
    def GetImageLocation(self, image):
        """ NOT USER EDITABLE
            check if image is present in skin-folder. If so, use that one, of not,
            us the local one
        """
        if image == "":
            return ""
        if not os.path.exists(os.path.join(config.rootDir,"resources","skins", config.skinFolder, "media", image)):
            image = os.path.join(config.rootDir, "channels", self.__module__.replace("chn_", ""), image)
        return image
    
    #===============================================================================
    def CacheThumb(self, remoteImage):
        """ NOT USER EDITABLE
        Caches an image. Before calling, set the thumb to noImage in the channel
        """
        logFile.debug("Going to cache %s", remoteImage)
            
        if remoteImage == "":
            return self.noImage
        
        if remoteImage.find(":") < 2:
            return remoteImage
        
        logFile.debug("Caching url=%s", remoteImage)
        thumb = ""
        
        # get image
        localImageName = common.DoRegexFindAll('/([^/]*)$', remoteImage)[-1]
        # correct for fatx
        localImageName = uriHandler.CorrectFileName(localImageName)
        
        localCompletePath = os.path.join(config.cacheDir, localImageName)
        try:
            if os.path.exists(localCompletePath): #check cache
                    thumb = localCompletePath
            else: #  save them in cache folder
                    logFile.debug("Downloading thumb. Filename=%s", localImageName)
                    thumb = uriHandler.Download(remoteImage, localImageName, folder=config.cacheDir, pb=False)
        except:
            logFile.error("Error opening thumbfile!", exc_info=True)
            return self.noImage            
        
        return thumb    
    
    #===============================================================================
    # Default methods
    #===============================================================================
    def __str__(self):
        if self.channelCode == "":
            return "%s  [%s]" % (self.channelName, self.guid)
        else:
            return "%s (%s) [%s]" % (self.channelName, self.channelCode, self.guid)
    
    #============================================================================== 
    def __eq__(self, other):
        """
            Compares to channel objects
        """
        if other == None:
            return False
        
        return self.guid == other.guid
    
    #===============================================================================
    # properties        
    #===============================================================================
    def IsOutOfDate(self):
        """ NOT USER EDITABLE
            Compare the maxVersion of the channel (so the maximum version of XOT
            for which the channel was tested) against the current version of XOT.
            If the currentversion is higher, don't load the channel.
        """
        maxVersionSplit = common.DoRegexFindAll('^(\d{1,3})\.(\d{1,3})\.(\d{1,3})(([abAB])(\d{0,2}))*$', self.maxXotVersion)[0];
        xotVersionSplit = common.DoRegexFindAll('^(\d{1,3})\.(\d{1,3})\.(\d{1,3})(([abAB])(\d{0,2}))*$', config.version)[0];
        versions = (maxVersionSplit, xotVersionSplit)
        intVersions = []
        
        for version in versions:
            tmpVersion = "%s%s%s" % (version[0].rjust(3, '0'), version[1].rjust(3, '0'), version[2].rjust(3, '0'))
            # now the last part will be for the beta/alpha counting. Therefore we assume that if no beta/alpa is present
            # the last 3 digits are 999. If they are presents the digits are between 0-998
            if version[4]!="":
                if version[4]=='a':
                    tmpVersion = "%s%s" % (tmpVersion, "1")
                elif version[4]=='b':
                    tmpVersion = "%s%s" % (tmpVersion, "2")
                tmpVersion = "%s%s" % (tmpVersion, version[5].rjust(3, '0')) 
            else:
                tmpVersion = "%s99" % (tmpVersion)
            intVersions.append(tmpVersion)
                    
        if intVersions[0] < intVersions[1]:
            logFile.warning("%s has maxVersion %s and is to old for XOT version %s. (maxXot=%s, currentXot=%s)", self.channelName, self.maxXotVersion, config.version, intVersions[0], intVersions[1])
            return True
        else:
            return False 
    
    # register the property     
    OutOfDate = property(IsOutOfDate, doc='Check if channel is out of date')
