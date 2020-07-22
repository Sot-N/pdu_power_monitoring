import logging
import influxdb_config as config
from influxdb import client as influxdb  # install influxdb library with pip
from datetime import timezone, datetime
from multiprocessing import Pool
import multiprocessing
from sys import exit
import multiprocessing



class influxdb_writer:

    def __init__(self, pdu, snmp_object, namings):
        self.snmp_pdu = snmp_object
        self.measurement_name = pdu
        self.namings = namings
        self.log = logging.getLogger(__name__)
        # Logging setup
        if config.debug:
            self.loglevel = logging.DEBUG
            self.logging = logging.basicConfig(level=self.loglevel, format='%(asctime)s %(levelname)s: %(name)s: %(message)s')

        # database connection
        self.log.debug("[info] \t\t connecting to database ...")
   
        try:
            self.db = influxdb.InfluxDBClient(config.Influxdb_ip, config.Influxdb_port, config.Influxdb_user,
                                              config.Influxdb_pass,
                                              config.Influxdb_used_database_name)
            self.log.debug("[success]\t ... database connection established")
        except:
            self.log.debug("[failure]\t ... database connection failed")
        try:
            self.db.create_database(config.Influxdb_used_database_name)
        except:
            self.log.debug("Database already existing - skipping creation")
    def format_for_influxdb(self, timestamp, pdu_port, result_wattage):
        return [{
            "measurement": self.measurement_name,
            "tags": {
                "pdu_port": pdu_port,
            },
            "time": timestamp,
            "fields": {
                "wattage": result_wattage,
            }
        }]


    def write_snmp_data(self):
        self.snmp_pdu.sendCommand()
        timestamp = datetime.now(timezone.utc).isoformat()
        try:
            for i in range(len(self.namings)):
                self.db.write_points(self.format_for_influxdb(timestamp,self.namings[i],self.snmp_pdu.wattage_list[i]))
                self.log.debug("PDU port: %s = %s" % (self.namings[i], self.snmp_pdu.wattage_list[i]))
        except TypeError:
                print("[failure] \t no value was given")
                #Check whether the number of namings are the same as the returned values. Some pdu have only 3 values(group A,B and C)
                if len(self.namings) != len(self.snmp_pdu.wattage_list):
                    self.log.debug("Possibly labels are not the same number as the power values, please check the snmp commands!")
                exit(0) # Successful exit
