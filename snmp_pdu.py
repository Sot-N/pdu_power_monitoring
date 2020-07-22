import re
from subprocess import Popen, PIPE
import os
from datetime import datetime
import subprocess
import time
import itertools
import time
import influxdb_config as config
import multiprocessing
import threading
from queue import Queue

class snmp_reader_V2:
    

    client = None


    def __init__(self, snmp_version, snmp_option, rocommunity, ip, oid, node_parallel):
        self.wattage_list = []
        command = ['snmpwalk', snmp_version, snmp_option, rocommunity, ip, oid]
        self.snmp_command = list(filter(None, command))

        command2 = ['snmpget', snmp_version, snmp_option, rocommunity, '-Oqv', ip,]
        self.snmp_command2 = list(filter(None, command2))
        self.node = node_parallel


    def snmp_command_function(self, L, oid1, oid2):
        tmp_command = []
        watt = []
        tmp_command = list(self.snmp_command2)
        oid = 'lgpPduRcpEntryPwrOut.1.' + str(oid1) + '.' + str(oid2)
        tmp_command.append(oid)
        #print(tmp_command)
        p = Popen(tmp_command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, err = p.communicate(b'input data that is passed to stdin of subprocess')
        rc = p.returncode
        string_output = output.decode()
        string_output = string_output.split("W")[0]
        L[(((oid1-1) * 8) + (oid2-1))] = string_output


    def receiveLabels(self):
        self.label_list = []
        if config.virtual_data:
            output = "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.1.1 = STRING: Cascade-031 \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.1.2 = STRING: Cascade-032 \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.1.3 = STRING: Cascade-033 \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.1.4 = STRING: Cascade-034 \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.1.5 = STRING: Cascade-035 \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.1.6 = STRING: - \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.1.7 = STRING: - \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.1.8 = STRING: - \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.2.1 = STRING: Cascade-036 \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.2.2 = STRING: Cascade-037 \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.2.3 = STRING: Cascade-038 \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.2.4 = STRING: Cascade-039 \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.2.5 = STRING: Cascade-040 \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.2.6 = STRING: - \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.2.7 = STRING: - \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.2.8 = STRING: - \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.3.1 = STRING: Cascade-041 \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.3.2 = STRING: Cascade-042 \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.3.3 = STRING: Cascade-043 \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.3.4 = STRING: Cascade-044 \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.3.5 = STRING: Cascade-045 \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.3.6 = STRING: - \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.3.7 = STRING: - \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.3.8 = STRING: -"
            for line in output.splitlines():
                self.label_list.append(line.split(':')[-1])
        else:
            p = Popen(self.snmp_command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            output, err = p.communicate(b'input data that is passed to stdin of subprocess')
            rc = p.returncode
            string_output = output.decode()
            for line in string_output.splitlines():
                self.label_list.append(str(line).split(':')[-1])
        return self.label_list


    def sendCommand(self):
        self.wattage_list = []       
        if config.virtual_data:
            output = "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.1.1 = Gauge32: 0 Watt \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.1.2 = Gauge32: 10 Watt \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.1.3 = Gauge32: 20 Watt \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.1.4 = Gauge32: 30 Watt \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.1.5 = Gauge32: 40 Watt \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.1.6 = Gauge32: 50 Watt \n "\
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.1.7 = Gauge32: 60 Watt \n "\
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.1.8 = Gauge32: 70 Watt \n "\
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.2.1 = Gauge32: 80 Watt \n "\
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.2.2 = Gauge32: 90 Watt \n "\
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.2.3 = Gauge32: 10 Watt \n "\
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.2.4 = Gauge32: 120 Watt \n "\
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.2.5 = Gauge32: 130 Watt \n "\
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.2.6 = Gauge32: 140 Watt \n "\
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.2.7 = Gauge32: 150 Watt \n "\
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.2.8 = Gauge32: 60 Watt \n "\
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.3.1 = Gauge32: 710 Watt \n "\
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.3.2 = Gauge32: 50 Watt \n "\
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.3.3 = Gauge32: 30 Watt \n "\
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.3.4 = Gauge32: 50 Watt \n "\
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.3.5 = Gauge32: 30 Watt \n "\
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.3.6 = Gauge32: 154 Watt \n "\
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.3.7 = Gauge32: 30 Watt \n "\
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.3.8 = Gauge32: 10 Watt"
            for line in output.splitlines():
                power = self.wattage_list.append(int(str(line).split(':')[-1][1:-5]))
        else:
            if (self.node == "Multiprocessing"):
                manager = multiprocessing.Manager()
                L = manager.list(range(24))
                jobs = []
                for i in range(1, 4):
                    for j in range(1, 9):
                        process = multiprocessing.Process(target=self.snmp_command_function, args =(L ,i, j))
                        jobs.append(process)
                for k in jobs:
                    k.start()
                for k in jobs:
                    k.join()
                self.wattage_list = L
            else:
                p = Popen(self.snmp_command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                output, err = p.communicate(b'input data that is passed to stdin of subprocess')
                rc = p.returncode
                string_output = output.decode()
                for line in string_output.splitlines():
                    self.wattage_list.append(str(line).split(':')[-1][1:-5])
        return self.wattage_list


class snmp_reader_V3:

    
    client = None


    def __init__(self, version, username_option, username, security_level_option, security_level, auth_protocol_option, auth_protocol, auth_protocol_passphrase_option, auth_protocol_passphrase, priv_protocol_option, priv_protocol, priv_protocol_passphrase_option, priv_protocol_passphrase, ip, oid, node_parallel):
        self.wattage_list = []
        command = ['snmpwalk', version, username_option, username, security_level_option, security_level, auth_protocol_option, auth_protocol, auth_protocol_passphrase_option, auth_protocol_passphrase, priv_protocol_option, priv_protocol, priv_protocol_passphrase_option, priv_protocol_passphrase, ip, oid]
        self.snmp_command = list(filter(None, command))       

        command2 = ['snmpget', version, username_option, username, security_level_option, security_level, auth_protocol_option, auth_protocol, auth_protocol_passphrase_option, auth_protocol_passphrase, priv_protocol_option, priv_protocol, priv_protocol_passphrase_option, priv_protocol_passphrase, '-Oqv', ip]
        self.snmp_command2 = list(filter(None, command2))
        self.node = node_parallel


    def snmp_command_function(self, L, oid1, oid2):
        tmp_command = []
        watt = []
        tmp_command = list(self.snmp_command2)
        oid = 'lgpPduRcpEntryPwrOut.1.' + str(oid1) + '.' + str(oid2)
        tmp_command.append(oid)
        #print(tmp_command)
        p = Popen(tmp_command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, err = p.communicate(b'input data that is passed to stdin of subprocess')
        rc = p.returncode
        string_output = output.decode()
        string_output = string_output.split("W")[0]
        L[(((oid1-1) * 8) + (oid2-1))] = string_output

 
    def receiveLabels(self):
        self.label_list = []
        if config.virtual_data:
            output = "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.1.1 = STRING: Cascade-031 \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.1.2 = STRING: Cascade-032 \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.1.3 = STRING: Cascade-033 \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.1.4 = STRING: Cascade-034 \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.1.5 = STRING: Cascade-035 \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.1.6 = STRING: - \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.1.7 = STRING: - \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.1.8 = STRING: - \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.2.1 = STRING: Cascade-036 \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.2.2 = STRING: Cascade-037 \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.2.3 = STRING: Cascade-038 \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.2.4 = STRING: Cascade-039 \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.2.5 = STRING: Cascade-040 \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.2.6 = STRING: - \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.2.7 = STRING: - \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.2.8 = STRING: - \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.3.1 = STRING: Cascade-041 \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.3.2 = STRING: Cascade-042 \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.3.3 = STRING: Cascade-043 \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.3.4 = STRING: Cascade-044 \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.3.5 = STRING: Cascade-045 \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.3.6 = STRING: - \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.3.7 = STRING: - \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryUsrLabel.1.3.8 = STRING: -"
            for line in output.splitlines():
                self.label_list.append(line.split(':')[-1])
        else:
            p = Popen(self.snmp_command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            output, err = p.communicate(b'input data that is passed to stdin of subprocess')
            rc = p.returncode
            string_output = output.decode()
            for line in string_output.splitlines():
                self.label_list.append(str(line).split(':')[-1])
        return self.label_list
    

    def sendCommand(self):
        self.wattage_list = []       
        if config.virtual_data:
            output = "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.1.1 = Gauge32: 0 Watt \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.1.2 = Gauge32: 10 Watt \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.1.3 = Gauge32: 20 Watt \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.1.4 = Gauge32: 30 Watt \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.1.5 = Gauge32: 40 Watt \n " \
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.1.6 = Gauge32: 50 Watt \n "\
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.1.7 = Gauge32: 60 Watt \n "\
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.1.8 = Gauge32: 70 Watt \n "\
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.2.1 = Gauge32: 80 Watt \n "\
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.2.2 = Gauge32: 90 Watt \n "\
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.2.3 = Gauge32: 10 Watt \n "\
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.2.4 = Gauge32: 120 Watt \n "\
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.2.5 = Gauge32: 130 Watt \n "\
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.2.6 = Gauge32: 140 Watt \n "\
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.2.7 = Gauge32: 150 Watt \n "\
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.2.8 = Gauge32: 60 Watt \n "\
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.3.1 = Gauge32: 710 Watt \n "\
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.3.2 = Gauge32: 50 Watt \n "\
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.3.3 = Gauge32: 30 Watt \n "\
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.3.4 = Gauge32: 50 Watt \n "\
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.3.5 = Gauge32: 30 Watt \n "\
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.3.6 = Gauge32: 154 Watt \n "\
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.3.7 = Gauge32: 30 Watt \n "\
                     "LIEBERT-GP-PDU-MIB::lgpPduRcpEntryPwrOut.1.3.8 = Gauge32: 10 Watt"
            for line in output.splitlines():
                power = self.wattage_list.append(int(str(line).split(':')[-1][1:-5]))
        else:
            if (self.node == "Multiprocessing"):
                manager = multiprocessing.Manager()
                L = manager.list(range(24))
                jobs = []
                for i in range(1, 4):
                    for j in range(1, 9):
                        process = multiprocessing.Process(target=self.snmp_command_function, args =(L ,i, j))
                        jobs.append(process)
                for k in jobs:
                    k.start()
                for k in jobs:
                    k.join()
                self.wattage_list = L
            else:
                p = Popen(self.snmp_command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                output, err = p.communicate(b'input data that is passed to stdin of subprocess')
                rc = p.returncode
                string_output = output.decode()
                for line in string_output.splitlines():
                    self.wattage_list.append((str(line).split(':')[-1][1:-5]))
        return self.wattage_list
