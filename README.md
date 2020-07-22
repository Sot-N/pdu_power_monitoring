# Power monitoring
A flexible power monitoring tool of Emerson power unit distributions (PDUs) for HPC clusters.

## Requirements

1)Install the related Emerson PDU mibs. They are already located in the mibs folder.

2)Fill out the configuration files.

For snmpV2, the rocommunity and oid are needed

For snmpV3, depending on the version the following are needed:

  i)username

  ii)auth_protocol_passphrase

  iii)priv_protocol_passphrase

3)The following packages are needed:

* influxdb
* multiprocessing
* threading

## Usage
```
usage: main.py [-h] -labels LABELS [LABELS ...] -version {1,2,3} -mode
               {Parallel,Serial} [-libPDU {Threading,Multiprocessing}]
               [-iterations ITERATIONS] [-libNODE {Multiprocessing}]
               snmp configuration file

PDU data acquisition tool

required arguments:
  snmp configuration file
                        Parse the snmp config file into program
  -labels LABELS [LABELS ...], -l LABELS [LABELS ...]
                        Obtain labels of PDUs by providing the ip address,
                        please use human readable names.
  -version {1,2,3}, -v {1,2,3}
                        Determine snmp version to be used, please consider the
                        corresponding configuration file working with the
                        given version
  -mode {Parallel,Serial}, -m {Parallel,Serial}
                        Determine the data acquisition way, parallel or serial
  -iterations ITERATIONS, -i ITERATIONS
                        Determine the number of iterations to issue the snmp
                        command and save the timing into a file. When you do
                        not use this option then perpetual monitoring is
                        enabled

optional arguments:
  -libPDU {Threading,Multiprocessing}, -lbP {Threading,Multiprocessing}
                        Determine the used library for the parallel mode in
                        PDU level
  -libNODE {Multiprocessing}, -lbN {Multiprocessing}
                        Determine the used library for the parallel mode in
                        further NODE level, in that case the snmpget command
                        is used

```

**Example:**

```
python3 main.py config_files/snmpV2/snmpV2.ini -l pdu11 -v 2 -m Parallel -lbP Threading -lbN Multiprocessing -i 1
```
