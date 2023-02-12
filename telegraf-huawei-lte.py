from argparse import ArgumentParser
from huawei_lte_api.Client import Client
from huawei_lte_api.Connection import Connection

p=ArgumentParser()
p.add_argument('url',type=str)
p.add_argument('--u',type=str)
p.add_argument('--p',type=str)
args=p.parse_args()

def gather_data(connection):
    client = Client(connection)
    deviceSignal = client.device.signal()
    deviceInformation = client.device.information()
    smsConfig = client.sms.config()
    smsCount = client.sms.sms_count()
    totalTrafficStatistics = client.monitoring.traffic_statistics()
    totalMonthStatistics = client.monitoring.month_statistics()
    netCurrentPlan = client.net.current_plmn()
    monitoringStatus = client.monitoring.status()
    return deviceSignal, deviceInformation, smsConfig, smsCount, totalTrafficStatistics, totalMonthStatistics, netCurrentPlan, monitoringStatus

with Connection(args.url, username=args.u, password=args.p) as connection:
    deviceSignal, deviceInformation, smsConfig, smsCount, totalTrafficStatistics, totalMonthStatistics, netCurrentPlan, monitoringStatus = gather_data(connection)

# Pull chosen keys
keys = {
    "imei": deviceInformation.get('Imei'),
    "number": smsConfig.get('Sca'),
    "operator": netCurrentPlan.get('FullName'),
    "band": deviceSignal.get('band')
}
# Pull chosen data
data = {
    "band": deviceSignal.get('band'),
    "uptime": deviceInformation.get('uptime'),
    "enodeb_id": deviceSignal.get('enodeb_id'),
    "unreadsms": smsCount.get('LocalInbox'),
    "currentdownload": totalTrafficStatistics.get('CurrentDownload'),
    "currentupload": totalTrafficStatistics.get('CurrentUpload'),
    "totaldownload": totalTrafficStatistics.get('TotalDownload'),
    "totalupload": totalTrafficStatistics.get('TotalUpload'),
    "nsa_status": monitoringStatus.get('EndcStatus')
}
# Pull chosen signal data
signal = {
    "rsrq": deviceSignal.get('rsrq').replace("dB", ""),
    "rsrp": deviceSignal.get('rsrp').replace("dBm", ""),
    "rssi": deviceSignal.get('rssi').replace("dBm", ""),
    "sinr": deviceSignal.get('sinr').replace("dB", ""),
}

Line1Data = "ltemodem,imei="+keys["imei"]+",number="+keys["number"]+",operator="+keys["operator"]+" "
Line2Signal = "ltemodem,imei="+keys["imei"]+",number="+keys["number"]+",operator="+keys["operator"]+",band="+keys["band"]+" "

for key, value in data.items():
    Line1Data += key + "=" + value + ","
for key, value in signal.items():
    Line2Signal += key + "=" + value + ","

print(Line1Data.strip(","))
print(Line2Signal.strip(","))
