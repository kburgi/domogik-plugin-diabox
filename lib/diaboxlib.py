#!/usr/bin/python
# -*-coding:Utf-8 -*

import sys
import traceback

try:
    import pymysql
except Exception as e:
    print("--------------------------------------------")
    print("Unable to import pymsql module for Python !")
    print("Is it installed ? (pip install pymysql) ")
    print("--------------------------------------------")
    print(e)
    sys.exit(1)
    
try:
    import mysqlcfg as mysqlcfg
except Exception as e:
    print("--------------------------------------------")
    print("Unable to import mysqlcfg module !!")
    print("=> Check his presence in plugin lib folder ")
    print("--------------------------------------------")
    print(e)
    sys.exit(1)


class DiaboxLib():

    def __init__(self, log, callback, stop, mysql_host, mysql_db, mysql_table, mysql_login, mysql_pwd):
        """ Init TeleinfoMysqlObject
            @param log : log instance
            @param callback : callback
            @param stop : stop
            @param mysql_host : mysql hostname (string)
            @param mysql_db : mysql database name (string)
            @param mysql_table : mysql table with teleinfo data (string)
            @param mysql_login : mysql user name (string)
            @param mysql_pwd : mysql password (string)
        """
        
        #print "Init of class TeleinfoMysql()"
        self.log = log
        self._callback = callback # to send and xpl message
        self._stop = stop
        self.log.info("\n\t\t\t\t\t-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#")
        self.log.info("Init of plugin_\"timysql\"...")
        self.dbcfg =  mysqlcfg.MysqlConnectCfg(mysql_host, mysql_db, mysql_table, mysql_login, mysql_pwd)

        self.log.info("Testing MySQL connection...")        
        self.dbcon = self.mysql_connect()
        self.dbcon = self.mysql_disconnect()
        self.log.info("Testing MySQL connection -> success :-)")
        self.log.info("Init of plugin \"timysql\" -> completed")

    def __del__(self):
        """ Need to disconnect from Mysql when closing !"""
        #print "Destruct. of TeleinfoMysql()"
        if self.dbcon is not None:
            sys.log.info("Closing plugin_timysql, need to disconnect from MySQL")
            self.mysql_disconnect()
        else:
            sys.log.info("Closing plugin_timysql, plugin already disconnected from MySQL")        
        self.log.info("\n\t\t\t\t\t\t-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#\n")

    def stop(self):
        """ disconnect from mysql when plugin stop """
       #nothing to do 

    def mysql_connect(self):
        """ try to connect to mysql database with given config """

        #print "Testing MySQL connection..."
        #self.log.info("Trying to connect to MySQL...")
        try:
            db = pymysql.connect(self.dbcfg.host, self.dbcfg.login, self.dbcfg.pwd, self.dbcfg.dbname)
        except pymysql.err.OperationalError as emsg:
            #print "\n\n######### ERROR DURING CONNECTION TO MYSQL DB  #########"
            #print emsg
            self.log.error("!!!! Unable to connect to mysql database ! Check your config !!!!!")
            self.log.error(emsg)
            sys.exit(1)
        else:
            #print " success :-)"
            self.log.info("Trying to connect to MySQL -> SUCCESS :-)")
            return db


    def mysql_disconnect(self):
        """ Disconnect from mysql database """

        #print "Disconnecting from MYSQL server... "
        #self.log.info("Disconnecting from MySQL server... ")
        try:
            self.dbcon.close()
        except Exception as e:
            #print "\n\n!!! Error while disconnecting from DB server !!!"    
            self.log.error("\n\n!!! Error while disconnecting from DB server !!!")    
            print e
        else:
            #print "success :-)"
            self.log.info("Disconnecting from MySQL server -> SUCCESS  :-)")

    def fetch_last_teleinfo_line(self):
        """ Select the last entry in teleinfo table and return it """
        db_table = self.dbcfg.tablename
        nb_row = "1"

        sql = "SELECT * FROM " +  db_table + \
                " ORDER BY TIMESTAMP DESC LIMIT " + nb_row
        cursor = self.dbcon.cursor()

        msg = "Trying to fetch the " + nb_row + " last row(s) in " + \
                str(db_table) + " table..."
        #print "%s" % msg
        self.log.info(msg)                
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
        except Exception as e:
            #print "\n\n######### ERROR WHILE FETCHING DATA #########"
            self.log.error("\n\n######### ERROR WHILE FETCHING MySQL DATA #########")
            self.log.error(e)
            sys.exit(1)
        else:
            #print " success :-)"
            self.log.info("Fetching data from MySQL -> SUCCESS  :-)")
            return results

    def sql2dic(self, sql_frame):
        """ Convert 1 line of teleinfo data from MySQL into a dict """
        
        #print "sql2dic => --------- SQL_FRAME -------------"
        #print sql_frame
        try:
            timestamp = sql_frame[0]
            rec_date = sql_frame[1]
            rec_time = sql_frame[2]
            optarif = sql_frame[3]
            hchp = sql_frame[4]
            hchc = sql_frame[5]
            ptec = sql_frame[6]
            inst1 = sql_frame[7]
            imax1 = sql_frame[8]
            papp = sql_frame[9]
        except Exception as e:
            self.log.error("ERROR !! Have you tried to change the sql request or the sql table ???")
            self.log.error(e)
            #print e
            sys.exit(1)
        else:
            #put into a dict
            teleinfo = {}
            # teleinfo["timestamp"] = timestamp
            # teleinfo["recdate"] = rec_date
            # teleinfo["rectime"] = rec_time
            teleinfo["optarif"] = optarif
            teleinfo["hchp"] = hchp
            teleinfo["hchc"] = hchc
            teleinfo["ptec"] = ptec
            teleinfo["inst1"] = inst1
            teleinfo["imax1"] = imax1
            teleinfo["papp"] = papp
            return teleinfo

    #def test_callback(self):
    #    """ TEST FUNCTION => \"callback\" the last line of mysql entry """
    #    self.dbcon = self.mysql_connect()
    #    sql_res = self.fetch_last_teleinfo_line()
    #    self.dbcon = self.mysql_disconnect()
    #    
    #    frame = self.sql2dic(sql_res[0])  #only one sql line !!
    #    self.log.debug("Current teleinfo frame is :")
    #    self.log.debug(frame)
    #    self._callback(frame)

    def get_last_teleinfo(self, interval):
        """ get the last teleinfo line in database and push to xpl msg""" 
        while not self._stop.isSet():
            try:        
                self.dbcon = self.mysql_connect()
                sql_res = self.fetch_last_teleinfo_line()
                self.dbcon = self.mysql_disconnect()                
                frame = self.sql2dic(sql_res[0])  #only one sql line !!
                self.log.debug("Current teleinfo frame is :")
                self.log.debug(frame)
                self._callback(frame)
            except Exception as e :
                self.error.log("Error for getting the last teleinfo line : {0}".format(e))
            self._stop.wait(interval)



if __name__ == "__main__":
    print "Test execution timysql"
    t = TeleinfoMysql("0","0","0")
    sql_res = t.fetch_last_teleinfo_line()

    cur_row = sql_res[0]

    timestamp = cur_row[0]
    rec_date = cur_row[1]
    rec_time = cur_row[2]
    optarif = cur_row[3]
    hchp = cur_row[4]
    hchc = cur_row[5]
    ptec = cur_row[6]
    inst1 = cur_row[7]
    imax1 = cur_row[8]
    papp = cur_row[9]

    print("\n------------------- RESULT ------------------------")
    print("\tThe last rec_date is " + str(rec_date) + " " + str(rec_time))
    print("---------------------------------------------------\n")

    # Fetch a single row using fetchone() method.
    #data = cursor.fetchone()


    # disconnect from server
    del t
    #    mysql_disconnect(db)
    #db.close()


    sys.exit(0)
