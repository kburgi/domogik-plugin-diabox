#!/usr/bin/python2
# -*- coding: utf-8 -*-

import requests
import json
import datetime 

class TestZone ():
    
    dbx_name="Kermorvan"
    dbx_id="15"
    dataName="kermorvan_temperature"
    url = "http://avelet.diabox.com/dataUpdate.php?"+ \
          "dbx_id="+dbx_id+"&"+ \
          "dataName="+dataName
    #print url

    # fetch http diabox data
    r = requests.get(url)
    
    #check if http request is successful [code 200]
    if r.status_code != 200:
        print "HTTP REQUEST ERROR ! [return code : {}]".format(r.status_code)
        print "Diabox Name={} id={} dataName={}" \
                .format(dbx_name,dbx_id,dataName)
        quit()
    #else:
    #    print("HTTP REQUEST OK")

    #check that content is not null
    if r.headers["Content-Length"] == '0':
        print "ERROR : http response contains no data ! [\"Content-Length\"='0']"
        quit()

    #parse http response
    json_tab = json.loads(r.content)
    dbx_data = json_tab[0]

    print "Diabox \"{}\"".format(dbx_name)
    print "Date : {}".format(datetime.datetime.fromtimestamp(int(dbx_data["date"])).strftime('%Y-%m-%d %H:%M:%S'))
    print "Temp : {} °C".format(dbx_data["val"])









if __name__ == "__main__":
        TestZone()

