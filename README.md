# Israel-supermarket-chains-tool
Easy tool helping data-engineers and developers grabbing updated food prices data of the biggest supermarket chains in Israel.


## Goal
The main goal of the tool, is improving accessibility to the supermarket chains prices data,
to help developing future apps that will encourge competitions between different supermarket chains.
Which will help fighting the cost of living in Israel.

## Dependencies
None, all you need is Python 3.8 standard library.

## Chains supported
* Shufersal
* Rami Levi
* Victory
* Keshet Teamim
* Osher Ad
* Mega


## license
This project is licensed under the terms of the MIT license.

## How to use
<pre>
usage: data.py [-h] [-c CHAIN_NAME] [-f FORCE]

Open-Source tool to download israeli food chains prices data.

optional arguments:
  -h, --help            show this help message and exit
  -c CHAIN_NAME, --chain_name CHAIN_NAME
                        chain name to get data from, options: (ramilevi, shufersal, victory, keshet-teamim, osher-ad,mega, all)
  -f FORCE, --force FORCE
                        Force downloding data` even if data is already up to date.
</pre>

## To do List
* allow custom chain store data selection
* support more supermarkets chain webs
