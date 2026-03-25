# Process Injection Detection Lab

## 1 Scenario Description

Process injection is a common technique used by malware to hide malicious activity by executing code inside legitimate processes.

In this scenario, a malicious executable injects payload into notepad.exe using CreateRemoteThread.

## 2 Configuration

🛡️ Scenario: Process Injection Detection with Wazuh & Sysmon
This guide outlines the configuration steps to detect Process Injection (T1055.001) by integrating Wazuh with Windows Sysmon.

Phase 1: Windows Client Configuration (Agent Side)
1. Install Sysmon
Open PowerShell as Administrator and run the following commands to download and install Sysmon:

PowerShell
# Create a directory and download Sysinternals tools
New-Item -ItemType Directory -Force -Path "C:\Sysinternals"
cd C:\Sysinternals
# Note: You might need to download the Sysmon binary specifically if the bundle is not used
2. Download and Apply Sysmon Configuration
We use the popular sysmon-config from SwiftOnSecurity for comprehensive logging:

PowerShell
# Download the configuration file
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/SwiftOnSecurity/sysmon-config/master/sysmonconfig-export.xml" -OutFile ".\sysmonconfig.xml"

# Install Sysmon with the config file
.\sysmon64.exe -accepteula -i .\sysmonconfig.xml
3. Configure Wazuh Agent to Collect Sysmon Logs
Edit the Wazuh Agent configuration file located at C:\Program Files (x86)\ossec-agent\ossec.conf. Add the following block within the <ossec_config> section:

XML
<localfile>
    <location>Microsoft-Windows-Sysmon/Operational</location>
    <log_format>eventchannel</log_format>
</localfile>
4. Restart Wazuh Agent
Apply the changes by restarting the service:

PowerShell
Restart-Service -Name wazuh
Phase 2: Wazuh Manager Configuration (Server Side)
On the Wazuh Server, we need to create custom rules to trigger alerts based on Sysmon Event ID 10 (Process Access).

1. Edit Local Rules
Add the following rules to /var/ossec/etc/rules/local_rules.xml:

XML
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
2. Restart Wazuh Manager
Run the following command to apply the new rules:

Bash
systemctl restart wazuh-manager
