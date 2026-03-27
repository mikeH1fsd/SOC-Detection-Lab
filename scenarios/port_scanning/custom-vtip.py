#!/var/ossec/framework/python/bin/python3

import sys
import json
import requests
from socket import socket, AF_UNIX, SOCK_DGRAM

SOCKET_ADDR = "/var/ossec/queue/sockets/queue"

ALERT_INDEX = 1
APIKEY_INDEX = 2


def main(args):
    alert_file = args[ALERT_INDEX]
    apikey = args[APIKEY_INDEX]

    with open(alert_file) as f:
        alert = json.load(f)

    if "data" not in alert or "srcip" not in alert["data"]:
        sys.exit(0)

    ip = alert["data"]["srcip"]

    vt_data = query_vt_ip(ip, apikey)

    if not vt_data:
        sys.exit(0)

    msg = build_message(alert, ip, vt_data)

    send_msg(msg, alert["agent"])

def query_vt_ip(ip, apikey):
    url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"

    headers = {
        "x-apikey": apikey
    }

    try:
        r = requests.get(url, headers=headers)

        if r.status_code != 200:
            return None

        data = r.json()
        return data.get("data", {}).get("attributes", {})

    except Exception:
        return None


def build_message(alert, ip, vt_data):

    stats = vt_data.get("last_analysis_stats", {})
    harmless = stats.get("harmless", 0)
    malicious = stats.get("malicious", 0)
    suspicious = stats.get("suspicious", 0)
    undetected = stats.get("undetected", 0)
    malicious_count = stats.get("malicious", 0)
    suspicious_count = stats.get("suspicious", 0)

    malicious = 1 if malicious_count > 0 else 0

    output = {
        "integration": "vtip_custom",
        "srcip": ip,
        "virustotal": {
            "source": {
                "alert_id": alert["id"],
                "srcip": ip
            },
            "malicious": malicious,
            "harmless": harmless,
            "malicious": malicious,
            "suspicious": suspicious,
            "undetected": undetected,
            "malicious_vendor_count": malicious_count,
            "suspicious_vendor_count": suspicious_count,
            "country": vt_data.get("country"),
            "as_owner": vt_data.get("as_owner"),
            "reputation": vt_data.get("reputation"),
            "permalink": f"https://www.virustotal.com/gui/ip-address/{ip}"
        }
    }

    return output


def send_msg(msg, agent):
    if not agent or agent["id"] == "000":
        string = f'1:virustotal_ip:{json.dumps(msg)}'
    else:
        location = f'[{agent["id"]}] ({agent["name"]}) {agent.get("ip","any")}'
        location = location.replace("|", "||").replace(":", "|:")
        string = f'1:{location}->virustotal_ip:{json.dumps(msg)}'

    sock = socket(AF_UNIX, SOCK_DGRAM)
    sock.connect(SOCKET_ADDR)
    sock.send(string.encode())
    sock.close()


if __name__ == "__main__":
    main(sys.argv)
