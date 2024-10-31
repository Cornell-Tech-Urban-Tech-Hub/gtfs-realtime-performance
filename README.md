gtfs-realtime-performance
==============================

This library makes it easy to calculate transity performance statistics (e.g., segment speeds, bus bunching) using archival GTFS-realtime data. It is intended to be used in conjuction with the GTFS-realtime archiving tool being developed in [gtfs-realtime-capsule](https://github.com/tsdataclinic/gtfs-realtime-capsule). 

### Project Organization

Currently, the main functionalities enabled by this repository are as follows:

1.  Segmenting GTFS static feeds into shape segments defined by pairs of consecutive stops (`src/gtfs_segments.py`)
2.  Calculation of trip-level speeds along these segments using archival GTFS-realtime data (`src/speeds.py`)

We have also included a number of utility functions to simplify the process of working with the GTFS data as well as our outputs. In the future, we will add more performance statistics and the ability to segment routes based on OSM street segments in addition to the static-feed segments currently implemented.

### Notebooks

This repository contains a number of notebooks that contain figures, tables, and maps created using our speed estimates. Some of these are old and messy - I'd reccommend looking at `notebooks/basic_plots_and_mta.ipynb` for comparisons of our speeds to speeds published by the MTA and at `notebooks/holidays.ipynb` to see bus speed comparisons on holidays.

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
