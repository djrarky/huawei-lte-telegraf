# Telegraf Importer for Huawei 4G / 5G Routers
Telegraf importer for the Huawei series of LTE/5G routers. This should be compatible with most, if not all Huawei AI Life compatible routers. 

For a full compatibility list, see the API maintainers list here: https://github.com/Salamek/huawei-lte-api/#tested-on

## Example
![Grafana Dashboard Screenshot](https://user-images.githubusercontent.com/10834935/218320610-b363ada8-d5d5-4aa3-9de1-c712f5312145.png)

## API Installation

### PIP (pip3 on some distros)
`pip install -r requirements.txt`

### Repository
You can also use these repositories maintained by [Salamek](https://github.com/Salamek/huawei-lte-api/)    

- [Debian / Ubuntu](https://github.com/Salamek/huawei-lte-api/#debian-and-derivatives)
- [Archlinux](https://github.com/Salamek/huawei-lte-api/#archlinux)
- [Gentoo](https://github.com/Salamek/huawei-lte-api/#gentoo)
 
## Configure

### Telegraf Setup
```
[[inputs.exec]]
  ## Commands array
  commands = ["python3 location/telegraf-huawei-lte.py 'http://username:password@IP Address/'"]

  ## measurement name suffix (for separating different commands)
  name_suffix = "_mycollector"

  ## Data format to consume.
  data_format = "influx"
```
### Grafana Setup

Example dashboard [config](/examples/grafana.json)

Guage values taken from: https://wiki.teltonika-networks.com/view/Mobile_Signal_Strength_Recommendations
