import telnetlib as tn
import time as t
import os
import sys
import json
import re

modem_ip = sys.argv[1]
modem_username = sys.argv[2]
modem_password = sys.argv[3]

class ParsedStats:
    def __init__(self, conn_stats_output, system_uptime):
        conn_stats_output_split = conn_stats_output.decode().split("\r\n")
        if len(conn_stats_output_split) == 176:
            self.connection_up = True
            max_line = conn_stats_output_split[5]
            match = re.search(r"Upstream rate = (\d+) Kbps, Downstream rate = (\d+) Kbps", max_line)
            self.max_up = int(match.group(1))
            self.max_down = int(match.group(2))            
            current_line = conn_stats_output_split[6].replace("Bearer:\t0, Upstream rate = ", "")
            current_split = current_line.split(", Downstream rate = ")
            self.current_up = int(current_split[0].replace(" Kbps", ""))
            self.current_down = int(current_split[1].replace(" Kbps", ""))
            snr_line = conn_stats_output_split[16].replace("SNR (dB):\t ", "")
            snr_split = snr_line.split("\t\t ")
            self.snr_down = float(snr_split[0])
            self.snr_up = float(snr_split[1])
            attn_line = conn_stats_output_split[17].replace("Attn(dB):\t ", "")
            attn_split = attn_line.split("\t\t ")
            self.attn_down = float(attn_split[0])
            self.attn_up = float(attn_split[1])
            pwr_line = conn_stats_output_split[18].replace("Pwr(dBm):\t ", "")
            pwr_split = pwr_line.split("\t\t ")
            self.pwr_down = float(pwr_split[0])
            self.pwr_up = float(pwr_split[1])
            interleaving_line = conn_stats_output_split[28].replace("D:\t\t", "")
            interleaving_split = interleaving_line.split("\t\t")
            self.int_down = int(interleaving_split[0])
            self.int_up = int(interleaving_split[1])
            err_secs_line = conn_stats_output_split[98].replace("ES:\t\t", "")
            err_secs_split = err_secs_line.split("\t\t")
            self.err_secs_up = int(err_secs_split[0])
            self.err_secs_down = int(err_secs_split[1])
            serious_err_secs_line = conn_stats_output_split[99].replace("SES:\t\t", "")
            serious_err_secs_split = serious_err_secs_line.split("\t\t")
            self.serious_err_secs_up = int(serious_err_secs_split[0])
            self.serious_err_secs_down = int(serious_err_secs_split[1])
            unavailable_secs_line = conn_stats_output_split[100].replace("UAS:\t\t", "")
            unavailable_secs_split = unavailable_secs_line.split("\t\t")
            self.unavailable_secs_up = int(unavailable_secs_split[0])
            self.unavailable_secs_down = int(unavailable_secs_split[1])
            self.available_secs = int(conn_stats_output_split[101].replace("AS:\t\t", ""))
            DSLuptime = conn_stats_output_split[166].replace("Since Link time = ", "")
            days = hours = minutes = seconds = 0
            components = DSLuptime.split()
            for i in range(len(components)):
                if i > 0 and components[i-1].isdigit():
                    if "day" in components[i]:
                        days += int(components[i-1])
                    elif "hour" in components[i]:
                        hours += int(components[i-1])
                    elif "min" in components[i]:
                        minutes += int(components[i-1])
                    elif "sec" in components[i]:
                        seconds += int(components[i-1])
            days = days
            hours = hours
            mins = minutes
            seconds = seconds
            self.DSLuptimeSeconds = (days * 24 * 60 * 60) + (hours * 60 * 60) + (minutes * 60) + seconds
        else:
            self.connection_up = False
        system_uptime_split = system_uptime.decode().split("\r\n")
        self.system_uptime = float(system_uptime_split[1].split(" ")[0]) 

def main():
    parsed_stats = retrieve_stats()
    influxdb_line = format_influxdb_line(parsed_stats)
    print(influxdb_line)

def retrieve_stats():
    try:
        tnconn = tn.Telnet(modem_ip)
        tnconn.read_until(b"Login:")
        tnconn.write("{0}\n".format(modem_username).encode())
        tnconn.read_until(b"Password:")
        tnconn.write("{0}\n".format(modem_password).encode())
        tnconn.read_until(b"ATP>")
        tnconn.write(b"sh\n")
        tnconn.read_until(b"#")
        tnconn.write(b"xdslcmd info --stats\n")
        stats_output = tnconn.read_until(b"#")
        tnconn.write(b"cat /proc/uptime\n")
        system_uptime = tnconn.read_until(b"#")
        parsed_stats = ParsedStats(stats_output, system_uptime)
        return parsed_stats
    except Exception:
        raise

def format_influxdb_line(parsedStats):
    try:
        if parsedStats.connection_up:
            tags = f"modem_ip={modem_ip}"
            fields = f"AttDown={parsedStats.attn_down},AttnUp={parsedStats.attn_up},AvailableSecs={parsedStats.available_secs},CurrDown={parsedStats.current_down},CurrUp={parsedStats.current_up},ErrSecsDown={parsedStats.err_secs_down},ErrSecsUp={parsedStats.err_secs_up},InterleavingDown={parsedStats.int_down},InterleavingUp={parsedStats.int_up},MaxDown={parsedStats.max_down},MaxUp={parsedStats.max_up},PwrDown={parsedStats.pwr_down},PwrUp={parsedStats.pwr_up},SeriousErrSecsDown={parsedStats.serious_err_secs_down},SeriousErrSecsUp={parsedStats.serious_err_secs_up},SNRDown={parsedStats.snr_down},SNRUp={parsedStats.snr_up},SystemUptime={parsedStats.system_uptime},UnavailableSecsDown={parsedStats.unavailable_secs_down},UnavailableSecsUp={parsedStats.unavailable_secs_up},DSLuptime={parsedStats.DSLuptimeSeconds}"
            return f"dslstats,{tags} {fields}"
    except Exception:
        raise

main()
