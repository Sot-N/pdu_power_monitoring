In this folder,

you can find all the emerson pdu related mibs. They have been corrected. Otherwise, they were not recognized by snmp.

So, install all the necessary snmp software. Then in the /etc/snmp create the following snmp.conf.


# As the snmp packages come without MIB files due to license reasons, loading
# of MIBs is disabled by default. If you added the MIBs you can reenable
# loading them by commenting out the following line.
#mibs +ALL

mibdirs +$HOME/.snmp/mibs
mibs +LIEBERT-GP-REGISTRATION-MIB           
mibs +LIEBERT-GP-AGENT-MIB
mibs +LIEBERT-GP-CONDITIONS-MIB
mibs +LIEBERT-GP-CONTROLLER-MIB
mibs +LIEBERT-GP-NOTIFICATIONS-MIB
mibs +LIEBERT-GP-SYSTEM-MIB
mibs +LIEBERT-GP-ENVIRONMENTAL-MIB
mibs +LIEBERT-GP-PDU-MIB
mibs +LIEBERT-GP-POWER-MIB
mibs +LIEBERT-GP-FLEXIBLE-MIB
mibs +LIEBERT-GP-FLEXIBLE-CONDITIONS-MIB
mibs +LIEBERT-GP-SRC-MIB           
mibs +UPS-MIB
