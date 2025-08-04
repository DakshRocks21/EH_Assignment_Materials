#!/bin/bash
###############################################################################
# Wazuh API Enumeration Script
# Enumerates Wazuh API Information
# Fetches cluster nodes, agents, user privileges, and API users
###############################################################################

MANAGER_IP="10.10.1.4"
WAZUH_USER="wazuh-wui"
WAZUH_PASS="q6mMDCUKJ61jfmGzm.Axx.ogqNZhJb7s"
API_BASE="https://${MANAGER_IP}:55000"

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}--- Wazuh API Enumeration Script---${NC}"

# Authentication
echo "Authenticating to Wazuh API"
TOKEN_RES=$(curl -sk -u "${WAZUH_USER}:${WAZUH_PASS}" \
    -X GET "${API_BASE}/security/user/authenticate")
TOKEN=$(echo "${TOKEN_RES}" | jq -r '.data.token')

if [[ -z "$TOKEN" || "$TOKEN" == "null" ]]; then
    echo -e "${RED}Failed to retrieve token from Wazuh API${NC}"
    echo "Response: $TOKEN_RES"
    exit 1
else
    echo -e "${GREEN}Token acquired successfully.${NC}"
fi

# Cluster nodes enumeration
echo -e "\n${GREEN}Fetching cluster nodes...${NC}"
CLUSTER_JSON=$(curl -sk -H "Authorization: Bearer $TOKEN" \
    "${API_BASE}/cluster/nodes")

echo "$CLUSTER_JSON" | jq -r '
  if (.data.affected_items? | length // 0) == 0 then
    "No cluster nodes found."
  else
    .data.affected_items[]
    | "Node: " + .name
      + "\n  Role: " + .type
      + "\n  Version: " + .version
      + "\n  IP: " + .ip
      + "\n"
  end
'

# Agents enumeration
echo -e "\n${GREEN}Fetching agents list...${NC}"
AGENTS_JSON=$(curl -sk -H "Authorization: Bearer $TOKEN" \
    "${API_BASE}/agents?limit=500")

echo "$AGENTS_JSON" | jq -r '
  if (.data.affected_items? | length // 0) == 0 then
    "No agents found."
  else
    .data.affected_items[]
    | "Agent ID: " + .id
      + "\n  Name: " + .name
      + "\n  IP: " + (.ip // "N/A")
      + "\n  Status: " + .status
      + "\n  Manager: " + .manager
      + "\n  Version: " + .version
      + "\n"
  end
'

# Wazuh API privileges check
echo -e "\n${GREEN}Checking Current User info...${NC}"
USER_JSON=$(curl -sk -H "Authorization: Bearer $TOKEN" \
    "${API_BASE}/security/users/me")

echo "$USER_JSON" | jq -r '
  if (.data.affected_items? | length // 0) == 0 then
    "No user found."
  else
    .data.affected_items[] as $user |
    "Username: \($user.username)\nAllow Run As: \($user.allow_run_as)\n" +
    (
      $user.roles[] |
      "Role: \(.name)\n" +
      (
        .policies
        | group_by(.name)
        | .[]
        | {
            name: .[0].name,
            actions: (map(.policy.actions[]) | unique),
            resources: (map(.policy.resources[]) | unique)
          }
        | "  Policy: \(.name)\n" +
          "    Actions:\n" +
          ( .actions | sort | map("      - " + .) | join("\n") ) + "\n" +
          "    Resources:\n" +
          ( .resources | sort | map("      - " + .) | join("\n") ) + "\n"
      ) +
      (
        if (.rules? | length > 0) then
          "  Rules:\n" +
          (
            .rules[] |
            "    - \(.name): " +
            ( .rule.FIND | to_entries[] | "\(.key)=\(.value)" )
          )
        else
          ""
        end
      )
    )
  end
'

# Fetching all API users
echo -e "\n${GREEN}Fetching All API Users...${NC}"
USER_LIST_JSON=$(curl -sk -H "Authorization: Bearer $TOKEN" \
    "${API_BASE}/security/users/")

echo "$USER_LIST_JSON" | jq -r '
  if (.data.affected_items? | length == 0) then
    "No users found."
  else
    .data.affected_items[] |
    "Username: \(.username)\nAllow Run As: \(.allow_run_as)\nRoles: \(.roles | join(", "))\n"
  end
'

echo -e "${GREEN}--- Enumeration Complete ---${NC}"