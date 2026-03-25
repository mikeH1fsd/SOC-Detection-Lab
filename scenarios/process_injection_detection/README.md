# Process Injection Detection Lab

## 1 Scenario Description

### Process Injection Detection (T1055.001)

Process Injection is a stealthy technique commonly used by malware to execute malicious code within the context of a legitimate process, helping attackers evade detection.

In this scenario, a malicious executable (main.exe) injects a payload into a trusted Windows process — notepad.exe — by calling the CreateRemoteThread API. This allows the malicious code to execute with the privileges and context of the legitimate process, making detection significantly more difficult.

Sysmon (Event ID 8) captures the remote thread creation event, which is then forwarded to Wazuh for analysis. Custom Wazuh rules are triggered to detect this suspicious behavior and generate a high-severity alert on the dashboard.

## 2 Configuration

🛡️ Scenario: Process Injection Detection with Wazuh & Sysmon

This guide outlines the configuration steps to detect Process Injection (T1055.001) by integrating Wazuh with Windows Sysmon.

**Phase 1**: Windows Client Configuration (Agent Side)
1. Install Sysmon
Open PowerShell as Administrator and run the following commands to download and install Sysmon:

```
Download-SysInternalsTools C:\Sysinternals 
```

2. Download and Apply Sysmon Configuration
We use the popular sysmon-config from SwiftOnSecurity for comprehensive logging:

```
# Download the configuration file
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/SwiftOnSecurity/sysmon-config/master/sysmonconfig-export.xml" -OutFile ".\sysmonconfig.xml"

# Install Sysmon with the config file
.\sysmon64.exe -accepteula -i .\sysmonconfig.xml
```

3. Configure Wazuh Agent to Collect Sysmon Logs
Edit the Wazuh Agent configuration file located at ```C:\Program Files (x86)\ossec-agent\ossec.conf```. Add the following block within the <ossec_config> section:

```
<localfile>
    <location>Microsoft-Windows-Sysmon/Operational</location>
    <log_format>eventchannel</log_format>
</localfile>
```

4. Restart Wazuh Agent
Apply the changes by restarting the service:

```
Restart-Service -Name wazuh
```
**Phase 2**: Wazuh Manager Configuration (Server Side)

On the Wazuh Server, we create custom rules to detect suspicious process injection behavior based on **Sysmon Event ID 8 (CreateRemoteThread)**.

1. Edit Local Rules
Add the following rules to ```/var/ossec/etc/rules/local_rules.xml```:

```XML
<group name="windows,sysmon">
  <rule id="100200" level="12">
    <if_sid>61610</if_sid>
    <description>Possible process injection activity detected from "$(win.eventdata.sourceImage)" on "$(win.eventdata.targetImage)"</description>
    <mitre>
      <id>T1055.001</id>
    </mitre>
  </rule>

  <rule id="100100" level="0">
    <if_sid>100200</if_sid>
    <field name="win.eventdata.sourceImage" type="pcre2">(C:\\\\Windows\\\\system32)|chrome.exe</field>
    <description>Ignore noise from Windows system binaries and Chrome</description>
  </rule>
</group>
```
2. Restart Wazuh Manager
Run the following command to apply the new rules:

```Bash
systemctl restart wazuh-manager
```

## 3. Attack Simulation & Verification

After completing the configuration on both the Windows Agent and Wazuh Manager, we simulate the process injection attack to verify that the detection rule works as expected.

![](https://github.com/mikeH1fsd/SOC-Detection-Lab/blob/main/scenarios/process_injection_detection/images/image.png)
Dashboard before attack (no alerts)

![](https://github.com/mikeH1fsd/SOC-Detection-Lab/blob/main/scenarios/process_injection_detection/images/image2.png)
Executing malicious file main.exe
