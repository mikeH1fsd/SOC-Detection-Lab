# Blue Team Detection Engineering Lab using Wazuh SIEM

## Overview

This repository showcases practical SOC detection engineering labs built using Wazuh SIEM. The project focuses on detecting common attack techniques by analyzing system and security logs, building detection rules, and understanding attacker behavior through real attack simulations.

The objective is to strengthen hands-on skills in security monitoring, threat detection, and incident analysis within a SOC environment.

## Lab Architecture

The lab environment was built using VMware Workstation and consists of multiple virtual machines simulating a small enterprise network.

The environment includes:

• **Wazuh Server:** Ubuntu Server 22.04 running the Wazuh manager, indexer, and dashboard for centralized log collection and security monitoring.

• **Linux Endpoint:** Ubuntu Server 22.04 acting as a target server to simulate attacks such as SSH brute force, SQL injection, and port scanning.

• **Windows Endpoint:** Windows 10 machine used to simulate endpoint attacks such as process injection and to generate Sysmon telemetry.

• **Attacker Machine:** Kali Linux used to simulate real-world attack techniques against the target systems.

## Detection Scenarios

The following detection scenarios were executed within the lab architecture to simulate real-world attacks against both Windows and Linux systems. Each scenario demonstrates how Wazuh collects logs from different endpoints and generates alerts based on attack behavior.


### 1 Process Injection Detection

Process Injection is a defense evasion technique where malicious code is executed inside legitimate processes to avoid detection.

In this lab, a malicious executable injects a payload into a trusted Windows process (notepad.exe) using the CreateRemoteThread API. Sysmon captures the remote thread creation event (Event ID 8), and Wazuh custom detection rules identify the suspicious behavior and generate high-severity alerts.

Technique:

MITRE ATT&CK T1055.001 – Process Injection

Read the full lab:

➡️ [Process Injection Detection Lab](scenarios/process_injection_detection/README.md)

---

### 2 Port Scanning Detection and Threat Intelligence Enrichment

Port scanning is a reconnaissance technique used by attackers to identify open ports and discover running services before launching attacks.

In this scenario, an attacker performs a port scan against an Ubuntu server. UFW firewall logs blocked connection attempts which are collected by Wazuh. Custom correlation rules detect abnormal connection patterns and generate alerts.

To enhance detection context, a custom Wazuh integration automatically queries the VirusTotal API for threat intelligence data about the suspicious IP. The returned intelligence data is parsed and used to generate enriched alerts, demonstrating automated threat intelligence enrichment.

Technique:

MITRE ATT&CK T1046 – Network Service Discovery

Read the full lab:

➡️ [Port Scanning Detection Lab](scenarios/port_scanning/README.md)

---

### 3 SSH Brute Force Detection with Log Analysis and Active Response

SSH brute force attacks attempt to gain unauthorized access by repeatedly trying different password combinations. These attacks generate multiple authentication failures which can be detected through system logs.

In this scenario, Wazuh monitors SSH authentication logs from an Ubuntu server. When multiple failed login attempts are detected, Wazuh triggers an alert using default detection rules. Active Response is then used to automatically block the attacker IP address, demonstrating both detection and automated response capabilities.

Technique:

MITRE ATT&CK T1110 – Brute Force

Read the full lab:

➡️ [SSH Brute Force Detection Lab](scenarios/ssh_bruteforce/README.md)

---

### 4 SQL Injection Detection

SQL Injection is a common web attack where attackers attempt to manipulate backend database queries by injecting malicious SQL statements into HTTP requests.

In this lab, an attacker sends crafted SQL payloads to an Apache web server. The requests are recorded in Apache access logs and collected by the Wazuh agent. Wazuh built-in web attack rules detect SQL injection patterns and generate security alerts based on suspicious query strings.

Technique:

MITRE ATT&CK T1190 – Exploit Public Facing Application

Read the full lab:

➡️ [SQL Injection Detection Lab](scenarios/sql_injection/README.md)

---

## Future Improvements

This project can be further expanded to simulate more advanced SOC capabilities and improve detection coverage. Possible future enhancements include:

• **IDS Integration:** Integrate network-based IDS such as Suricata or Zeek to collect network traffic alerts and enhance network threat detection.

• **YARA Malware Detection:** Implement YARA rules to detect malicious files and improve host-based malware detection capabilities.

• **SOAR Automation:** Extend the lab with Security Orchestration, Automation, and Response (SOAR) concepts such as automated enrichment, alert triage, and response playbooks.

• **AI-assisted Log Analysis:** Explore the use of Large Language Models (LLMs) to automatically summarize alerts, explain attacker behavior, and assist SOC analysts in incident investigation.

