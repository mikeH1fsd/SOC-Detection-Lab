# Port Scanning Detection with UFW and Threat Intelligence Enrichment using Wazuh Integration

## 1 Scenario Description

### Port Scanning Detection and Threat Intelligence Enrichment (MITRE ATT&CK T1046)

Port Scanning Detection and Threat Intelligence Enrichment (MITRE ATT&CK T1046)

Port scanning is a common reconnaissance technique used by attackers to identify open ports and discover services running on a target system before launching further attacks. This activity is mapped to ```MITRE ATT&CK technique T1046 (Network Service Discovery)```.

In this scenario, an attacker performs a port scanning attack against an Ubuntu server. The Uncomplicated Firewall (UFW) detects and blocks multiple connection attempts from the attacker’s IP address. These firewall events are logged into the system log file and collected by the Wazuh agent for analysis.

To detect suspicious scanning behavior, custom Wazuh correlation rules monitor the frequency of blocked packets from the same source IP. When a large number of blocked connections is observed within a short timeframe, Wazuh generates a high-severity alert indicating a potential port scanning attack.

To further enrich the detection, Wazuh integration is configured to automatically trigger a custom Python script when the detection rule is matched. This script queries the ```VirusTotal API``` to retrieve threat intelligence information about the suspicious IP address, such as reputation score and malicious activity reports.

The VirusTotal response is then parsed and sent back to Wazuh, where additional custom rules analyze the returned JSON data and generate a threat intelligence alert.

This scenario demonstrates how Wazuh can be used not only for detection but also for automated threat intelligence enrichment, helping SOC analysts quickly assess whether suspicious activity originates from known malicious sources.

Workflow:

![](scenarios/port_scanning/images/images/flowportscanning.drawio.png)

## 2 Configuration

🛡️ Scenario: Port Scan Detection with UFW and Threat Intelligence Enrichment using Wazuh Integration

This section describes the configuration steps required to detect port scanning activity using UFW firewall logs and enrich the detection with VirusTotal threat intelligence using Wazuh integration.

**Phase 1: Ubuntu Server Configuration (Agent Side)**

**1. Enable UFW Firewall**

First, enable the UFW firewall to ensure the system can monitor and block unauthorized connection attempts:

```bash
sudo ufw enable
```

Verify the firewall status:

```bash
sudo ufw status
```

**2. Enable UFW Logging**

Next, enable firewall logging so that blocked connection attempts can be recorded for analysis:

```bash
sudo ufw logging high
```

This ensures all blocked packets and suspicious connection attempts are stored in:

```bash
/var/log/ufw.log
```

**3. Configure Wazuh Agent to Collect UFW Logs**

Edit the Wazuh agent configuration file:

```bash
sudo nano /var/ossec/etc/ossec.conf
```

Add the following configuration inside the <ossec_config> section:

```xml
<localfile>
  <log_format>syslog</log_format>
  <location>/var/log/ufw.log</location>
</localfile>
```

This configuration allows the Wazuh agent to monitor UFW firewall logs and forward them to the Wazuh manager for analysis.


**4. Restart Wazuh Agent**

Apply the configuration changes:

```bash
sudo systemctl restart wazuh-agent
```

**Phase 2: Wazuh Manager Configuration (Server Side)**

In this phase, we create custom detection rules to identify port scanning activity based on repeated firewall block events.

**1. Create Port Scan Detection Rules**

Edit the local rules file:

```bash
sudo nano /var/ossec/etc/rules/local_rules.xml
```

Add the following rules:

```xml
<group name="local,portscan">

  <rule id="100030" level="3">
    <if_sid>4100</if_sid>
    <options>no_log</options>
    <description>UFW block base event</description>
  </rule>

  <rule id="100031" level="12" frequency="200" timeframe="60">
    <if_matched_sid>100030</if_matched_sid>
    <same_source_ip />
    <description>Possible Port Scan - 200 blocked packets from same IP in 60s</description>
    <group>attack,portscan,network</group>
  </rule>

</group>
```

Rule logic:

```Rule 100030``` acts as a base rule to normalize UFW block events.

```Rule 100031``` detects possible port scanning when ```200 blocked packets``` from the same IP occur within ```60 seconds```.

The ```<same_source_ip />``` condition ensures correlation is performed on the same attacker IP.

**2. Configure Wazuh Integration**

Wazuh integration allows automatic execution of scripts when specific rules are triggered. In this scenario, it is used to query VirusTotal for IP reputation data.

Edit the Wazuh configuration:

```bash
sudo nano /var/ossec/etc/ossec.conf
```

Add:

```xml
<integration>
  <name>custom-vtip</name>
  <api_key>Your_VirusTotal_API_Key</api_key>
  <rule_id>100031</rule_id>
  <alert_format>json</alert_format>
</integration>
```

