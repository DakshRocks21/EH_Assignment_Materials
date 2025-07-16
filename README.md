# Ethical Hacking Assignment

> NO Misconfigurations, NO METASPLLOIT.
> Everything here has either happened before or is a POC of a real vulnerability.

## Flow of events

#### 1. Linux Server @ Azure

`exploit`

1. SSTI through website
2. Write a wrapper to execute commands
3. (1) Make SSH connection to the server by exfilltrating the SSH private key

`post exploitation`

3. (2) Persistance on the Linux server
4. do recon and find exposed github credentials

#### 2. Windows Server @ Active Directory (in the internal network)

`exploit`

5. Use the github credentials to access private repositories
6. Realise that its a CI/CD pipeline
7. Use the pipeline to deploy a malicious code to the Windows server
8. Get a reverse shell on the Windows server

`post exploitation`

8. Persistance on the Windows server
9. Do recon and find the exposed SSH keys.
10. find the next target(linuxserver)

#### 3. Internal LinuxServer

`exploit`

X. Find WAZAH API KEYS!

`post exploitation`

11. Persistance on Internal Linux server

#### Back to 2. Windows Server @ Active Directory

`exploit`

12. realise that its vuln to Local Privilege Escalation, `CVE-2025-33073`
13. Use the exploit to get Administrative privileges on the Windows Server

`post exploitation`

14. Do recon and analyse the network
15. Find the next target (Windows Client)

#### 4. Windows Client

`exploit`

16. Log in with domain credentials
    NO EXPLOIT

`post exploitation`

17. Mimikatz to dump the credentials (DOMAIN ADMIN!!!!!)
18. Do recon and find the exposed credentials of the Wazah server

#### 5. Wazah Server

19. Realise its vulnerable to Wazah CVE - `CVE-2025-24016`
20. Use the exploit to get a reverse shell on the Wazah server
21. Persistence on the Wazah server

## Removed (time constraints)

Section 4, After 17, Password dump from browsers, -> IP Camera, -> expose camera feed to the internet

## Summary

1. 2 CVES
2. persistence THROUGH SSH KEYS ????
3.
