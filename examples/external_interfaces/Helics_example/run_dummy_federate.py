import time
import helics as h
from math import pi
import random
import time

initstring = "-f 2 --name=mainbroker"
fedinitstring = "--broker=mainbroker --federates=1"
deltat = 0.01

helicsversion = h.helicsGetVersion()
print("Helics version: ", helicsversion )

# Create broker #
broker = h.helicsCreateBroker("zmq", "", initstring)
print("Broker: ", broker)
isconnected = h.helicsBrokerIsConnected(broker)
print("Broker connected: ", isconnected)


# Create Federate Info object that describes the federate properties #
fedinfo = h.helicsCreateFederateInfo()
print("Fedinfo created: ", fedinfo)


# Set Federate name #
h.helicsFederateInfoSetCoreName(fedinfo, "Test Federate")

# Set core type from string #
h.helicsFederateInfoSetCoreTypeFromString(fedinfo, "zmq")

# Federate init string #
h.helicsFederateInfoSetCoreInitString(fedinfo, fedinitstring)

# Set the message interval (timedelta) for federate. Note th#
# HELICS minimum message time interval is 1 ns and by default
# it uses a time delta of 1 second. What is provided to the
# setTimedelta routine is a multiplier for the default timedelta.

# Set one second message interval #
h.helicsFederateInfoSetTimeProperty(fedinfo, h.helics_property_time_delta, deltat)
#h.helicsFederateInfoSetIntegerProperty(fedinfo, h.helics_property_int_log_level, 20)
# Create value federate #
vfed = h.helicsCreateValueFederate("Test Federate", fedinfo)
print("Federate created: ", vfed )

# Register the publication #
pub1 = h.helicsFederateRegisterGlobalTypePublication(vfed, "test.load1.power", "double", "kW")
pub2 = h.helicsFederateRegisterGlobalTypePublication(vfed, "test.feederhead.voltage", "double", "kW")
print("Publication creation complete")
sub1 = h.helicsFederateRegisterSubscription(vfed, "PyDSS/Circuit/heco19021/power/complex/ABC/1", "kVA")
#h.helicsInputSetMinimumChange(sub1, 0.1)
print("Subscription creation complete")
# Enter execution mode #

print("Federate finalized: ", vfed )

h.helicsFederateEnterExecutingMode(vfed)
print("Entered execution mode")

for t in range(1, 30):
    print(t)
    time_requested = t * 60
    #currenttime = h.helicsFederateRequestTime(vfed, time_requested)
    iteration_state = h.helics_iteration_result_iterating
    for i in range(20):
        currenttime, iteration_state = h.helicsFederateRequestTimeIterative(
            vfed,
            time_requested,
            h.helics_iteration_request_iterate_if_needed
        )
        h.helicsPublicationPublishDouble(pub1, 5.0 + 1. / (1.0 + i))
        h.helicsPublicationPublishDouble(pub2, 1.0)
        value = h.helicsInputGetComplex(sub1)
        print(value)

h.helicsFederateFinalize(vfed)

while h.helicsBrokerIsConnected(broker):
    time.sleep(1)

h.helicsFederateFree(vfed)
h.helicsCloseLibrary()