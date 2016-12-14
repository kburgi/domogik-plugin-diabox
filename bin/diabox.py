#!/usr/bin/python
# -*- coding: utf-8 -*-

""" This file is part of B{Domogik} project (U{http://www.domogik.org}).

License
=======

B{Domogik} is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

B{Domogik} is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Domogik. If not, see U{http://www.gnu.org/licenses}.

Plugin purpose
==============

Fetch live weather data from diabox station
See http://data.diabox.com/ for more informations

Implements
==========

This plugin implements the interface between a diabox station
and domogik db.

@author: kbu <kbu@kbulabs.fr>
@copyright: (C) 2007-2016 Domogik project
@license: GPL(v3)
@organization: Domogik
"""

from domogik.xpl.common.xplmessage import XplMessage
from domogik.xpl.common.plugin import XplPlugin

from domogik_packages.plugin_diabox.lib.diaboxlib import DiaboxLib

import threading
import traceback

class DiaboxManager(XplPlugin):
    """ Bin part of the diabox plugin """

    def __init__(self):
        """  Init plugin
        """
        XplPlugin.__init__(self, name='diabox')

        # check if the plugin is configured. If not, this will stop the plugin and log an error
        #if not self.check_configured():
        #    return
        
        # if there is no station configured, the plugin has no interest...
        self.devices = self.get_device_list(quit_if_no_device = True)

        # one thread per diabox station
        threads = {}
        for dev in self.devices:
            try:
                self.log.debug("--------- INIT DEVICE \"{}\" ------------------".format(dev['name']))
                
                # need to now which diabox station id for current "dev"
                # => it's used to catch right diabox variable in lib/diaboxconfig.py
                self.log.info("Init of the station diabox type => \"{}\"".format(dev['device_type_id']))
                self.log.debug("[dbx_type={}] Diabox description \"{}\"".format(dev['device_type_id'], dev['description']))

                # getting the xpl_uid (xpl unique identifier)
                feat = dev['xpl_stats'].iterkeys().next()
                xpl_uid = self.get_parameter_for_feature(dev,"xpl_stats",feat,"device")
                self.log.debug("[dbx_type={}] Device xpl_uid =  \"{}\"".format(dev['device_type_id'], xpl_uid))
                
                # listing whole feature for current station (from info.json)
                self.log.info("[dbx_type={}] The feature for this station are : ".format(dev['device_type_id']))
                for cur_feat in dev['xpl_stats']:
                    self.log.info("[dbx_type={}]\tfeat : {}".format(dev['device_type_id'], cur_feat))

                dbx_domo_id=dev['id']
                refresh_interval = self.get_parameter(dev,"interval")
                if refresh_interval == None or refresh_interval < 60 :
                    self.log.error("[dbx_type={}] Interval \"{}\" is invalid for device \"{}\"".format(dev['device_type_id'], refresh_interval, dev['name']))                
                    self.log.error("[dbx_type={}] The interval MUST be greater than 60 seconds to prevent overloading on server side".format(dev['device_type_id']))
                    return
                self.log.debug("[dbx_type={}] Refresh interval configured = \"{}\" seconds".format(dev['device_type_id'], dev['name'], refresh_interval))

                #self.log.debug("[dbx_type={}] ------- Calling manager => DiaboxLib  -------------".format(dev['device_type_id']))
                # note : device_type_id = diabox.minou / diabox.wrach / etc => required for diaboxconfig module
                self._diabox_manager = DiaboxLib(self.log, self.send_xpl, self.get_stop(), dev['device_type_id'], dev["id"], refresh_interval, xpl_uid)
                self.add_stop_cb(self._diabox_manager.stop)

                # checking if this diabox is ready to work
                if self._diabox_manager.isConfigured == False:
                    self.log.error("[dbx_type={}] Something went wrent wrong during init of the DiaboxManager !!  => skip this device !".format(dev['device_type_id'])) 
                    continue;

                # creating thread for current station. No argument needed.
                thr_name = "diabox_{}".format(dev['name'])
                self.log.info("[dbx_type={}][Starting thread {}] Start fetching diabox data".format(dev['device_type_id'], thr_name))
                threads[thr_name] = threading.Thread(None,
                                                    self._diabox_manager.get_diabox_data,
                                                    thr_name,
                                                    (),
                                                    {})
                threads[thr_name].start()
                self.register_thread(threads[thr_name])
            except:
                self.log.error("[bin/diabox.py] Exception spotted while creating threads !!")
                self.log.error("{0}".format(traceback.format_exc()))
                self.log.error("[bin/diabox.py][device_type_id={}] Leaving this diabox thread for this device !".format(dev['device-type_id']))
                return  

        self.log.info("Plugin \"diabox\" ready :)")
        self.ready()

    
    def send_xpl(self, domo_dev_id, xpl_uid, dbx_station_name, sensor_name, sensor_type, sensor_value):
        """ send xPL on the network """

        # building xPl msg
        msg = XplMessage()
        msg.set_type("xpl-stat")
        msg.set_schema("sensor.basic")
        msg.add_data({"device" : xpl_uid})
        msg.add_data({"type" : sensor_type })
        msg.add_data({"current" : sensor_value})

        try:
            self.log.debug("Now trying to send the xpl msg...")
            self.myxpl.send(msg)
        except XplMessageError: 
            self.log.debug(u"Bad xpl message to send. Xpl message is : {0}".format(str(msg)))
            pass



if __name__ == "__main__":
    DiaboxManager()


