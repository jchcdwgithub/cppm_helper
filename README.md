# About this script
This script is a utility script that parses information from one or more switches, processes that data and outputs the data into tables in an excel workbook.

## Where to place the configuration output data
The script will look for configuration information in the show_files directory. Create a directory for each switch vendor OS that you have data for.
Example: All AOS-CX data should go into a directory called aos-cx. All AOS-S data should go into a directory called aos-s, etc.
Currently only AOS-CX and AOS-S outputs are supported. There should be one file per host and ideally, the file will be named what the hostname is.

## Automatic information gathering
If there is connectivity to the host(s) from the machine where this script will be executing then a hosts.yml file can be created in the main directory.
This is where the cppm_helper.py file resides. List the hosts and their information in the hosts.yml file, again under a specific vendor OS. Currently
only AOS-CX hosts are supported. With this information, the script will SSH into each host listed and gather three pieces of information: show vlan,
show mac-address and show arp. These files will be saved in the show_files directory. Each filename will be the hostname of the host it was derived from.

### hosts.yml example
``
---
- hosts:
  aos-cx:
    - host: 10.10.0.100
      credentials:
        username : admin
        password : aruba123
    - host: 10.10.0.101
      credentials:
        username : admin
        password : aruba12$
``
### Updating the MAC OUI information
The MAC OUI to vendor information is stored in a CSV file stored in the static directory. If this information needs to be updated, upload a new CSV
file of the same name and format to the static folder. Call it MAC_OUI.csv.

## Downloading the script
Either pull the script from github or download it directly through the code button on github.

## First time python environment setup

All the dependencies for this script are found in the requirements.txt file. The command to install these dependencies is:

`python -m pip install -r requirements.txt`

Note that your environment might use python3 and pip3 instead.

## Running the script

Once all the dependencies are installed, run the script using python:

`python cppm_helper.py`