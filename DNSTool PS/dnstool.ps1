param([Parameter(Mandatory = $true)]$ServerIp, [Parameter(Mandatory = $true)]$DomainName, [Parameter(Mandatory = $true)]$SrcIp, [Parameter(Mandatory = $true)]$DstRecord)

Get-LdapConnection -LdapServer $ServerIp -EncryptionType Kerberos

$DnsResult = Resolve-DnsName $DomainName -Type SOA

$dnsRecord = New-Object System.Collections.Generic.List[byte]

# DataLength
$dnsRecord.AddRange([BitConverter]::GetBytes([UInt16]4))
# Type (A record)
$dnsRecord.AddRange([BitConverter]::GetBytes([UInt16]1))
# Version
$dnsRecord.Add(5)
# Rank
$dnsRecord.Add(240)
# Flags
$dnsRecord.AddRange([BitConverter]::GetBytes([UInt16]0))
# Serial
$dnsRecord.AddRange([BitConverter]::GetBytes($DnsResult.SerialNumber))
# TTL
$dnsRecord.AddRange([BitConverter]::GetBytes([UInt32]([System.Net.IPAddress]::HostToNetworkOrder([int]$ttl))))
# Reserved
$dnsRecord.AddRange([byte[]](0, 0, 0, 0))
# Timestamp
$dnsRecord.AddRange([byte[]](0, 0, 0, 0))
# IP address (4 bytes)
$dnsRecord.AddRange([System.Net.IPAddress]::Parse($SrcIp).GetAddressBytes())

# Convert to byte array
$dnsRecordBytes = $dnsRecord.ToArray()

#Design the object
$Props = @{
    objectClass       = @("top", "dnsNode")
    distinguishedName = "DC={0},DC={1},CN=MicrosoftDNS,DC=DomainDnsZones,DC={2},DC={3}" -f $DstRecord, $DomainName, $DomainName.Split(".")[0], $DomainName.Split(".")[1]
    dnsRecord         = $dnsRecordBytes
}

#Create the object according to design
$obj = new-object PSObject -Property $Props

#When dealing with password, LDAP server is likely
#to require encrypted connection
$Ldap = Get-LdapConnection -EncryptionType Kerberos
#Create the object in directory
$obj | Add-LdapObject -LdapConnection $Ldap