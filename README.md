# Ethical Hacking Assignment

> [!WARNING]
> NO Misconfigurations, NO METASPLOIT.
> Everything here has either happened before or is a POC of a real vulnerability.

## Storyline
DAR Solutions is a tech company specialising in software development. They recently hired an intern with the GitHub alias AvidTennisCoach, who is a Y3 IT intern from Ngee Ann Poly. He was part of a team who built applications for clients, including his first major project Tennis Booking Website.

Having recently had a pentest done by internal pentesters, many of the simple low hanging fruits and misconfigurations have been fixed by DAR Solutions' sysadmin team, making the Active Directory network more secure and harder to hack (with the least secure configurations being the defaults).

With the recent cybersecurity developments around the world, DAR Solutions has invited us to conduct another round of pentests in an effort to secure their infrastructure from the evolving cybersecurity threat landscape.

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
#### Exploit
1.1. Server-Side Template Injection through website

1.2.	Write a wrapper to execute commands

1.3.1.	Make SSH connection to the server by exfiltrating the SSH private key

#### Post Exploitation
1.3.2.	Persistence on the Linux server

1.4.	Do recon and find exposed GitHub credentials

### 2. Windows Server @ Active Directory (in the internal network)
#### Exploit
2.1.	Use the GitHub credentials to access private repositories

2.2.	Realise that it's a CI/CD pipeline

2.3.	Use the pipeline to deploy a malicious code to the Windows Server

2.4.	Get a reverse shell on the Windows Server

#### Post Exploitation
2.5.	Persistence on the Windows Server

2.6.	Do recon and find the exposed SSH keys.

2.7.	Find the next target (Linux server)

### 3. Internal Linux Server
#### Exploit
3.1.	Find Wazuh API Keys

#### Post Exploitation
3.2.	Persistence on Internal Linux server through SSH reverse tunnelling

3.3.	Attacker able to bring in own attacker environment to network (needed for RDP since only machine with X11/GUI access)

### 4.	Back to Windows Server @ Active Directory
#### Exploit
4.1.	Get Domain User privileges via compromised CI/CD pipeline

4.2.	 Discover SSH keys to another Linux server on network

#### Post Exploitation
4.3.	Start reverse shell on Windows Server and Linux Server

4.4.	Do recon and analyse the network

4.5.	Find the next target (Windows Client)

### 5. Windows Client (Domain Admin’s personal laptop)
#### Exploit
5.1.	Discover that Windows Client is vulnerable to CVE-2025-33073

5.2.	Make use of SSPI/GSSAPI on Windows Server to authenticate as Domain User (prerequisite for CVE-2025-33073)

5.3.	Gain SYSTEM privileges on Windows Client

#### Post Exploitation
5.4.	Disable remote UAC to allow local administrators to execute commands remotely via NetExec

5.5.	Enable Restricted Admin to allow RDP via Pass-the-Hash

5.6.	RDP into client

5.7.	Mimikatz to dump Domain Admin credentials

5.8.	Do recon and find the exposed credentials of the Wazuh server

### 6.	Wazuh Server
#### Exploit
6.1.	Enumerate Information via API key

6.2.	Reverse Shell into the Wazuh Master Node via CVE-2025-24016

6.3.	Privilege escalation via Wazuh default active response script using Wazuh API Key

#### Post Exploitation
6.4.	Compromising admin account

6.5.	Creating new indexer user & server user

6.6.	Clearing tracks

### 7. Domain Controller
#### Exploit
7.1.	Enable Restricted Admin to allow RDP via Pass-the-Hash

7.2.	RDP into Domain Controller using stolen Domain Admin hash

#### Post Exploitation
7.3.	Dump NTDS.dit

7.4.	Create new Domain Admin user with known password for persistence without relying on password hashes

7.5.	Gold/Sapphire/Diamond ticket attack?

7.6.	Exfiltrating browser data

#### Exploit
7.1.	Enable Restricted Admin to allow RDP via Pass-the-Hash

7.2.	RDP into Domain Controller using stolen Domain Admin hash

#### Post Exploitation
7.3.	Dump NTDS.dit

7.4.	Create new Domain Admin user with known password for persistence without relying on password hashes

7.5.	Gold/Sapphire/Diamond ticket attack?

7.6.	Exfiltrating browser data

## Removed (time constraints)

Section 4, After 17: Password dump from browsers --> IP Camera, --> expose camera feed to the Internet
