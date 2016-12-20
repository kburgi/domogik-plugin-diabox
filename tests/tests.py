#!/usr/bin/python
# -*- coding: utf-8 -*-

from domogik.xpl.common.plugin import XplPlugin
from domogik.tests.common.plugintestcase import PluginTestCase
from domogik.tests.common.testplugin import TestPlugin
from domogik.tests.common.testdevice import TestDevice
from domogik.tests.common.testsensor import TestSensor
from domogik.common.utils import get_sanitized_hostname
from datetime import datetime
import unittest
import sys
import os
import traceback

class DiaboxTestCase(PluginTestCase):

    def test_0100_checkThatWeGetDataFromStation(self):
        """ check if we receive xpl msg with a rainrate value from a diabox station

            Note that we cannot check "value" which change all the time (live weather conditions...)

            However, we can try to catch an xpl msg with the rainrate value... wich the hope that 
            between the 2 requests, the data will not change :-P

            Example : Phare Du Minou (which has dbx_dev_type = diabox.minou  [see info.json])
            
            xpl-stat
            {
                hop=1
                source=
                target=
            }
            sensor.basic
            {
                device=dbx_Minou
                type=rainrate
                current=0.0
            }
            
            => possible type : temperature, pressure, windspeed, winddirection, humidity, rainrate
        """
        global diabox_json_dev_type_id  # dict with ["json_dev_id"] = { "dev_id" : 000, "ref_xpl": xpl_uuid }
        global cur_jdtid
        global interval

        dev_param = diabox_json_dev_type_id[cur_jdtid]
        dev_id = dev_param["dev_id"]
        dev_xpl = dev_param["ref_xpl"]

        # test 
        print(u"Device tested = {0}".format(cur_jdtid))
        print(u"Device id = {0}".format(diabox_json_dev_type_id[cur_jdtid]))
        print(u"Check that we receive an xpl msg with rainrate value from {} diabox station.".format(cur_jdtid))
        
        self.assertTrue(self.wait_for_xpl(xpltype = "xpl-stat",
                                          xplschema = "sensor.basic",
                                          xplsource = "domogik-{0}.{1}".format(self.name, get_sanitized_hostname()),
                                          data = {"type" : "rainrate",
                                                  "device" : dev_xpl,
                                                  "current" : "0.0"},
                                          timeout = 70))

        cur_xpl_rcv_val = self.xpl_data.data['current']
        print(u"Xpl receive value : {}".format(cur_xpl_rcv_val))        

        print(u"Check that the value of the xPL message has been inserted in database")
        #print(u"[debug perso] dev_id={}  dev_xpl={}".format(dev_id, dev_xpl))
        sensor = TestSensor(dev_id, "current_rain_rate")
        print(sensor.get_last_value())
        self.assertTrue(sensor.get_last_value()[1] == cur_xpl_rcv_val)


if __name__ == "__main__":

    test_folder = os.path.dirname(os.path.realpath(__file__))

    # the list of diabox tested    key = dev_type_id and value = id for created device
    diabox_json_dev_type_id = { "diabox.minou" : 0
                              }
    interval = 60

    ### configuration

    # set up the xpl features
    xpl_plugin = XplPlugin(name = 'test', 
                           daemonize = False, 
                           parser = None, 
                           nohub = True,
                           test  = True)

    # set up the plugin name
    name = "diabox"

    # set up the configuration of the plugin
    # configuration is done in test_0010_configure_the_plugin with the cfg content
    # notice that the old configuration is deleted before
    cfg = { 'configured' : True}

    ### start tests

    # load the test devices class
    td = TestDevice()

    for cur_jdtid in diabox_json_dev_type_id:

        # xpl param config => xpl unique reference of the created device
        refName="ref"+cur_jdtid
        
        # delete existing devices for this plugin on this host
        client_id = "{0}-{1}.{2}".format("plugin", name, get_sanitized_hostname())
        try:
            td.del_devices_by_client(client_id)
        except: 
            print(u"Error while deleting all the test device for the client id '{0}' : {1}".format(client_id, traceback.format_exc()))
            sys.exit(1)

        # create a test device
        try:
            params = td.get_params(client_id, cur_jdtid)
       
            print("DEV_ID={0}".format(cur_jdtid))
            # fill in the params
            params["device_type"] = cur_jdtid
            params["name"] = "test_device_diabox_{0}_".format(cur_jdtid)
            params["reference"] = "reference"
            params["description"] = "description"
            # global params
            pass # there are no global params for this plugin
            # xpl params
            # usually we configure the xpl parameters. In this device case, we can have multiple addresses
            # so the parameters are configured on xpl_stats level
            for the_param in params['global']:
                if the_param['key'] == "interval":
                    the_param['value'] = interval           #cannot be <60
            for the_param in params['xpl']:
                if the_param['key'] == "device":
                    the_param['value'] = refName
            # create
            device_id = td.create_device(params)['id']
            diabox_json_dev_type_id[cur_jdtid] = { "dev_id" :device_id, "ref_xpl" : refName }


        except:
            print(u"Error while creating the test devices : {0}".format(traceback.format_exc()))
            sys.exit(1)

        
        ### prepare and run the test suite
        suite = unittest.TestSuite()
        # check domogik is running, configure the plugin
        suite.addTest(DiaboxTestCase("test_0001_domogik_is_running", xpl_plugin, name, cfg))
        suite.addTest(DiaboxTestCase("test_0010_configure_the_plugin", xpl_plugin, name, cfg))
        
        # start the plugin
        suite.addTest(DiaboxTestCase("test_0050_start_the_plugin", xpl_plugin, name, cfg))

        # do the specific plugin tests
        suite.addTest(DiaboxTestCase("test_0100_checkThatWeGetDataFromStation", xpl_plugin, name, cfg))


    # do some tests comon to all the plugins
    #suite.addTest(PingTestCase("test_9900_hbeat", xpl_plugin, name, cfg))
    suite.addTest(DiaboxTestCase("test_9990_stop_the_plugin", xpl_plugin, name, cfg))
    
    # quit
    res = unittest.TextTestRunner().run(suite)
    if res.wasSuccessful() == True:
        rc = 0   # tests are ok so the shell return code is 0
    else:
        rc = 1   # tests are ok so the shell return code is != 0
    xpl_plugin.force_leave(return_code = rc)


