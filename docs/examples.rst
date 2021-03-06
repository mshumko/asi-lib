========
Examples
========

This example gallery using the best practices and illustrates functionality throughout `asilib`. 

Example 1: Fisheye Lens View of an Arc
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: ./_static/example_1.png
    :alt: A fisheye lens view of an auroral arc.
    :width: 75%

    A bright auroral arc that was analyzed by Imajo et al., 2021 "Active auroral arc powered by accelerated electrons from very high altitudes"

.. code:: python

    from datetime import datetime

    import matplotlib.pyplot as plt

    import asilib

    frame_time, frame, ax, im = asilib.plot_frame(datetime(2017, 9, 15, 2, 34, 0), 
        'THEMIS', 'RANK', color_norm='log', force_download=False)
    plt.colorbar(im)
    ax.axis('off')
    plt.show()

Example 2: A keogram
^^^^^^^^^^^^^^^^^^^^
.. figure:: ./_static/example_2.png
    :alt: A keogram of STEVE.
    :width: 75%

    A keogram with a STEVE event that moved towards the equator. This event was analyzed in Gallardo-Lacourt et al. 2018 "A statistical analysis of STEVE"

.. code:: python

    import matplotlib.pyplot as plt

    import asilib

    mission='REGO'
    station='LUCK'
    map_alt_km = 230

    fig, ax = plt.subplots(figsize=(8, 6))
    ax, im = asilib.plot_keogram(['2017-09-27T07', '2017-09-27T09'], mission, station, 
                    ax=ax, map_alt=map_alt_km, color_bounds=(300, 800))
    plt.colorbar(im, label='Intensity')
    ax.set_xlabel('UTC')
    ax.set_ylabel(f'Emission Latitude [deg] at {map_alt_km} km')
    plt.tight_layout()
    plt.show()


Example 2: Fisheye Movie
^^^^^^^^^^^^^^^^^^^^^^^^

.. raw:: html

    <iframe width="75%" height="500"
    src="_static/20150326_060700_062957_themis_fsmi.mp4"; frameborder="0"
    allowfullscreen></iframe>

.. code:: python

    from datetime import datetime

    import asilib
    
    time_range = (datetime(2015, 3, 26, 6, 7), datetime(2015, 3, 26, 6, 30))
    asilib.plot_movie(time_range, 'THEMIS', 'FSMI', overwrite=True)
    print(f'Movie saved in {asilib.config["ASI_DATA_DIR"] / "movies"}')

Example 4: A Satellite pass
^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is a sophisticated example that maps a hypothetical satellite track to an image

.. raw:: html

    <iframe width="75%" height="500"
    src="_static/20170915_023400_023557_themis_rank.mp4"; frameborder="0"
    allowfullscreen></iframe>

.. code:: python

    from datetime import datetime

    import numpy as np

    import asilib
    from asilib import plot_movie_generator
    from asilib import lla2azel
    from asilib import load_cal

    # ASI parameters
    mission = 'THEMIS'
    station = 'RANK'
    time_range = (datetime(2017, 9, 15, 2, 34, 0), datetime(2017, 9, 15, 2, 36, 0))

    # Load the calibration data.
    cal_dict = load_cal(mission, station)

    # Create the satellite track's latitude, longitude, altitude (LLA) coordinates.
    # This is an imaginary north-south satellite track oriented to the east
    # of the THEMIS/RANK station.
    n = int((time_range[1] - time_range[0]).total_seconds() / 3)  # 3 second cadence.
    lats = np.linspace(cal_dict["SITE_MAP_LATITUDE"] + 10, cal_dict["SITE_MAP_LATITUDE"] - 10, n)
    lons = (cal_dict["SITE_MAP_LONGITUDE"] + 3) * np.ones(n)
    alts = 500 * np.ones(n)
    lla = np.array([lats, lons, alts]).T

    # Map the satellite track to the station's azimuth and elevation coordinates as well as the
    # image pixels
    # The mapping is not along the magnetic field lines! You need to install IRBEM and then use
    # asilib.lla2footprint().
    sat_azel, sat_azel_pixels = lla2azel(mission, station, lla)

    # Initiate the movie generator function.
    movie_generator = plot_movie_generator(
        time_range, mission, station, azel_contours=True, overwrite=True
    )

    for i, (time, frame, ax, im) in enumerate(movie_generator):
        # Plot the entire satellite track
        ax.plot(sat_azel_pixels[:, 0], sat_azel_pixels[:, 1], 'red')
        # Plot the current satellite position.
        ax.scatter(sat_azel_pixels[i, 0], sat_azel_pixels[i, 1], c='red', marker='x', s=100)

        # Annotate the station and satellite info in the top-left corner.
        station_str = (
            f'{mission}/{station} '
            f'LLA=({cal_dict["SITE_MAP_LATITUDE"]:.2f}, '
            f'{cal_dict["SITE_MAP_LONGITUDE"]:.2f}, {cal_dict["SITE_MAP_ALTITUDE"]:.2f})'
        )
        satellite_str = f'Satellite LLA=({lla[i, 0]:.2f}, {lla[i, 1]:.2f}, {lla[i, 2]:.2f})'
        ax.text(0, 1, station_str + '\n' + satellite_str, va='top', 
                transform=ax.transAxes, color='red')

    print(f'Movie saved in {asilib.config["ASI_DATA_DIR"] / "movies"}')

