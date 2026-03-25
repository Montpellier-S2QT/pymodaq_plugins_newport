# -*- coding: utf-8 -*-

import sys
import clr
import time
from pythonnet import load

class CS130():

    _dll_path = 'D:\\My_DLLs\\Cornerstone'
    _shutter_auto = True

    def open_communication(self):
        load()
        sys.path.append(self._dll_path)
        clr.AddReference('Cornerstone64')
        import CornerstoneDll

        self._device = CornerstoneDll.Cornerstone(True)

        try:
            self._device.connect()
            self._device.findDevices()
        except:
            raise IOError('No device found')


        if self._shutter_auto:
            self._device.setShutter(True)

        self._device.setVendorID(1180)
        self._device.setProductID(12)
        self._device.setWaitTime(100)
        self._device.setDeviceTimeout(500)

        return True

    def close_communication(self):
        if self._shutter_auto:
            self._device.setShutter(False)
        return self._device.disconnect()

    def get_device_name(self):
        return self._device.getDeviceName()

    def get_available_gratings(self):
        available_gratings = []
        for i in range(1,4):
            lines = self._device.getGratingLines(i)
            if lines =! -1.0:
                available_gratings.append(i)
        return available_gratings

    def get_grating_lines(self, index):
        return self._device.getGratingLines(index)

    def get_grating_label(self, index):
        return self._device.getGratingLabel(index)

    def get_grating(self):
        """ Returns the current grating index

        @return (int): Current grating index
        """
        return int(self._device.getGrating()[0])

    def set_grating(self, index):
        """ Sets the grating by index

        @param (int) value: grating index
        """
        self._device.setGrating(index)


    def get_wavelength(self):
        """ Returns the current central wavelength in nmeter

        @return (float): current central wavelength (nmeter)
        """
        time.sleep(0.1)

        self._device.getWavelength()
        w=float(self._device.getResponse())
        return w   #*1.0e-9

    def set_wavelength(self, value):
        """ Sets the new central wavelength in nmeter

        @params (float) value: The new central wavelength (nmeter)
        """

        command_str = 'GOWAVE ' + str(value)
        self._device.sendCommand(command_str)
        time.sleep(0.1)


    def stop_motion(self):
        self._device.device.sendCommand('ABORT')


