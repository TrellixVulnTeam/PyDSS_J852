from PyDSS.pyContrReader import pyExportReader, pySubscriptionReader
from PyDSS.pyLogger import getLoggerTag
import logging
import helics
import os

import math

class helics_interface:

    n_states = 5
    init_state = 1

    type_info = {
        'CurrentsMagAng': 'vector',
        'Currents': 'vector',
        'RatedCurrent': 'double',
        'EmergAmps': 'double',
        'NormalAmps': 'double',
        'normamps': 'double',
        'Losses': 'vector',
        'PhaseLosses': 'vector',
        'Powers': 'vector',
        'TotalPower': 'vector',
        'LineLosses': 'vector',
        'SubstationLosses': 'vector',
        'kV': 'double',
        'kVARated': 'double',
        'kvar': 'double',
        'kW': 'double',
        'kVABase': 'double',
        'kWh': 'double',
        'puVmagAngle': 'vector',
        'VoltagesMagAng': 'vector',
        'VMagAngle': 'vector',
        'Voltages': 'vector',
        'Vmaxpu': 'double',
        'Vminpu': 'double',
        'Frequency': 'double',
        'Taps': 'vector',
        '%stored': 'double',
        'Distance': 'double'
    }

    def __init__(self, dss_solver, objects_by_name, objects_by_class, options, system_paths):

        if options["Logging"]["Pre-configured logging"]:
            LoggerTag = __name__
        else:
            LoggerTag = getLoggerTag(options)

        self.itr = 0
        self.c_seconds = 0
        self.c_seconds_old = -1
        self._logger = logging.getLogger(LoggerTag)
        self._options = options
        self._co_convergance_error_tolerance = options['Helics']['Error tolerance']
        self._co_convergance_max_iterations = options['Helics']['Max co-iterations']
        self._publications = {}
        self._subscriptions = {}
        self._system_paths = system_paths
        self._objects_by_element = objects_by_name
        self._objects_by_class = objects_by_class
        self._create_helics_federate()
        self._dss_solver = dss_solver
        self._registerFederateSubscriptions()
        self._registerFederatePublications()
        helics.helicsFederateEnterExecutingModeIterative(
            self._PyDSSfederate,
            helics.helics_iteration_request_iterate_if_needed
        )
        self._logger.info('Entered HELICS execution mode')

    def _create_helics_federate(self):
        self.fedinfo = helics.helicsCreateFederateInfo()
        helics.helicsFederateInfoSetBroker(self.fedinfo, self._options['Helics']['Broker'])
        helics.helicsFederateInfoSetCoreName(self.fedinfo, self._options['Helics']['Federate name'])
        helics.helicsFederateInfoSetCoreTypeFromString(self.fedinfo, self._options['Helics']['Core type'])
        helics.helicsFederateInfoSetCoreInitString(self.fedinfo, f"--federates=1")
        if 'Broker' in self._options['Helics']:
            helics.helicsFederateInfoSetBroker(self.fedinfo, self._options['Helics']['Broker'])
        #helics.helicsFederateInfoSetBroker(self.fedinfo, self._options['Helics']['Broker'])
        #helics.helicsFederateInfoSetBrokerPort(self.fedinfo, self._options['Helics']['Broker port'])
        helics.helicsFederateInfoSetTimeProperty(self.fedinfo, helics.helics_property_time_delta,
                                                 self._options['Helics']['Time delta'])
        helics.helicsFederateInfoSetIntegerProperty(self.fedinfo, helics.helics_property_int_log_level,
                                                self._options['Helics']['Helics logging level'])

        helics.helicsFederateInfoSetFlagOption(self.fedinfo, helics.helics_flag_uninterruptible, True)
        helics.helicsFederateInfoSetIntegerProperty(self.fedinfo, helics.helics_property_int_max_iterations,
                                                    self._options["Helics"]["Max co-iterations"])
        self._PyDSSfederate = helics.helicsCreateValueFederate(self._options['Helics']['Federate name'], self.fedinfo)


        return


    def _registerFederateSubscriptions(self):
        self._sub_file_reader = pySubscriptionReader(
            os.path.join(
                self._system_paths["ExportLists"],
                "Subscriptions.toml",
            ),
        )
        self._subscriptions = {}
        self._subscription_dState = {}
        for element, subscription in self._sub_file_reader.SubscriptionList.items():
            assert element in self._objects_by_element, '"{}" listed in the subscription file not '.format(element) +\
                                                     "available in PyDSS's master object dictionary."

            sub = helics.helicsFederateRegisterSubscription(
                self._PyDSSfederate,
                subscription["Subscription ID"],
                subscription["Unit"]
            )
            #helics.helicsInputSetMinimumChange(sub, self._options["Helics"]["Error tolerance"])
            self._logger.info('Subscription registered: "{}" with units "{}"'.format(
                subscription["Subscription ID"],
                subscription["Unit"])
            )
            subscription['Subscription'] = sub
            self._subscriptions[element] = subscription
            self._subscription_dState[element] = [self.init_state] * self.n_states
        return

    def updateHelicsSubscriptions(self):

        for element_name, sub_info in self._subscriptions.items():
            if 'Subscription' in sub_info:
                value = None
                if sub_info['Data type'].lower() == 'double':
                    value = helics.helicsInputGetDouble(sub_info['Subscription'])
                elif sub_info['Data type'].lower() == 'vector':
                    value = helics.helicsInputGetVector(sub_info['Subscription'])
                    if isinstance(value, list):
                        value = value[sub_info['index']]
                elif sub_info['Data type'].lower() == 'string':
                    value = helics.helicsInputGetString(sub_info['Subscription'])
                elif sub_info['Data type'].lower() == 'boolean':
                    value = helics.helicsInputGetBoolean(sub_info['Subscription'])
                elif sub_info['Data type'].lower() == 'integer':
                    value = helics.helicsInputGetInteger(sub_info['Subscription'])

                if value:
                    value = value * sub_info['Multiplier']
                    # if you are iterating and the feedin voltage is close to 0, log the time and iteration, but continue with nominal so that you can continue
                    if element_name == "Vsource.source" and self._options['Helics']['Iterative Mode'] and (value<0.01 or math.isnan(value) or value=='nan'):
                        self._logger.debug('Feed-in voltage {value} at time {self.c_seconds} iteration {self.itr}, continuing with nominal voltage.')
                        print(f'voltage {value} continuing with nominal')
                        value = 1.0
                    elif element_name.startswith('Load.load') and self._options['Helics']['Iterative Mode'] and (abs(value)>10e20 or math.isnan(value) or value=='nan'):
                        self._logger.debug('load {value} at time {self.c_seconds} iterationi {self.itr}, continuing with 0 load.')
                        print(f'load {element_name} = {value}, conitinuing with 0 load.') 
                        value = 0.0
                    dssElement = self._objects_by_element[element_name]
                    dssElement.SetParameter(sub_info['Property'], value)
                    print(f'Value for {element_name}.{sub_info["Property"]} changed to {value}')
                    self._logger.debug('Value for "{}.{}" changed to "{}"'.format(
                    element_name,
                    sub_info['Property'],
                    value * sub_info['Multiplier']
                    ))

                    if self._options['Helics']['Iterative Mode']:
                        if self.c_seconds != self.c_seconds_old:
                            self._subscription_dState[element_name] = [self.init_state] * self.n_states
                        else:
                            self._subscription_dState[element_name].insert(0,self._subscription_dState[element_name].pop())
                        self._subscription_dState[element_name][0] = value
                        print(self._subscription_dState[element_name])
        self.c_seconds_old = self.c_seconds

    def _registerFederatePublications(self):
        self._file_reader = pyExportReader(
            os.path.join(
                self._system_paths ["ExportLists"],
                "ExportMode-byClass.toml",
            ),
        )
        self._publications = {}
        for valid_publication in self._file_reader.publicationList:
            obj_class, obj_property = valid_publication.split(' ')
            objects = self._objects_by_class[obj_class]
            for obj_X, obj in objects.items():
                name = '{}.{}.{}'.format(self._options['Helics']['Federate name'], obj_X, obj_property)
                self._publications[name] = helics.helicsFederateRegisterGlobalTypePublication(
                    self._PyDSSfederate,
                    name,
                    self.type_info[obj_property],
                    ''
                )
                self._logger.info(f'Publication registered: {name}')
        return

    def updateHelicsPublications(self):
        for element, pub in self._publications.items():
            fed_name, class_name, object_name, ppty_name = element.split('.')
            obj_name = '{}.{}'.format(class_name, object_name)
            obj = self._objects_by_element[obj_name]
            value = obj.GetValue(ppty_name)
            if isinstance(value, list):
                helics.helicsPublicationPublishVector(pub, value)
                #print(f'{obj_name}, {ppty_name} published as list {value}')
            elif isinstance(value, float):
                helics.helicsPublicationPublishDouble(pub, value)
            elif isinstance(value, str):
                helics.helicsPublicationPublishString(pub, value)
            elif isinstance(value, bool):
                helics.helicsPublicationPublishBoolean(pub, value)
            elif isinstance(value, int):
                helics.helicsPublicationPublishInteger(pub, value)
        return

    def request_time_increment(self, step=1):
        error = sum([abs(x[0] - x[1]) for k, x in self._subscription_dState.items()])
        r_seconds = self._dss_solver.GetTotalSeconds() #- self._dss_solver.GetStepResolutionSeconds()
        if not self._options['Helics']['Iterative Mode'] or error<0.0001 or step==0:
            while self.c_seconds < r_seconds:
                self.c_seconds = helics.helicsFederateRequestTime(self._PyDSSfederate, r_seconds)
            self._logger.info('Time requested: {} - time granted: {} '.format(r_seconds, self.c_seconds))
            print(f'advance, not iterative helics time: {self.c_seconds}')
            return True, self.c_seconds
        else:
            
            #iteration_state = helics.helics_iteration_result_iterating
            #while iteration_state == helics.helics_iteration_result_iterating:
            print(f'requresting time {r_seconds} with helics time: {self.c_seconds}')
            self.c_seconds, iteration_state = helics.helicsFederateRequestTimeIterative(self._PyDSSfederate, r_seconds, iterate=helics.helics_iteration_request_iterate_if_needed)
            print(f'time requested {r_seconds}, timegranted {self.c_seconds}')
            self._logger.info('Time requested: {} - time granted: {} error: {} it: {}'.format(
                r_seconds, self.c_seconds, error, self.itr))
            if error > 0.0001 and self.itr < self._co_convergance_max_iterations:
                self.itr += 1
                return False, self.c_seconds
            else:
                self.itr = 0
                return True, self.c_seconds

    def __del__(self):
        helics.helicsFederateFinalize(self._PyDSSfederate)
        state = helics.helicsFederateGetState(self._PyDSSfederate)
        helics.helicsFederateInfoFree(self.fedinfo)
        helics.helicsFederateFree(self._PyDSSfederate)
        self._logger.info('HELICS federate for PyDSS destroyed')
