import requests
from datetime import datetime
from typing import List, Union
import dateutil.parser
import pathlib

from bs4 import BeautifulSoup

from asi import config

"""
This program contains the download() function to download the Red-line Emission Geospace 
Observatory (REGO) data from the themis.ssl.berkeley.edu server to the 
config.ASI_DATA_DIR/rego/ directory
"""

IMG_BASE_URL = 'http://themis.ssl.berkeley.edu/data/themis/thg/l1/reg/'
CAL_BASE_URL = 'https://data.phys.ucalgary.ca/sort_by_project/GO-Canada/REGO/skymap/'

# Check and make a config.ASI_DATA_DIR/rego/ directory if doesn't already exist.
if not pathlib.Path(config.ASI_DATA_DIR, 'rego').exists():
    pathlib.Path(config.ASI_DATA_DIR, 'rego').mkdir()


def download_rego_img(day: Union[datetime, str], station: str, download_hour: bool=True,
            force_download: bool=False, test_flag: bool=False) -> List[pathlib.Path]:
    """
    The wrapper to download the REGO data given the day, station name,
    and a flag to download a single hour file or the entire day. The images
    are saved to the config.ASI_DATA_DIR / 'rego' directory. 

    Parameters
    ----------
    day: datetime.datetime or str
        The date and time to download the data from. If day is string, 
        dateutil.parser.parse will attempt to parse it into a datetime
        object.
    station: str
        The station id to download the data from.
    download_hour: bool (optinal)
        If True, will download only one hour of image data, otherwise it will
        download image data from the entire day.
    force_download: bool (optional)
        If True, download the file even if it already exists.

    Returns
    -------
    download_paths: list
        A list of pathlib.Path objects that contain the downloaded file
        path(s).

    Example
    -------
    day = datetime(2017, 4, 13, 5)
    station = 'LUCK'
    download(day, station)  # Will download to the aurora_asi/data/rego/ folder.
    """
    if isinstance(day, str):
        day = dateutil.parser.parse(day)
    # Add the station/year/month url folders onto the url
    url = IMG_BASE_URL + f'{station.lower()}/{day.year}/{str(day.month).zfill(2)}/'

    if download_hour:
        # Find an image file for the hour.
        search_pattern = f'{station.lower()}_{day.strftime("%Y%m%d%H")}'
        file_names = search_hrefs(url, search_pattern=search_pattern)
        
        # Download file
        download_url = url + file_names[0]  # On the server
        download_path = pathlib.Path(config.ASI_DATA_DIR, 'rego', file_names[0])  # On the local machine.
        # Download if force_download=True or the file does not exist.
        if force_download or (not download_path.is_file()):
            stream_large_file(download_url, download_path, test_flag=test_flag)
        return [download_path]
    else:
        # Otherwise find all of the image files for that station and UT hour.
        file_names = search_hrefs(url)
        download_paths = []
        # Download files
        for file_name in file_names:
            download_url = url + file_name
            download_path = pathlib.Path(config.ASI_DATA_DIR, 'rego', file_name)
            download_paths.append(download_path)
            # Download if force_download=True or the file does not exist.
            if force_download or (not download_path.is_file()):
                stream_large_file(download_url, download_path, test_flag=test_flag)
        return download_paths

def download_rego_cal(station: str, force_download: bool=False):
    """
    This function downloads the latest calibration (skymap) IDL .sav files.

    Parameters
    ----------
    station: str
        The station name, case insensitive
    force_download: bool (optional)
        If True, download the file even if it already exists.
    
    Returns
    -------
    None
    """

    return

def stream_large_file(url, save_path, test_flag: bool=False):
    """
    Streams a file from url to save_path. In requests.get(), stream=True 
    sets up a generator to download a small chuck of data at a time, 
    instead of downloading the entire file into RAM first.

    Parameters
    ----------
    url: str
        The URL to the file.
    save_path: str or pathlib.Path
        The local save path for the file.
    test_flag: bool (optional)
        If True, the download will halt after one 5 Mb chunk of data is 
        downloaded.
    """
    r = requests.get(url, stream=True) 
    file_size = int(r.headers.get('content-length'))
    downloaded_bites = 0

    save_name = pathlib.Path(save_path).name

    megabyte = 1024*1024

    with open(save_path, 'wb') as f:
        for data in r.iter_content(chunk_size=5*megabyte): 
            f.write(data)
            if test_flag:
                return
            # Update the downloaded % in the terminal.
            downloaded_bites += len(data)
            print(f'{save_name} is {round(100*downloaded_bites/file_size)}% downloaded', end='\r')
    print()  # Add a newline 
    return

def search_hrefs(url: str, search_pattern: str ='') -> List[str]:
    """
    Given a url string, this function returns all of the 
    hyper references (hrefs, or hyperlinks) if search_pattern=='',
    or a specific href that contains the search_pattern. If search_pattern
    is not found, this function raises a NotADirectoryError. The 
    search is case-insensitive, and it doesn't return the '../' href.

    Parameters
    ----------
    url: str
        A url in string format
    search_pattern: str (optional)
        Find the exact search_pattern text contained in the hrefs.

    Returns
    -------
    hrefs: List(str)
        A list of hrefs that contain the search_pattern.
    """
    matched_hrefs = []

    request = requests.get(url)
    # request.status_code
    soup = BeautifulSoup(request.content, 'html.parser')

    for href in soup.find_all('a', href=True):
        if (search_pattern.lower() in href['href'].lower()):
            matched_hrefs.append(href['href'])
    if len(matched_hrefs) == 0:
        raise NotADirectoryError(f'The url {url} does not contain any hyper '
            f'references containing the search_pattern="{search_pattern}".')
    return matched_hrefs

if __name__ == '__main__':
    day = datetime(2020, 8, 1, 4)
    station = 'Luck'
    download(day, station, force_download=True)