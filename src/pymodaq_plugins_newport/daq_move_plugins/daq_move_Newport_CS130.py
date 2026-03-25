from pymodaq.control_modules.move_utility_classes import DAQ_Move_base, comon_parameters_fun, main, DataActuatorType, \
    DataActuator  # common set of parameters for all actuators
from pymodaq.utils.daq_utils import ThreadCommand   # object used to send info back to the main thread
from pymodaq.utils.parameter import Parameter

from pymodaq_plugins_newport.hardware.CS130 import CS130

class DAQ_Move_Newport_CS130(DAQ_Move_base):
    """ Instrument plugin class for an actuator.
    
    This object inherits all functionalities to communicate with PyMoDAQ’s DAQ_Move module through inheritance via
    DAQ_Move_base. It makes a bridge between the DAQ_Move module and the Python wrapper of a particular instrument.

    This plugin controls Newport/CornerStone C130 monochromator
    It has been tested with an USB CS130 monochromator with Pymodaq 5.1 in a Win10 operating system
    Up to date dll should be used (Cornerstone64.dll and CyUSB.dll)
    Of course, prior to this test, make sure that the spectrometer is working with the firmware (MonoUT)

    Attributes:
    -----------
    controller: object
        The particular object that allow the communication with the hardware, in general a python wrapper around the
         hardware library.
         
    """
    _controller_units = 'nm'
    is_multiaxes = False
    _axis_names = []
    _epsilon = 0.05
    data_actuator_type = DataActuatorType['DataActuator']

    params = [
                 {'title': 'Mono Settings:', 'name': 'mono_settings', 'type': 'group', 'expanded': True,
                  'children': [
                      {'title': 'Mono SN:', 'name': 'mono_serialnumber', 'type': 'str', 'value': '',
                       'readonly': True},
                      {'title': 'Grating Settings:', 'name': 'grating_settings', 'type': 'group', 'expanded': True,
                       'children': [
                           {'title': 'Grating:', 'name': 'grating', 'type': 'list','limits':[]},
                           {'title': 'Lines (/mm):', 'name': 'gr_lines', 'type': 'int', 'readonly': True},
                           {'title': 'Label:', 'name': 'gr_label', 'type': 'str', 'readonly': True},
                       ]},
                  ]},
             ] + comon_parameters_fun(is_multiaxes, _axis_names, epsilon=_epsilon)


    def ini_attributes(self):
        self.controller: CS130 = None
        pass

    def get_actuator_value(self):
        """Get the current value from the hardware with scaling conversion.

        Returns
        -------
        float: The position obtained after scaling conversion.
        """
        pos = DataActuator(data=self.controller.get_wavelength())
        pos = self.get_position_with_scaling(pos)
        return pos

    def get_available_gratings(self):
        """Defines the available gratings from the instrument"""
        gratings = self.controller.get_available_gratings()
        gratings_str = []
        gratings_dict = dict()
        for gr in gratings:
            string = str(self.controller.get_grating_lines(gr))+'/'+str(self.controller.get_grating_label(gr))
            gratings_str.append(string)
            gratings_dict[string] = gr
        return gratings_str, gratings_dict

    def close(self):
        """Terminate the communication protocol"""
        self.controller.close_communication()

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        if param.name() == "grating":
            gr_index = get_available_gratings()[1][param.value()]
            self.controller.set_grating(gr_index)
            self.settings.child('mono_settings', 'gr_lines').setValue(self.controller.get_grating_lines(gr_index))
            self.settings.child('mono_settings', 'gr_label').setValue(self.controller.get_grating_label(gr_index))
        else:
            pass

    def ini_stage(self, controller=None):
        """Actuator communication initialization

        Parameters
        ----------
        controller: (object)
            custom object of a PyMoDAQ plugin (Slave case). None if only one actuator by controller (Master case)

        Returns
        -------
        info: str
        initialized: bool
            False if initialization failed otherwise True
        """

        self.controller = self.ini_stage_init(old_controller=controller,
                                              new_controller=CS130())

        info = "Initializing CS130"
        initialized = self.controller.open_communication()
        self.settings.child('mono_settings', 'mono_serialnumber').setValue(self.controller.get_device_name())
        self.settings.child('mono_settings', 'grating').setLimits(self.get_available_gratings()[0])
        gr_index = self.controller.get_grating()
        self.settings.child('mono_settings', 'grating').setValue(list(get_available_gratings()[1].keys())[gr_index-1])
        self.settings.child('mono_settings', 'gr_lines').setValue(self.controller.get_grating_lines(gr_index))
        self.settings.child('mono_settings', 'gr_label').setValue(self.controller.get_grating_label(gr_index))
        return info, initialized

    def move_abs(self, value: DataActuator):
        """ Move the actuator to the absolute target defined by value

        Parameters
        ----------
        value: (float) value of the absolute target positioning
        """

        value = self.check_bound(value)   # if user checked bounds, the defined bounds are applied here
        self.target_value = value
        value = self.set_position_with_scaling(value)  # apply scaling if the user specified one

        self.controller.set_wavelength(value.value())
        message='New wavelength (nm): '+str(value.value())
        self.emit_status(ThreadCommand('Update_Status', [message]))

    def move_rel(self, value: DataActuator):
        """ Move the actuator to the relative target actuator value defined by value

        Parameters
        ----------
        value: (float) value of the relative target positioning
        """
        value = self.check_bound(self.current_position + value) - self.current_position
        self.target_value = value + self.current_position

        self.controller.set_wavelength(self.target_value)
        message = 'New wavelength (nm): ' + str(value.value())
        self.emit_status(ThreadCommand('Update_Status', [message]))

    def move_home(self):
        """Call the reference method of the controller"""

        # TODO for your custom plugin
        raise NotImplemented  # when writing your own plugin remove this line
        self.controller.your_method_to_get_to_a_known_reference()  # when writing your own plugin replace this line
        self.emit_status(ThreadCommand('Update_Status', ['Some info you want to log']))

    def stop_motion(self):
        """Stop the actuator and emits move_done signal"""
        self.controller.stop_motion()
        self.emit_status(ThreadCommand('Update_Status', ['Move done']))


if __name__ == '__main__':
    main(__file__)