Example 5: Another Satellite pass
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    
An even more sophisticated example that maps a hypothetical satellite track to an image and calculates the mean ASI intensity in a 10x10 km box around the satellite's location.

The `asilib` functionality used here: 

* `asilib.plot_movie_generator(..).send()` to get all the frames and frame times
* `asilib.equal_area()` to create a masked array of pixels within a X by Y km sized box at the emission altitude. The masked array is `np.nan` outside of the box and 1 inside.
    
.. raw:: html

    <iframe width="100%", height="900px"
    src="_static/20170915_023300_023457_themis_rank.mp4"
    allowfullscreen></iframe>

.. code:: python

    from datetime import datetime

    import numpy as np
    import matplotlib.pyplot as plt

    import asilib

    # ASI parameters
    mission = 'THEMIS'
    station = 'RANK'
    time_range = (datetime(2017, 9, 15, 2, 32, 0), datetime(2017, 9, 15, 2, 35, 0))

    fig, ax = plt.subplots(2, 1, figsize=(7, 10), gridspec_kw={'height_ratios':[4, 1]}, 
                            constrained_layout=True)

    # Load the calibration data. This is only necessary to create a fake satellite track.
    cal_dict = asilib.load_cal(mission, station)

    # Create the fake satellite track coordinates: latitude, longitude, altitude (LLA).
    # This is a north-south satellite track oriented to the east of the THEMIS/RANK 
    # station.
    n = int((time_range[1] - time_range[0]).total_seconds() / 3)  # 3 second cadence.
    lats = np.linspace(cal_dict["SITE_MAP_LATITUDE"] + 5, cal_dict["SITE_MAP_LATITUDE"] - 5, n)
    lons = (cal_dict["SITE_MAP_LONGITUDE"]-0.5) * np.ones(n)
    alts = 110 * np.ones(n)
    lla = np.array([lats, lons, alts]).T

    # Map the satellite track to the station's azimuth and elevation coordinates and
    # image pixels. NOTE: the mapping is not along the magnetic field lines! You need
    # to install IRBEM and then use asilib.lla2footprint() before 
    # lla2azel() is called.
    sat_azel, sat_azel_pixels = asilib.lla2azel(mission, station, lla)

    # Initiate the movie generator function. Any errors with the data will be raised here.
    movie_generator = asilib.plot_movie_generator(
        time_range, mission, station, azel_contours=True, overwrite=True,
        ax=ax[0]
    )

    # Use the generator to get the frames and time stamps to estimate mean the ASI
    # brightness along the satellite path and in a (10x10 km) box.
    frame_data = movie_generator.send('data')

    # Calculate what pixels are in a box_km around the satellite, and convolve it
    # with the frames to pick out the ASI intensity in that box.
    area_box_mask = asilib.equal_area(mission, station, lla, box_km=(20, 20))
    asi_brightness = np.nanmean(frame_data.frames*area_box_mask, axis=(1,2))
    area_box_mask[np.isnan(area_box_mask)] = 0  # To play nice with plt.contour()

    for i, (time, frame, _, im) in enumerate(movie_generator):
        # Note that because we are drawing moving data: ASI image in ax[0] and 
        # the ASI time series + a vertical bar at the frame time in ax[1], we need
        # to redraw everything at every iteration.
        
        # Clear ax[1] (ax[0] cleared by asilib.plot_movie_generator())
        ax[1].clear()
        # Plot the entire satellite track
        ax[0].plot(sat_azel_pixels[:, 0], sat_azel_pixels[:, 1], 'red')
        ax[0].contour(area_box_mask[i, :, :], levels=[0.99], colors=['yellow'])
        # Plot the current satellite position.
        ax[0].scatter(sat_azel_pixels[i, 0], sat_azel_pixels[i, 1], c='red', marker='o', s=50)

        # Plot the time series of the mean ASI intensity along the satellite path
        ax[1].plot(frame_data.time, asi_brightness)
        ax[1].axvline(time, c='k') # At the current frame time.

        # Annotate the station and satellite info in the top-left corner.
        station_str = (
            f'{mission}/{station} '
            f'LLA=({cal_dict["SITE_MAP_LATITUDE"]:.2f}, '
            f'{cal_dict["SITE_MAP_LONGITUDE"]:.2f}, {cal_dict["SITE_MAP_ALTITUDE"]:.2f})'
        )
        satellite_str = f'Satellite LLA=({lla[i, 0]:.2f}, {lla[i, 1]:.2f}, {lla[i, 2]:.2f})'
        ax[0].text(0, 1, station_str + '\n' + satellite_str, va='top', 
                transform=ax[0].transAxes, color='red')
        ax[1].set(xlabel='Time', ylabel='Mean ASI intensity [counts]')

    print(f'Movie saved in {asilib.config["ASI_DATA_DIR"] / "movies"}')