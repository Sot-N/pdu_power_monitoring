#! /usr/bin/python3
import argparse
import threading
from threading import Thread
import multiprocessing
import time
from snmp_pdu import snmp_reader_V2
from snmp_pdu import snmp_reader_V3
from pdu_influxdb import influxdb_writer
import influxdb_config as config
from configparser import ConfigParser
import os
import os.path
import shutil
import configparser
import logging


__author__      = "Sotirios Nikas"


if __name__ == "__main__":

#Read command line options

    parser = argparse.ArgumentParser(description="PDU data acquisition tool")

    parser._action_groups.pop()

    required = parser.add_argument_group('required arguments')

    optional = parser.add_argument_group('optional arguments')

    required.add_argument("snmp", metavar = "snmp configuration file", help = "Parse the snmp config file into program")

    required.add_argument("-labels", "-l", nargs='+', help = "Obtain labels of PDUs by providing the ip address, please use human readable names.", required = True)

    required.add_argument("-version", "-v", choices=['1','2','3'], help = "Determine snmp version to be used, please consider the corresponding configuration file working with the given version", required = True)

    required.add_argument("-mode", "-m", choices=['Parallel','Serial'], help = "Determine the data acquisition way, parallel or serial", required=True)

    optional.add_argument("-libPDU", "-lbP", choices=['Threading','Multiprocessing'], help = "Determine the used library for the parallel mode in PDU level")

    required.add_argument("-iterations", "-i", help = "Determine the number of iterations to issue the snmp command and save the timing into a file. When you do not use this option then perpetual monitoring is enabled")

    optional.add_argument("-libNODE", "-lbN", choices=['Multiprocessing'], help = "Determine the used library for the parallel mode in further NODE level, in that case the snmpget command is used")


options = parser.parse_args()


if options.mode == "Parallel" and options.libPDU == None:
   print("Parallel mode requires to use one of the given libraries by adding -lb <library>")
   exit(0) # Successful exit
elif options.mode == "Serial" and options.libPDU == None:
   options.libPDU = "no_library"    


if options.iterations == None:
   global_iterations = float('inf')
else:
   global_iterations = int(options.iterations)


# Enables parallel mode in node level
node = options.libNODE

if options.libNODE == None:
   options.libNODE = "no_library"


# Logging setup
log = logging.getLogger(__name__)
if config.debug:
    log = logging.getLogger(__name__)
    urllib3_logger = logging.getLogger('urllib3')
    urllib3_logger.setLevel(logging.CRITICAL)
    loglevel = logging.DEBUG
    logging.basicConfig(level=loglevel, format='%(asctime)s %(levelname)s: %(name)s: %(message)s')


# Reading configuration file
config_file = configparser.ConfigParser()
config_file.read(options.snmp)
log.debug("=================================================================================================")
log.debug("Configuration file %s:" %options.snmp)


if options.iterations != None:
    os.chdir("data")
    f = open("data_%s.txt" %(options.mode + "_" + options.libPDU + "_" + os.path.splitext(options.snmp)[0].split('/')[-1] + "_" + str(len(options.labels)) + "_" + options.libNODE + "_" + "pdus" ), 'w')
    os.chdir("..")
    log.debug("=================================================================================================")
    log.debug("Acquisition file: data_%s.txt" %(options.mode + "_" + options.libPDU + "_" + os.path.splitext(options.snmp)[0].split('/')[-1] + "_" + str(len(options.labels)) + "_" + options.libNODE + "_" + "pdus"))
    log.debug("=================================================================================================")
    log.debug("Acquisition iterations: %s "% options.iterations)


