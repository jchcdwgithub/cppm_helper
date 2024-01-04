# About the scripts

There are two scripts included in this repository. One is cppm_helper.py and the other is migration_helper.py.

The cppm_helper script is a utility script that parses information from one or more switches, processes that data and outputs the data into tables in an excel workbook.
Specifically, the MAC table, ARP entries and VLAN information are parsed and aggregated into a more convenient output.

The migration_helper script works similarly to the cppm_helper script but it parses different information and aggregates them into tables which are then saved to an excel file.

## Where to place the configuration output data
Both scripts will look for configuration information in a directory called show_files (exact spelling). Create the show_files directory in the same folder where the cppm_helper.py file is then create a directory for each switch vendor OS that you have data for.
Currently the cppm_helper script only AOS-CX and AOS-S outputs are supported. The migration_helper script supports AOS-CX, AOS-S, IOS-XE and NX-OS. There should be one file per host and ideally, the file will be named what the hostname is.
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

Note that you do not have to create any folders if you are doing automatic information gathering. The show_files and OS subfolders will be created for you.

The switch OS names need to be exact. Currently supported folder names are: aos-cx, aos-s, ios-xe and nx-os. The script will skip any other files or folders in this directory.

## Automatic information gathering
If there is connectivity to the host(s) from the machine where the scripts will be executing then a hosts.yml file can be created in the main directory.
This is where the cppm_helper.py and migration_helper.py files reside. List the hosts and their information in the hosts.yml file, again under a specific vendor OS. Currently the cppm_helper script
only AOS-CX and AOS-S hosts are supported while the migration_helper script also supports IOS-XE and NX-OS hosts. With this information, the cppm_helper script will SSH into each host listed and gather three pieces of information: show vlan,
show mac-address and show arp. These files will be saved in the show_files directory. Each filename will be the hostname of the host it was derived from.
The migration_helper script runs a variety of show commands which are specific to the OS. Generally CDP, LLDP, module, VLANs, version, inventory and other information will be gathered.

### hosts.yml example
```
---
hosts:
  aos-cx:
  - host: 10.10.0.100
      credentials:
        username : admin
        password : aruba123
  aos-s:
  - host: 10.10.0.101
      credentials:
        username : admin
        password : aruba12$
```
### Updating the MAC OUI information
The MAC OUI to vendor information is stored in a CSV file stored in the static directory. If this information needs to be updated, upload a new CSV
file of the same name and format to the static folder. Call it MAC_OUI.csv.

## Downloading the scripts
If you have git installed you can clone this repository directly from github:

`git clone https://github.com/jchcdwgithub/cppm_helper.git`

You can also download the code if you visit the github page.

If you already downloaded the script from github, you can issue a git pull to update the script:

`git pull https://github.com/jchcdwgithub/cppm_helper`

## First time python environment setup

All the dependencies for this script are found in the requirements.txt file. The command to install these dependencies is:

`python -m pip install -r requirements.txt`

Note that your environment might use python3 and pip3 instead. You might also require escalated privileges (sudo mode) to install these dependencies.

## Running the scripts

Once all the dependencies are installed, run the script using python:

`python cppm_helper.py` or `python migration_helper.py`