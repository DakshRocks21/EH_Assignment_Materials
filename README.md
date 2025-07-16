# Ethical Hacking Assignment

> NO Misconfigurations, NO METASPLOIT.
> Everything here has either happened before or is a POC of a real vulnerability.

## Storyline
[Company name] is a tech company specialising in software development. They recently hired an intern with the GitHub alias AvidTennisCoach, who is a Y3 IT intern from Ngee Ann Poly. He was part of a team who built applications for clients, including his first major project Tennis Booking Website.

Having recently had a pentest done by internal pentesters, many of the simple low hanging fruits and misconfigurations have been fixed by [Company name]'s sysadmin team, making the Active Directory network more secure and harder to hack (with the least secure configurations being the defaults).

With the recent cybersecurity developments around the world, [Company name] has invited us to conduct another round of pentests in an effort to secure their infrastructure from the evolving cybersecurity threat landscape.

## Pentest setup
> [!NOTE]
> All machines have been fuly patched as of May 2025.
### 1. EHLinuxServ
- Purpose: Linux Web Server hosting Tennis Booking Website
- OS: Ubuntu Server 25.04
- IP: NA
- Location: DMZ (emulated by hosting on Azure, NOT domain joined)

### 2. EH-DC01
- Purpose: Active Directory Domain Controller
- OS: Windows Server 2025
- IP: 10.10.1.2, Subnet: 10.10.1.0/24
- Location: Internal Network (domain joined)

### 3. EH-WinServ01
- Purpose: Windows Web Server hosting Internal Client Management Software
- OS: Windows Server 2025
- IP: 10.10.1.3, Subnet: 10.10.1.0/24
- Location: Internal Network (domain joined)

### 4. EH-SIEMServer
- Purpose: Linux master server hosting Wazuh SIEM
- OS: Ubuntu Server 25.04
- IP: 10.10.1.4, Subnet: 10.10.1.0/24
- Location: Internal Network (NOT domain joined)

### 5. EH-SIEMWorker
- Purpose: Linux worker server hosting Wazuh SIEM
- OS: Ubuntu Server 25.04
- IP: 10.10.1.5, Subnet: 10.10.1.0/24
- Location: Internal Network (NOT domain joined)

### 6. EH-LinuxServ01
- Purpose: Linux staging server to test internal software
- OS: Ubuntu Server 25.04
- IP: 10.10.1.6, Subnet: 10.10.1.0/24
- Location: Internal Network (NOT domain joined)

### 7. EH-AdminClient
- Purpose: Personal laptop used by the domain administrator
- OS: Windows 11 24H2
- IP: 10.10.1.128, Subnet: 10.10.1.0/24
- Location: Internal Network (domain joined)

### 8. EH-KaliAttacker
- Purpose: Attacker VM for pentesting
- OS: Kali Linux 2025.02
- IP: NA
- Location: Outside all networks

## Flow of events

### 1. Linux Server @ Azure

`Exploit`

1. SSTI through website
2. Write a wrapper to execute commands
3. (1) Make SSH connection to the server by exfiltrating the SSH private key

`Post Exploitation`

3. (2) Persistance on the Linux server
4. do recon and find exposed github credentials

### 2. Windows Server @ Active Directory (in the internal network)

`Exploit`

5. Use the GitHub credentials to access private repositories
6. Realise that it's a CI/CD pipeline
7. Use the pipeline to deploy a malicious code to the Windows Server
8. Get a reverse shell on the Windows Server

`Post exploitation`

8. Persistance on the Windows Server
9. Do recon and find the exposed SSH keys.
10. find the next target (Linux server)

### 3. Internal LinuxServer

`Exploit`

X. Find WAZUH API KEYS!

`Post exploitation`

11. Persistance on Internal Linux server

### Back to 2. Windows Server @ Active Directory

`Exploit`

12. Realise that its vulnerable to Local Privilege Escalation, `CVE-2025-33073`
13. Use the exploit to get administrative privileges on the Windows Server

`Post exploitation`

14. Do recon and analyse the network
15. Find the next target (Windows Client)

### 4. Windows Client

`Exploit`

(NO EXPLOIT)

16. Log in with domain credentials

`Post exploitation`

17. Mimikatz to dump Domain Admin credentials
18. Do recon and find the exposed credentials of the Wazuh server

### 5. Wazuh Server

19. Realise its vulnerable to Wazuh CVE - `CVE-2025-24016`
20. Use the exploit to get a reverse shell on the Wazuh server
21. Persistence on the Wazuh server

## Removed (time constraints)

Section 4, After 17: Password dump from browsers --> IP Camera, --> expose camera feed to the Internet