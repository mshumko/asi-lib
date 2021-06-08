"""
The Imager class handles the ASI data downloading, loading, analyzing, and plotting.
"""

supported_arrays = ['REGO', 'THEMIS']

from numpy import NaN
import pandas as pd

from asilib.io.load import _validate_time_range  # Or
# import asilib.io.load._validate_time_range as _validate_time_range

import asilib
from datetime import datetime

class Imager:
    """
    Handles the downloading, loading, analyzing, and plotting of ASI data.

    Methods
    -------
    download(time_range=None)
        Download data in bulk.
    load(time_range=None)
        Load data from the array camera system for a list of stations (all by default)
    plot(type, ax=None)
        Plots the ASI data in a few supported formats.

    Attributes
    ----------
    array_attributes: pd.DataFrame
        A table of array imagers and their locations
    data_availability: pd.DataFrame
        A table of data availability with station codes for the index and time for columns.
        The table values are yes for available data and no for unavailable data (doesn't exist).
    data: dict  
        A dictionary full of ASI time stamps and images
        # TODO: Think about how to store self.data for:
        #   1) one station for one hour 
        #   2) one station for multiple hours
        #   3) multiple stations for one hour
        #   4) multiple stations for multiple hours.
    cal: dict
        A dictionary contaning the calibration data from all of the loaded stations. 
    array: str
        The camera array
    stations: str or list[str]
        The stations represented in this instance.
    time_range: list[datetime]
        The ASI time_range.
    """

    def __init__(self, array, stations=None, time_range=None):
        """
        Initializes the Imager class.

        Parameters
        ----------
        array: str
            The ASI array. Must be either 'THEMIS' or 'REGO'.
        stations: str, or list of strings, optional
            Station or stations codes to load. If `station=None`, all 
            stations from the array will be loaded.
        """
        self.array = array.upper()
        self.stations = stations
        self.time_range = time_range

        # Validate inputs
        if not (self.time_range is None):
            self.time_range = _validate_time_range(self.time_range)
        self._load_array_attributes()
        self._check_array_code()
        # self._check_station_codes()
        return

    def download(self, time_range=None):
        """
        Downloads data from time_range. This function is automatically called 
        by load(), but it is useful if you only need to download data in bulk.

        Parameters
        ----------
        time_range: list , optional
            The start and end time to download the ASI data. 
        """
        self._check_time_range_exists(time_range)

        # TODO: Step 3: Here we make calls to 
        # download_rego_img, download_rego_cal
        # download_themis_img, download_themis_cal,
        # depending on the user-specified array. 
        # Since the calibration data 

        if self.array == 'THEMIS':
            from asilib.io.download_themis import download_themis_cal
            from asilib.io.download_themis import download_themis_img
        
        elif self.array == 'REGO':
            from asilib.io.download_rego import download_rego_cal
            from asilib.io.download_rego import download_rego_img

        elif self.array == None:
            from asilib.io.download_themis import download_themis_cal
            from asilib.io.download_themis import download_themis_img
            from asilib.io.download_rego import download_rego_cal
            from asilib.io.download_rego import download_rego_img

        return

    def load(self, time_range=None):
        """
        Downloads data from time_range.

        Parameters
        ----------
        time_range: list , optional
            The start and end time to download the ASI data. 
        """
        # TODO: Step 2: This method will load the requested ASI data.
        # If self.stations is None, reference the self.array_attributes
        # pd.DataFrame and load the data from all possible stations. 
        # Errors will arise when data is unavailable and we will have to 
        # catch them. Once load() has been called, save the ASI data to 
        # self.data, and the calibration data to self.cal. Functions in
        # asilib.io.load will be called from here, and we will save the
        # downloaded data into an self.data_avaliability pd.DataFrame that 
        # can be accessed by running print(Imager), or str(Imager). We will
        # need to think carefully on how to load the data to be preserve 
        # computer resources.

        from asilib.io.load import get_frames
        from asilib.io.load import load_cal

        self._check_time_range_exists(time_range)  
        
        self.data = {}

        if self.stations is None:
            
            for station in self.array_attributes['station']:
                
                try:
                    times, frames = get_frames(self.time_range, self.array, station)
                except FileNotFoundError as err:
                    if 'ASI data not found for station' in str(err):
                        continue
                    else:
                        raise

                cal = load_cal(self.array, station)
                self.data[station] = {'times':times, 'frames':frames, 'cal':cal}

        
        else:

            if isinstance(self.stations, str):

                try:
                    times, frames = get_frames(self.time_range, self.array, self.stations)
                except FileNotFoundError as err:
                    if 'ASI data not found for station' in str(err):
                        pass
                    else:
                        raise

                cal = load_cal(self.array, self.stations)
                self.data[self.stations] = {'times':times, 'frames':frames, 'cal':cal}

            elif hasattr(self.stations, '__len__'):
                
                for station in self.stations:
                    try:
                        times, frames = get_frames(self.time_range, self.array, station)
                    except FileNotFoundError as err:
                        if 'ASI data not found for station' in str(err):
                            continue
                        else:
                            raise

                    cal = load_cal(self.array, station)
                    self.data[station] = {'times':times, 'frames':frames, 'cal':cal}
        
        self.data_availability = pd.DataFrame(index = self.data.keys(), columns = pd.date_range(start=self.time_range[0], end=self.time_range[-1], freq='H'))

        print(self.data_availability)
  
        return

    def plot(self, type, ax=None):
        """
        Plots the ASI data.

        Parameters
        ----------
        type: str
            A type of plot to make. Valid types are 'fisheye', 'keogram', and 'map'.
        ax: plt.Axes, optional
            The subplot object to modify the axis, labels, etc.
        """
        return

    def __repr__(self):
        """
        Returns a string of an expression that re-creates this object.
        """
        s = (f"{self.__class__.__qualname__}('{self.array}', "
            f"stations={self.stations}, time_range={self.time_range})")
        return s

    def __str__(self):
        """
        Return a human-readable representation of this object containing:
        the array, stations, time_range, and data_avaliability.
        """
        s = (f"{self.array} Imager\nstations={self.stations}\n"
            f"time_range={self.time_range}")
        if hasattr(self, 'data_avaliability'):
            s += f"\ndata_avaliability:\n{self.data_availability}"
        return s

    def _load_array_attributes(self):
        """
        Loads the stations from asilib/data/asi_stations.csv that match the self.array code
        into a pd.DataFrame.

        Returns
        -------
        self.array_attributes
        """

        self.array_attributes = pd.read_csv('asilib/data/asi_stations.csv')
        self.array_attributes = self.array_attributes.loc[self.array_attributes['array'].str.upper() == self.array]
        self.array_attributes.reset_index(inplace=True)
        
        return self.array_attributes

    def _check_array_code(self):
        """
        Checks that the array code is valid.
        """
        assert self.array in supported_arrays, (f"{self.array} array code is invalid, must be "
            f" in {supported_arrays}. Case insensitive.")
        return

    def _check_station_codes(self):
        """
        Checks that the station or station codes are all valid stations.
        """
        if hasattr(self.stations, '__len__'):
            invalid_stations = []

            for station in self.stations:
                if station.upper() not in self.array_attributes['station']:
                    invalid_stations.append(station)
            
            assert len(invalid_stations) > 0, (f'{invalid_stations} stations '
                f'are not in {self.array_attributes["station"]}')
        
        else:
            assert self.station.upper() in self.array_attributes['station'], (f'{self.stations} not in '
                f'{self.array_attributes["station"]}')
        return

    def _check_time_range_exists(self, time_range):
        """
        Check that the time_range variable exists in the class.
        """
        if (time_range is None) and (not hasattr(self, 'time_range')):
            raise AttributeError('Imager.time_range not found. It must be supplied '
                                'to __init__() or the called method')
        return

if __name__ == '__main__':
    #im = Imager('THEMIS', 'GILL', [datetime(2008, 3, 9, 4, 39), datetime(2008, 3, 9, 4, 40)])
    #im = Imager('THEMIS', ['GILL'], [datetime(2008, 3, 9, 4, 39), datetime(2008, 3, 9, 4, 40)])
    #im = Imager('THEMIS', ['GILL', 'FSMI'], [datetime(2008, 3, 9, 4, 39), datetime(2008, 3, 9, 4, 40)])
    im = Imager('THEMIS', stations = None, time_range = [datetime(2008, 3, 9, 4, 39), datetime(2008, 3, 9, 4, 40)])
    repr(im)
    print(im)

    im.load()