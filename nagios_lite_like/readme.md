Problem:
Rarely, very rarely, random device stops functioning. I discover that few days later when I need something from this or that device.

Typical solution is running Nagios. Nagios can execute list of "checks", keep and track the status of the checks, and alert/execute_some_code if the status passed defined threshold. Nagios is the beast :slight_smile:

However, for a small network it's a mammoth in a crystal shop.
This is variant of Nagios which:

* Runs defined commands per every unit in the smart home and compares results with expected criteria.
* Puts all the results in InfluxDB (or other DB).
* In case of failure of a certain unit it sends email and/or IM (pushbullet, telegram, etc.)
