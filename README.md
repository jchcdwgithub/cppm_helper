# About this script
This script is a utility script that parses information from one or more switches, processes that data and outputs the data into tables in an excel workbook.
Specifically, the MAC table, ARP entries and VLAN information are parsed and aggregated into a more convenient output.

## Where to place the configuration output data
The script will look for configuration information in a directory called show_files (exact spelling). Create the show_files directory in the same folder where the cppm_helper.py file is then create a directory for each switch vendor OS that you have data for.
Currently only AOS-CX and AOS-S outputs are supported. There should be one file per host and ideally, the file will be named what the hostname is.
Ex.
```
> show_files
    > aos-cx
       host1.txt
       host2.txt
    > aos-s
       host3.txt
       host4.txt
```

## Automatic information gathering
If there is connectivity to the host(s) from the machine where this script will be executing then a hosts.yml file can be created in the main directory.
This is where the cppm_helper.py file resides. List the hosts and their information in the hosts.yml file, again under a specific vendor OS. Currently
only AOS-CX hosts are supported. With this information, the script will SSH into each host listed and gather three pieces of information: show vlan,
show mac-address and show arp. These files will be saved in the show_files directory. Each filename will be the hostname of the host it was derived from.

### hosts.yml example
```
---
hosts:
  aos-cx:
  - host: 10.10.0.100
      credentials:
        username : admin
        password : aruba123
  - host: 10.10.0.101
      credentials:
        username : admin
        password : aruba12$
```
### Updating the MAC OUI information
The MAC OUI to vendor information is stored in a CSV file stored in the static directory. If this information needs to be updated, upload a new CSV
file of the same name and format to the static folder. Call it MAC_OUI.csv.

## Downloading the script
If you have git installed you can clone this repository directly from github.
`git clone https://github.com/jchcdwgithub/cppm_helper.git`
You can also download the code if you visit the github page.

## First time python environment setup

All the dependencies for this script are found in the requirements.txt file. The command to install these dependencies is:

`python -m pip install -r requirements.txt`

Note that your environment might use python3 and pip3 instead. You might also require escalated privileges (sudo mode) to install these dependencies.

## Running the script

Once all the dependencies are installed, run the script using python:

`python cppm_helper.py`