This configuration ensures that when ```rule 100031``` is triggered, Wazuh executes the custom integration script.

**3. Create Custom VirusTotal Integration Script**

Create the Python integration script:

```bash
sudo nano /var/ossec/integrations/custom-vtip
```

The integration script can be found here:

👉 [VirusTotal Integration Script](custom-vtip.py)

The script performs the following actions:

- Extracts the attacker IP from the Wazuh alert 
- Queries the VirusTotal API
- Retrieves IP reputation data
- Returns the result in JSON format


***Important requirements:***

File must be placed inside:
```bash
/var/ossec/integrations/
```
***File name must follow format:***

```custom-<name>```

Make the script executable:
```bash
sudo chmod +x /var/ossec/integrations/custom-vtip
```
***Assign ownership to root and wazuh group:***

```bash
chown root:wazuh /var/ossec/integrations/custom-vtip
```


**4. Create Rules to Process VirusTotal Results**

Add rules to analyze the JSON output returned by the integration script:

```xml
<group name="virustotal_ip,custom,threat_intel,ip_reputation">

  <rule id="100569" level="12">
    <decoded_as>json</decoded_as>
    <field name="integration">vtip_custom</field>
    <description>IP Reputation check from VirusTotal integration</description>
  </rule>

</group>
```

This rule ensures Wazuh generates an alert when VirusTotal enrichment data is received.

**5. Restart Wazuh Manager**

Apply all changes:

```bash
sudo systemctl restart wazuh-manager
```

## 3 Attack Simulation & Verification

**3 Attack Simulation & Verification**

After completing the configuration of UFW logging, Wazuh detection rules, and VirusTotal integration, a port scanning attack is simulated to verify that the detection pipeline and threat intelligence enrichment mechanism function correctly.

**Attack Simulation**

To simulate reconnaissance activity, an attacker machine performs a network scan against the Ubuntu server using Nmap:

Example command used:

```bash
nmap <Ubuntu_Server_IP>
```

This scan attempts to discover open ports by sending multiple connection requests, which are detected and blocked by UFW. These events are logged and forwarded to Wazuh for analysis.

**Verification Results**

![](scenarios/port_scanning/images/images/image.png)

At this stage, no suspicious activity has been generated and the Wazuh dashboard shows no security alerts related to port scanning.

![](scenarios/port_scanning/images/images/image2.png)

Before the attack simulation, the VirusTotal dashboard shows only 18 API requests.

![](scenarios/port_scanning/images/images/image3.png)

The attacker machine starts scanning the Ubuntu server using Nmap. This generates multiple blocked connection attempts which are recorded by UFW.

![](scenarios/port_scanning/images/images/image4.png)
![](scenarios/port_scanning/images/images/image5.png)

Wazuh detects a high number of blocked packets from the same source IP within a short timeframe and triggers rule 100031, generating a high severity alert.


![](scenarios/port_scanning/images/images/image6.png)
![](scenarios/port_scanning/images/images/image7.png)

After rule 100031 is triggered, Wazuh integration automatically executes the custom script to query VirusTotal. The returned IP reputation data is processed by rule 100569 and displayed in the dashboard.


Since the IP address used in this lab belongs to a private network range, VirusTotal classifies it as benign, which is expected behavior.

![](scenarios/port_scanning/images/images/image8.png)

The VirusTotal request counter increased from 18 to 36 requests, confirming that the integration script successfully performed API queries after the detection rule was triggered.


## 4 Conclusion

The experiment demonstrates that Wazuh, when combined with UFW firewall logs and custom detection rules, can effectively detect port scanning activities ```(MITRE ATT&CK T1046)```.

During the attack simulation, when the attacker performed an Nmap scan against the Ubuntu server, UFW successfully logged and blocked the suspicious connection attempts. These logs were forwarded to Wazuh, where custom correlation rules identified abnormal connection patterns from the same source IP and generated high-severity alerts.

Furthermore, the integration feature of Wazuh proved valuable by automatically triggering a custom VirusTotal lookup script when the port scanning rule was matched. This allowed the system to enrich detection alerts with external threat intelligence data, providing additional context about the attacker IP.

Although the IP address used in this lab belonged to a private network and was classified as benign, the successful API queries confirmed that the enrichment workflow operates correctly and can be applied to real-world scenarios involving public malicious IP addresses.

This scenario highlights the effectiveness of combining firewall telemetry, SIEM correlation rules, and automated threat intelligence enrichment to improve detection accuracy and provide better context for security analysis. Such an approach can be practically implemented in production SOC environments to enhance threat visibility and accelerate incident investigation.

## References

https://wildwolf.name/wazuh-and-ufw-in-ubuntu-24-04/

https://github.com/wazuh/wazuh/tree/v4.14.3/src

https://documentation.wazuh.com/current/user-manual/manager/integration-with-external-apis.html
