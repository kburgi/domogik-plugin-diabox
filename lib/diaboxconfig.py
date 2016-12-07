#!/usr/bin/python
# -*-coding:Utf-8 -*

# here are variable used in diabox website

minou={}
minou["dev_type"]="diabox.minou"  #domogik json id
minou["name"]="minou"
minou["id"]="11"
minou["temperature"]="minou_d_temperature"
minou["pressure"]="minou_d_pressure"
minou["wind_speed_kts"]="minou_d_wind_rt"
minou["wind_direction"]="minou_d_wind_rt"     #it's the same var
minou["humidity"]="minou_d_humidity"
minou["rain_rate"]="minou_d_rain"

wrach={}
wrach["dev_type"]="diabox.wrach"  #domogik json id
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

    def __init__(self, dev_type, domo_log):
        self.domo_log = domo_log
        
        #get the config of the diabox station
        cfg = self.get_dbx_config(dev_type)
        if cfg == None:
            self.isValid=False
        else:
            self.station_name = cfg["name"]
            self.station_id = cfg["id"]   # This is remote id, on diabox website !
            self.url_temperature = self.get_remote_url(cfg["id"], cfg["temperature"])
            self.url_pressure = self.get_remote_url(cfg["id"], cfg["pressure"])
            self.url_wind_speed = self.get_remote_url(cfg["id"], cfg["wind_speed_kts"])
            self.url_wind_drection = self.get_remote_url(cfg["id"], cfg["wind_direction"])
            self.url_humidity = self.get_remote_url(cfg["id"], cfg["humidity"])
            self.url_rain_rate = self.get_remote_url(cfg["id"], cfg["rain_rate"])
            self.isValid=True

    def get_dbx_config(self, dev_type):
        """ Iteration over list_diabox to get config for dev_type (diabox.minou / diabox.wrach / ...) """
        for dbx in list_diabox:
            if dev_type == dbx["dev_type"]:
                self.domo_log.info("Diabox config found ! It's the station \"{}\" ! :-)".format(dbx["name"]))
                #print "debug : diabox config found for dbx_name = {}".format(dbx["name"])
                return dbx
        self.domo_log.error("No Diabox config correspondance for diabox_type=\"{}\" !!!!".format(dev_type))
        return None

    def get_remote_url(self, dbx_remote_id, dbx_remote_sensor_var):
        url = "http://avelet.diabox.com/dataUpdate.php?dbx_id={}&dataName={}" \
               .format(dbx_remote_id, dbx_remote_sensor_var)
        #self.domo_log.debug("[DEBUG URL] get_url for diabox {} is :\n".format(self.station_name))
        #self.domo_log.debug("[DEBUG URL] : {}".format(url))
        return url


