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
#sys.path.append(os.path.join(os.getcwd().replace(";",""),'libs'))
from pysqlite2 import dbapi2 as sqlite
import config
import common
import mediaitem

logFile = sys.modules['__main__'].globalLogFile

#===============================================================================
# Database Handler class
#===============================================================================
class DatabaseHandler:
    def __init__(self):
        """
            initialize the DB connection
        """
        self.xotDatabase = sqlite.connect(config.xotDbFile)
        self.__CheckDatabaseExistence()
        pass
    
    #===============================================================================
    #    Favorites Methodes
    #===============================================================================
    def AddFavorite(self, name, url, channel):
        logFile.debug("Adding favorite '%s' for channel '%s' with guid '%s' and url '%s'", name, channel.channelName, channel.guid, url)
        sql = u"INSERT INTO favorites (name, url, guid) VALUES(?, ?, ?)"
        params = (name, url, channel.guid)
        logFile.debug(params)
        self.__ExecuteNonQuery(sql, params=params)
    
    #==============================================================================
    def LoadFavorites(self, channel):
        logFile.debug("Loading favorites")
        items = []
        
        self.__UpgradeFrom310(channel)
        
        sql = "SELECT name, url FROM favorites WHERE guid='%s'" % (channel.guid)
        rows = self.__ExecuteQuery(sql)
        
        for row in rows:            
            item = mediaitem.MediaItem(row[0], row[1])
            items.append(item)
        
        return items
    
    #============================================================================== 
    def DeleteFavorites(self, name, url, channel):
        logFile.debug("Deleting favorite %s (%s)", name, url)
        query = "DELETE FROM favorites WHERE name=? AND url=? AND guid=?"
        self.__ExecuteNonQuery(query, commit=True, params=(name, url, channel.guid))
        return
    
    #============================================================================== 
    # Database creation 
    #============================================================================== 
    def __CheckDatabaseExistence(self):
        """
            Checks if the database exists, if not, it will be created.
        """
        sql = "PRAGMA table_info('favorites')"
        results = self.__ExecuteQuery(sql)
        
        # check if DB exists
        if len(results) < 1:
            self.__CreateDatabase()
            # reload the query
            results = self.__ExecuteQuery(sql)
        
        # Check for GUID column
        columnGuidExists = False
        for result in results:
            if result[1] == "guid":
                logFile.debug("Database: Guid column already present in favorites table.")
                columnGuidExists = True
                break
        if not (columnGuidExists):            
            logFile.debug("Database: Creating column guid")
            sql = "ALTER TABLE favorites ADD COLUMN guid"
            self.__ExecuteNonQuery(sql, commit=True)
        
    #============================================================================== 
    def __CreateDatabase(self):
        """
            Creates a functional database
        """
        logFile.info("Creating Database")
        sql = 'PRAGMA encoding = "UTF-16"'
        self.__ExecuteNonQuery(sql, True)
        sql = "CREATE TABLE favorites (channel string, name string, url string)"
        self.__ExecuteNonQuery(sql)
        sql = "CREATE TABLE settings (setting string, value string)"
        self.__ExecuteNonQuery(sql)
    
    #==============================================================================
    def __UpgradeFrom310(self, channel):
        sql = "UPDATE favorites SET guid='%s' where channel='%s'" % (channel.guid, channel.channelName)
        self.__ExecuteNonQuery(sql, commit=True)
                
    #===============================================================================
    # Query Methods 
    #===============================================================================
    def __ExecuteNonQuery(self, query, commit=True, params = []):
        """
            Executes and commits (if true) a sql statement to the database.
            Returns nothing, as it does not expect any results
        """
        
        # decode to unicode
        uParams = []
        for param in params:
            uParams.append(param.decode('iso-8859-1'))
        
        cursor = self.xotDatabase.cursor()
        if len(params) > 0:
            cursor.execute(query, uParams)
        else:
            cursor.execute(query)
        
        if commit:
            self.xotDatabase.commit()
    
    def __ExecuteQuery(self, query, commit=False, params = []):
        """
            Executs and commits (if true) a sql statement to the database.
            Returns a row-set
        """
        
        # decode to unicode
        uParams = []
        for param in params:
            uParams.append(param.decode('iso-8859-1'))
        
        cursor = self.xotDatabase.cursor()
        if len(params) > 0:
            cursor.execute(query, uParams)
        else:
            cursor.execute(query)        
        
        if commit:
            self.xotDatabase.commit()
        
        return cursor.fetchall()