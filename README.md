## Intelligent Power Saving Solution

Intelligent Power Saving Solutionis tstarted as internal project to gather the power consumption from ASR9000 and NCS5500 devices in Cisco CX lab and analyze it to verify how much energy could be saved. The idea is to power-off unused slices on devices by verifying port status.

The power saving method is to "shutdown" unused ports and "power-off"slices on line cards.

There is static YAML file contains the list of line cards which architecture allow such actions and port to NPU (Network Processing Unit) mapping.

There are separate platform related scripts using NetConf with ncclient library and Netmiko library and module to process captured information depending on the platform data. There are also common data gathering module and module implementing API access. The gathered data are saved in the JSON format and then processed separately to generate static HTML file as report for the pilot phase.

For business justification, real data collected from CX tickets for the ASR9000 and NCS5500 platform utilizing internal API back-end providing access to the CX ticketing system allowing to extract platform related data and save on back-end MongoBD for further processing.

The final outcome of the pilot phase saved in JSON format as raw data and generated HTML report.

