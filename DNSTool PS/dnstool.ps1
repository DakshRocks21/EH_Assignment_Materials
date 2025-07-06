param($ServerIp, $DomainName, $SrcIp, $DstRecord)

Get-LdapConnection -LdapServer $ServerIp -EncryptionType Kerberos
#We use transforms to convert values to LDAP native format when saving object to LDAP store
Register-LdapAttributeTransform -Name UnicodePwd
Register-LdapAttributeTransform -Name UserAccountControl

#Design the object
$Props = @{
  distinguishedName="DC=,{0},DC={1},CN=MicrosoftDNS,DC=DomainDnsZones,DC={2},DC=local" -f $DstRecord, $DomainName, $DomainName.Split(".")[0]
  dnsRecord=""
}

#Create the object according to design
$obj = new-object PSObject -Property $Props

#When dealing with password, LDAP server is likely
#to require encrypted connection
$Ldap = Get-LdapConnection -EncryptionType Kerberos
#Create the object in directory
$obj | Add-LdapObject -LdapConnection $Ldap