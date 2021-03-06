import unittest
import pathlib
from datetime import datetime

import cdflib

from asilib.io import load
from asilib import config

"""
Most of these tests just makes sure that the functions run correctly
and it doesn't validate the output.
"""


class TestPlotFrame(unittest.TestCase):
    def setUp(self):
        self.load_date = datetime(2016, 10, 29, 4)
        self.station = 'GILL'

    def test_rego_load_img(self):
        """ Checks that the REGO ASI image file can be loaded. """
        cdf_obj = load.load_img(self.load_date, 'REGO', self.station)
        return

    def test_themis_load_img(self):
        """ Checks that the REGO ASI image file can be loaded. """
        cdf_obj = load.load_img(self.load_date, 'THEMIS', self.station)
        return

    def test_rego_load_cal(self):
        """ Load the REGO callibration file. """
        cal = load.load_cal('REGO', self.station)
        return

    def test_themis_load_cal(self):
        """ Load the THEMIS callibration file. """
        cal = load.load_cal('THEMIS', self.station)
        return

    def test_themis_get_frame(self):
        """ Get one THEMIS ASI image."""
        time, frame = load.get_frame(self.load_date, 'THEMIS', 'GILL')
        time_diff = (self.load_date - time).total_seconds()
        self.assertTrue(abs(time_diff) < 3)
        return

    def test_rego_get_frame(self):
        """ Get one REGO ASI image."""
        time, frame = load.get_frame(self.load_date, 'REGO', 'GILL')
        time_diff = (self.load_date - time).total_seconds()
        self.assertTrue(abs(time_diff) < 3)
        return


if __name__ == '__main__':
    unittest.main()
