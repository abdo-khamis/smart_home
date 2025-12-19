import subprocess

def get_ssid():
    try:
        # Run Windows command to get Wi-Fi SSID
        output = subprocess.check_output(["netsh", "wlan", "show", "interfaces"],encoding="utf-8", errors="ignore")
        for line in output.splitlines():
            if "SSID" in line and "BSSID" not in line:
                ssid = line.split(":")[1].strip()
              # SmartHome-Wifi  
              # Orange_AB2F
                if ssid == "SmartHome-Wifi":
                    return True
                else:
                    return False
        return None
    except subprocess.CalledProcessError:
        return None
    