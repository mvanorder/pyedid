# pyEDID
This is a python library to parse extended display identification data (EDID)!

## Original Author
This library is based on the work of jojonas: https://github.com/jojonas/pyedid

## Changes
* Moved everyhing (except the PnP IDs) in to one file
* Changed all methods to be static class methods (except loading the PnP IDs)
* Added a method (`get_edid`) to get all EDID values as a `dict`
* Removed "get the current monitor EDID if executed as a standalone program" part; executing the library will now output nothing
* Fixed some bitmask calculations on the features and input types
* Added values for the digital and analog features and input types
* Changed timings to `dict`s instead of tuples

## The Future
* There are still quite a few normal EDID fields that are not currently parsed
* All the [EIA/CEA-861](https://en.wikipedia.org/wiki/Extended_Display_Identification_Data#EIA/CEA-861_extension_block) stuff that's after the basic 128 EDID bytes should be considered
* Maybe a way to embed the PnP IDs so the code doesn't rely on an external file; or maybe a way to fetch the list from the Internet
* Some documentation would be nice
* Testing on multiple types of displays would be a good idea
* Set the module up as a proper package

## EDID data format
The EDID data frame format is described in detail on its [Wikipedia page](https://en.wikipedia.org/wiki/Extended_Display_Identification_Data).

## PNP IDs
The CSV file `pnp_ids.csv` contains plug-and-play ids which are maintained by Microsoft and obtained from [this page](http://www.uefi.org/pnp_id_list).
