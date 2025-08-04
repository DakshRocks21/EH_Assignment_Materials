#!/bin/bash
###############################################################################
# Wazuh Enumeration Script
# Enumerates Wazuh Agent Information
# Checks Wazuh Agent Version, Status, Open Ports, Manager Info, Logs, and
# Authentication Key
###############################################################################

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}--- Wazuh Agent Enumeration ---${NC}"

echo -e "\n${GREEN}Checking Wazuh agent version...${NC}"
if [ -f /var/ossec/bin/wazuh-agentd ]; then
    /var/ossec/bin/wazuh-agentd -V
else
    echo -e "${RED}wazuh-agentd not found${NC}"
fi

echo -e "\n${GREEN}Checking agent service status...${NC}"
if systemctl is-active --quiet wazuh-agent; then
    echo "Wazuh agent is RUNNING."
else
    echo -e "${RED}Wazuh agent is NOT running.${NC}"
fi

echo -e "\n${GREEN}Checking Wazuh-related open ports...${NC}"
REMOTE_ADDR=$(ss | awk '$6 ~ /:1514$|:1515$/ {print $6}')

if [[ -n "$REMOTE_ADDR" ]]; then
    echo "Agent is connected to: $REMOTE_ADDR"
else
    echo -e "${RED}No Wazuh ports detected listening.${NC}"
fi

echo -e "\n${GREEN}Checking Wazuh manager IP/hostname...${NC}"
if [ -f /var/ossec/etc/ossec.conf ]; then
    MANAGER_ADDR=$(grep -A2 "<server>" /var/ossec/etc/ossec.conf | grep -E "<address>" | sed 's/<[^>]*>//g' | xargs)
    echo -e " Manager Address: ${MANAGER_ADDR}"
else
    echo -e "${RED}Cannot find ossec.conf!${NC}"
fi

echo -e "\n${GREEN}Showing last 10 agent logs...${NC}"
if [ -f /var/ossec/logs/ossec.log ]; then
    tail -n 10 /var/ossec/logs/ossec.log
else
    echo -e "${RED}Agent log file not found.${NC}"
fi

echo -e "\n${GREEN}Wazuh Agent Authentication Key${NC}"
if [[ -f /var/ossec/etc/client.keys ]]; then
    awk '{print $NF}' /var/ossec/etc/client.keys
else
    echo -e "${RED}Wazuh Agent Authentication Key not found. ${NC}"
fi

echo -e "\n${GREEN}--- Agent Enumeration Complete ---${NC}"
