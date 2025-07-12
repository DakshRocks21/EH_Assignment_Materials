param([Parameter(Mandatory = $true)]$ServerIp, [Parameter(Mandatory = $true)]$DomainName, [Parameter(Mandatory = $true)]$SrcRecord, [Parameter(Mandatory = $true)]$DstIp)

Add-Type -AssemblyName System.DirectoryServices.Protocols

$ldapIdentifier = New-Object System.DirectoryServices.Protocols.LdapDirectoryIdentifier($ServerIp, $null, $false, $false)
$ldapConnection = New-Object System.DirectoryServices.Protocols.LdapConnection($ldapIdentifier)
$ldapConnection.AuthType = [System.DirectoryServices.Protocols.AuthType]::Negotiate
$ldapConnection.Bind()

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
$dnsRecord.AddRange([byte[]](0x00, 0x00))
# Serial
$dnsRecord.AddRange([BitConverter]::GetBytes([UInt32]$DnsResult.SerialNumber))
# TTL
$ttl = [BitConverter]::GetBytes([UInt32]180)
[void][array]::Reverse($ttl)
$dnsRecord.AddRange($ttl)
# Reserved
$dnsRecord.AddRange([byte[]](0x00, 0x00, 0x00, 0x00))
# Timestamp
$dnsRecord.AddRange([byte[]](0x00, 0x00, 0x00, 0x00))
# IP address (4 bytes)
$dnsRecord.AddRange([System.Net.IPAddress]::Parse($DstIp).GetAddressBytes())

$dnsRecord | ForEach-Object { "{0:X2}" -f $_ }

# Convert to byte array
#$dnsRecordBytes = $dnsRecord.ToArray()

$distinguishedName = "DC={0},DC={1},CN=MicrosoftDNS,DC=DomainDnsZones,DC={2},DC={3}" -f $SrcRecord, $DomainName, $DomainName.Split(".")[0], $DomainName.Split(".")[1]

#Design the object
$Props = @{
    objectClass = @("top", "dnsNode")
    dnsRecord   = $dnsRecord.ToArray()
}

#Create the object in directory
$addRequest = New-Object System.DirectoryServices.Protocols.AddRequest($distinguishedName, $null)
foreach ($key in $Props.Keys) {
    $attribute = New-Object System.DirectoryServices.Protocols.DirectoryAttribute($key, $Props[$key])
    $addRequest.Attributes.Add($attribute)
}

try {
    $ldapConnection.SendRequest($addRequest)
    Write-Host "DNS record added successfully."
} catch {
    Write-Error "Failed to add DNS record: $_"
}