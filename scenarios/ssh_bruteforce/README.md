# SSH Brute Force Detection and Automated IP Blocking with Wazuh Active Response

## 1 Scenario Description

### SSH Brute Force Detection (MITRE ATT&CK T1110)

SSH brute force attacks are a common technique used by attackers to gain unauthorized access to server by repeatedly attempting different password combinations. These attacks typically generate multiple authentication failures within a short period of time, which can be detected through system authentication logs.

In this scenario, an Ubuntu Server is configured with a Wazuh agent to monitor SSH authentication activity. An attacker machine simulates a brute force attack by performing multiple failed SSH login attempts against the target server.

The Wazuh agent collects authentication logs from `/var/log/auth.log` and forwards them to the Wazuh Manager for analysis. Wazuh default rule **2502** is used to detect multiple SSH authentication failures and generate a security alert.

To enhance the defensive capability, Wazuh Active Response is configured to automatically block the attacker's IP address once the detection rule is triggered. The system executes a firewall-drop response to prevent further SSH connection attempts from the malicious source.

Detection and response flow:

![](https://github.com/mikeH1fsd/SOC-Detection-Lab/blob/main/scenarios/ssh_bruteforce/images/flow.jpg)

## 2 Active Response Configuration

To automatically block attackers performing SSH brute force attempts, Wazuh Active Response is configured to trigger a firewall block when rule **2502** is detected.

### Configure Active Response on Wazuh Manager

Edit the Wazuh manager configuration file:

```bash
sudo nano /var/ossec/etc/ossec.conf
```
Add the following configuration inside the ```<ossec_config>``` section:
```xml
<active-response>
  <disabled>no</disabled>
  <command>firewall-drop</command>
  <location>local</location>
  <rules_id>2502</rules_id>
  <timeout>600</timeout>
</active-response>
```

Run the following command to apply the configuration:
```bash
sudo systemctl restart wazuh-manager
```
## 3 Attack Simulation & Verification

After completing the configuration, we simulate an SSH brute force attack to verify that Wazuh can successfully detect the attack and automatically block the attacker's IP using Active Response.

![](https://github.com/mikeH1fsd/SOC-Detection-Lab/blob/main/scenarios/ssh_bruteforce/images/image.png)
At the beginning, the Wazuh dashboard shows no security alerts, confirming that the system is in a normal state before the attack simulation.

![](https://github.com/mikeH1fsd/SOC-Detection-Lab/blob/main/scenarios/ssh_bruteforce/images/image2.png)

From the attacker machine, we perform an SSH brute force attack against the Ubuntu server using Hydra:

```bash
hydra -l ubuntu -P rockyoumini.txt ssh://<target-ip>
```

![](https://github.com/mikeH1fsd/SOC-Detection-Lab/blob/main/scenarios/ssh_bruteforce/images/image3.png)
After several failed login attempts, Wazuh detects the suspicious activity using the default rule 2502. A high severity alert is generated on the Wazuh dashboard.

![](https://github.com/mikeH1fsd/SOC-Detection-Lab/blob/main/scenarios/ssh_bruteforce/images/image4.png)
Once the alert is triggered, Wazuh automatically executes the Active Response module. The firewall-drop script is triggered to block the attacker's IP address

![](https://github.com/mikeH1fsd/SOC-Detection-Lab/blob/main/scenarios/ssh_bruteforce/images/image5.png)

To verify the effectiveness of the response, we attempt to connect from the attacker machine again. The attacker can no longer communicate with the victim server, and even ICMP ping requests fail.

This confirms that the attacker's IP has been successfully blocked.

## 4 Conclusion

This lab demonstrates how Wazuh can effectively detect SSH brute force attacks and automatically respond to potential threats using the Active Response feature.

During the attack simulation, multiple failed SSH login attempts generated authentication logs that were successfully collected by the Wazuh agent. The Wazuh manager analyzed these logs and triggered rule **2502**, generating a high severity alert indicating suspicious authentication activity.

Following the detection, the Active Response mechanism automatically executed the firewall-drop script to block the attacker's IP address. This prevented further connection attempts and demonstrated Wazuh’s capability to not only detect but also actively mitigate ongoing attacks.

This scenario highlights the importance of combining log monitoring, detection rules, and automated response to strengthen security operations. Such an approach can significantly reduce response time and improve the overall security posture of production environments.

## References

https://documentation.wazuh.com/current/proof-of-concept-guide/block-malicious-actor-ip-reputation.html

https://documentation.wazuh.com/current/user-manual/capabilities/active-response/ar-use-cases/blocking-ssh-brute-force.html
