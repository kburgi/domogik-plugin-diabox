#!/usr/bin/python
# -*-coding:Utf-8 -*

minou={}
minou["domo_id"]="diabox.minou"  #domogik json id
minou["name"]="minou"
minou["id"]="11"
minou["temperature"]="minou_d_temperature"
minou["pressure"]="minou_d_pressure"
minou["wind_speed_kts"]="minou_d_wind_rt"
minou["wind_direction"]="minou_d_wind_rt"     #it's the same var
minou["humidity"]="minou_d_humidity"
minou["rain_rate"]="minou_d_rain"

wrach={}
wrach["domo_id"]="diabox.wrach"  #domogik json id
wrach["name"]="wrach"
wrach["id"]="17"
wrach["temperature"]="wrach_temperature"
wrach["pressure"]="wrach_pressure"
wrach["wind_speed_kts"]="wrach_wind_rt"
wrach["wind_direction"]="wrach_wind_rt"     #it's the same var
wrach["humidity"]="wrach_humidity"
wrach["rain_rate"]="wrach_rainRate"

list_diabox = [ minou, wrach ]

        

class DiaboxConfig():
    """ List of all diabox config """

    def __init__(self, dbx_domo_id):
        
        cfg = self.get_dbx_config(dbx_domo_id)
        if cfg == None:
            self.isValid=False
        else:
            self.dbx_name = cfg["name"]
            self.rid = cfg["id"]   # """remote id"""
            self.url_temperature = self.get_remote_url(cfg["id"], cfg["temperature"])
            self.url_pressure = self.get_remote_url(cfg["id"], cfg["pressure"])
            self.url_wind_speed = self.get_remote_url(cfg["id"], cfg["wind_speed_kts"])
            self.url_wind_drection = self.get_remote_url(cfg["id"], cfg["wind_direction"])
            self.url_humidity = self.get_remote_url(cfg["id"], cfg["humidity"])
            self.url_rain_rate = self.get_remote_url(cfg["id"], cfg["rain_rate"])
            self.isValid=True


    def __repr__(self):        
        isDbPwdSet = self._pwd is not ""
        msg = "db.host(\"{}\"), db_login(\"{}\", " + \
                "db_pwd_isSet(\"{}\"), db_dbname(\"{}\") " + \
                "db_tablename(\"{}\")" \
                .format(self._host, self._login, isDbPwdSet, self._dbname, self._tablename)
        return msg

    def get_dbx_config(self, dbx_domo_id):
        """ Iteration over list_diabox to get config """
        for dbx in list_diabox:
            if dbx_domo_id == dbx["domo_id"]:
                print "DEBUG : diabox config found for dbx_name = {}".format(dbx["name"])
                return dbx
        print "ERROR : diabox config not found for diabox dbx_domo_id=\"{}\" !".format(dbx_domo_id)
        print "ERROR => Exiting"
        return 

    def get_remote_url(self, dbx_rid, dbx_remote_sensor_var):
        url = "http://avelet.diabox.com/dataUpdate.php?dbx_id={}&dataName={}" \
               .format(dbx_rid, dbx_remote_sensor_var)
        print "DEBUG : get_url for diabox {} is :\n".format(self._dbx_name)
        print "DEBUG : {}".format(url)
        return url


