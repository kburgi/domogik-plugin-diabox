#!/usr/bin/python3
# -*-coding:Utf-8 -*

class DiaboxConfig():
    """ List of all diabox config """

    def __init__(self):

    def __repr__(self):        
        isDbPwdSet = self._pwd is not ""
        msg = "db.host(\"{}\"), db_login(\"{}\", " + \
                "db_pwd_isSet(\"{}\"), db_dbname(\"{}\") " + \
                "db_tablename(\"{}\")" \
                .format(self._host, self._login, isDbPwdSet, self._dbname, self._tablename)
        return msg

