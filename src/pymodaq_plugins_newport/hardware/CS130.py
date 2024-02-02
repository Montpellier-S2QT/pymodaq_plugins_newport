# -*- coding: utf-8 -*-

import sys
import clr
import time
from pythonnet import load

class CS130():

    _dll_path = 'D:\\DLL_to_be_shared\\DLL'
    _shutter_auto = True
    def open_communication(self):
        load()
        sys.path.append(self._dll_path)
        clr.AddReference('Cornerstone64')
        import CornerstoneDll

        self._device = CornerstoneDll.Cornerstone(True)

        try:
            a=self._device.connect()
            b=self._device.findDevices()
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

    def get_grating(self):
        """ Returns the current grating index

        @return (int): Current grating index
        """
        return int(self._device.getGrating()[0])-1

    def set_grating(self, value):
        """ Sets the grating by index

        @param (int) value: grating index
        """

        self._device.setGrating(value+1)


    def get_wavelength(self):
        """ Returns the current central wavelength in nmeter

        @return (float): current central wavelength (nmeter)
        """
        self._device.getWavelength()
        w=float(self._device.getResponse())

        return w   #*1.0e-9

    def set_wavelength(self, value):
        """ Sets the new central wavelength in nmeter

        @params (float) value: The new central wavelength (nmeter)
        """

        self._device.setWavelength(float(value))   #* 1.0e9)
        time.sleep(0.1)