if options.labels:
    # Give the pdus from command line
    pdu_objects = options.labels
    log.debug("======================================== PDU ip =====================================================")
    for i in options.labels:
        log.debug("%s" %i)


    if options.version == "2":
        log.debug("=================================================================================================")
        log.debug("SNMP version: %s" %options.version)
        # Construct the snmp command for v2 to retrieve labels. Retrive information from the configuration file
        ### snmpV2 configurations ###
        version = config_file['snmpV2']['version']
        option = config_file['snmpV2']['option']
        rocommunity = config_file['snmpV2']['rocommunity']
        oid = config_file['snmpV2']['oid']

        # List of lists with all labels of all pdus
        pdu_label_list = []
        # List of objects created by snmp_reader class allowing to access snmp functions
        snmp_pdus = []
        for i in range(len(pdu_objects)):
            # labels for each pdu
            labels_per_pdu = []
            # Create a snmpV2 reader object for each pdu to obtain labels
            snmp_pdus.append(snmp_reader_V2(version, option, rocommunity, pdu_objects[i], oid, node))
            # Execute the snmp command for each pdu, and save the labels
            labels_per_pdu = snmp_pdus[i].receiveLabels()
            # Save the labels to list of list
            pdu_label_list.append(labels_per_pdu)

        # List of objects created by influxdb_writer class allowing to access influxdb database
        db_pdus = []
        for i in range(len(pdu_objects)):
            # Change the oid for the obtaining power information
            oid = 'lgpPduRcpEntryPwrOut'
            # Create database and save data
            # Link the objects of influxdb_writer with the existed objects of snmp_reader class for making sure correct labels 
            snmp_object = snmp_reader_V2(version, option, rocommunity, pdu_objects[i], oid, node)
            db_pdus.append(influxdb_writer(pdu_objects[i], snmp_object, pdu_label_list[i]))
            log.debug("============================================ LABELS =============================================")
            for j in pdu_label_list[i]:
                log.debug(j)


    elif options.version == "3":
        log.debug("=================================================================================================")
        log.debug("SNMP version: %s:" %options.version)
        # Construct the snmp command for v3 to retrieve labels. Retrieve information from the configuration file
        ### snmpV3 configurations ###
        version = config_file['snmpV3']['version']
        username_option = config_file['snmpV3']['username_option']
        username = config_file['snmpV3']['username']
        security_level_option = config_file['snmpV3']['security_level_option']
        security_level = config_file['snmpV3']['security_level']
        auth_protocol_option = config_file['snmpV3']['auth_protocol_option']
        auth_protocol = config_file['snmpV3']['auth_protocol']
        auth_protocol_passphrase_option = config_file['snmpV3']['auth_protocol_passphrase_option']
        auth_protocol_passphrase = config_file['snmpV3']['auth_protocol_passphrase']
        priv_protocol_option = config_file['snmpV3']['priv_protocol_option']
        priv_protocol = config_file['snmpV3']['priv_protocol']
        priv_protocol_passphrase_option = config_file['snmpV3']['priv_protocol_passphrase_option']
        priv_protocol_passphrase = config_file['snmpV3']['priv_protocol_passphrase']
        oid = config_file['snmpV3']['oid']


        # List of lists with all labels of all pdus
        pdu_label_list = []
        # list of objects created by snmp_reader class allowing to access snmp functions
        snmp_pdus = []
        for i in range(len(pdu_objects)):
            # labels for each pdu
            labels_per_pdu = []
            # Create a snmp reader object for each pdu to obtain labels
            snmp_pdus.append(snmp_reader_V3(version, username_option, username, security_level_option, security_level, auth_protocol_option, auth_protocol, auth_protocol_passphrase_option, auth_protocol_passphrase, priv_protocol_option, priv_protocol, priv_protocol_passphrase_option, priv_protocol_passphrase, pdu_objects[i], oid, node))
            # Execute the snmp command for each pdu, and save the labels
            labels_per_pdu = snmp_pdus[i].receiveLabels()
            # Save the labels to list of list
            pdu_label_list.append(labels_per_pdu)

        # List of objects created by influxdb_writer class allowing to access influxdb database
        db_pdus = []
        for i in range(len(pdu_objects)):
            # Change the oid for the obtaining power information
            oid = 'lgpPduRcpEntryPwrOut'
            # Create database and save data
            # Link the objects of influxdb_writer with the existed objects of snmp_reader class for making sure correct labels 
            snmp_object = snmp_reader_V3(version, username_option, username, security_level_option, security_level, auth_protocol_option, auth_protocol, auth_protocol_passphrase_option, auth_protocol_passphrase, priv_protocol_option, priv_protocol, priv_protocol_passphrase_option, priv_protocol_passphrase, pdu_objects[i], oid, node)
            db_pdus.append(influxdb_writer(pdu_objects[i], snmp_object, pdu_label_list[i]))
            log.debug("============================================ LABELS =============================================")
            for j in pdu_label_list[i]:
                log.debug(j)


    # Determine the local counter
    local_iterations = 0
    if (options.mode == "Parallel"):
        log.debug("=================================================================================================")
        log.debug("Parallel mode enabled")
        if (options.libPDU == "Multiprocessing"):
            log.debug("=================================================================================================")
            log.debug("Multiprocessing library enabled")
            while (local_iterations < global_iterations):
                log.debug("====================================== LABELS = VALUES ===========================================")
                jobs = []
                start = time.time()
                for i in range(0, len(db_pdus)):
                    process = multiprocessing.Process(target=db_pdus[i].write_snmp_data)
                    jobs.append(process)
                for j in jobs:
                    j.start()
                for j in jobs:
                    j.join()
                end = time.time()
                elapsed = end - start
                # Measure the elapsed time for one for loop over all the found objects
                if options.iterations != None:
                   f.write(str(elapsed) + '\n')
                   local_iterations += 1
        else:
            log.debug("=================================================================================================")
            log.debug("Threading library enabled")
            while (local_iterations < global_iterations):
                log.debug("====================================== LABELS = VALUES ===========================================")
                threads = []
                start = time.time()
                for i in range(len(db_pdus)):
                    t = threading.Thread(target=db_pdus[i].write_snmp_data)
                    t.start()
                    threads.append(t)
                for t in threads:
                    t.join()
                end = time.time()
                elapsed = end - start
                # Measure the elapsed time for one for loop over all the found objects
                if options.iterations != None:
                    f.write(str(elapsed) + '\n')
                    local_iterations += 1
        if options.iterations != None:
            f.close()
    else:
        log.debug("=================================================================================================")
        log.debug("Serial mode enabled")
        while (local_iterations < global_iterations):
            log.debug("====================================== LABELS = VALUES ===========================================")
            start = time.time()
            for i in range(len(db_pdus)):
                db_pdus[i].write_snmp_data()
            end = time.time()
            elapsed = end - start
            if options.iterations != None:
                f.write(str(elapsed) + '\n')
                local_iterations += 1
        if options.iterations != None:
            f.close()
