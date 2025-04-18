#!/bin/bash
# SSL Testing Script for Eventia
# Uses SSL Labs API to test SSL configuration

set -e

# Log function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Variables
SSL_TEST_API="https://api.ssllabs.com/api/v3/analyze"
DOMAINS=("api.eventia.live" "eventia.live")
WEBHOOK_URL="${SLACK_WEBHOOK_SSL}"

# Function to send notification to Slack
notify_slack() {
    local message="$1"
    local status="$2"  # success, warning, error
    local color="good"
    
    if [ "$status" = "warning" ]; then
        color="warning"
    elif [ "$status" = "error" ]; then
        color="danger"
    fi
    
    if [ -n "$WEBHOOK_URL" ]; then
        curl -s -X POST -H 'Content-type: application/json' \
            --data "{\"attachments\":[{\"color\":\"${color}\",\"title\":\"SSL Test Results\",\"text\":\"${message}\"}]}" \
            "$WEBHOOK_URL"
    else
        log "Slack webhook URL not defined, skipping notification"
    fi
}

# Install required tools
if ! which jq >/dev/null 2>&1; then
    log "Installing jq..."
    apt-get update && apt-get install -y jq curl
fi

# Process each domain
for DOMAIN in "${DOMAINS[@]}"; do
    log "Testing SSL configuration for ${DOMAIN}..."
    
    # Start new assessment
    START_RESPONSE=$(curl -s "${SSL_TEST_API}?host=${DOMAIN}&startNew=on")
    
    if echo "$START_RESPONSE" | grep -q "error"; then
        ERROR_MSG=$(echo "$START_RESPONSE" | jq -r '.errors[0].message')
        log "Error starting test for ${DOMAIN}: ${ERROR_MSG}"
        notify_slack "❌ Error testing SSL for ${DOMAIN}: ${ERROR_MSG}" "error"
        continue
    fi
    
    log "SSL test started for ${DOMAIN}, waiting for results..."
    
    # Wait for assessment to complete
    ASSESSMENT_DONE=false
    MAX_ATTEMPTS=30
    ATTEMPT=0
    
    while [ "$ASSESSMENT_DONE" != "true" ] && [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
        RESULT=$(curl -s "${SSL_TEST_API}?host=${DOMAIN}")
        STATUS=$(echo "$RESULT" | jq -r '.status')
        
        if [ "$STATUS" = "READY" ] || [ "$STATUS" = "ERROR" ]; then
            ASSESSMENT_DONE=true
        else
            ATTEMPT=$((ATTEMPT+1))
            PROGRESS=$(echo "$RESULT" | jq -r '.progress')
            log "Assessment in progress for ${DOMAIN} (${PROGRESS}%)... attempt ${ATTEMPT}/${MAX_ATTEMPTS}"
            sleep 10
        fi
    done
    
    if [ "$ASSESSMENT_DONE" != "true" ]; then
        log "Assessment timed out for ${DOMAIN} after ${MAX_ATTEMPTS} attempts"
        notify_slack "⚠️ SSL test for ${DOMAIN} timed out" "warning"
        continue
    fi
    
    # Get the results
    FINAL_RESULT=$(curl -s "${SSL_TEST_API}?host=${DOMAIN}")
    
    if [ "$(echo "$FINAL_RESULT" | jq -r '.status')" = "ERROR" ]; then
        ERROR_MSG=$(echo "$FINAL_RESULT" | jq -r '.errors[0].message')
        log "Error testing SSL for ${DOMAIN}: ${ERROR_MSG}"
        notify_slack "❌ Error testing SSL for ${DOMAIN}: ${ERROR_MSG}" "error"
        continue
    fi
    
    # Extract grades and scores
    GRADE=$(echo "$FINAL_RESULT" | jq -r '.endpoints[0].grade')
    PROTOCOL_SUPPORT=$(echo "$FINAL_RESULT" | jq -r '.endpoints[0].details.protocols | length')
    CIPHER_STRENGTH=$(echo "$FINAL_RESULT" | jq -r '.endpoints[0].details.bestCipherStrength')
    KEY_EXCHANGE=$(echo "$FINAL_RESULT" | jq -r '.endpoints[0].details.keyExchange.strength')
    FORWARD_SECRECY=$(echo "$FINAL_RESULT" | jq -r '.endpoints[0].details.forwardSecrecy')
    OCSP_STAPLING=$(echo "$FINAL_RESULT" | jq -r '.endpoints[0].details.ocspStapling')
    
    # Log results
    log "SSL Test Results for ${DOMAIN}:"
    log "  Grade: ${GRADE}"
    log "  Protocol Support: ${PROTOCOL_SUPPORT} protocols"
    log "  Cipher Strength: ${CIPHER_STRENGTH} bits"
    log "  Key Exchange: ${KEY_EXCHANGE} bits"
    log "  Forward Secrecy: ${FORWARD_SECRECY}"
    log "  OCSP Stapling: ${OCSP_STAPLING}"
    
    # Determine status
    if [ "$GRADE" = "A+" ]; then
        STATUS="success"
        MESSAGE="✅ SSL configuration for ${DOMAIN} received an A+ grade!"
    elif [ "$GRADE" = "A" ]; then
        STATUS="success"
        MESSAGE="✅ SSL configuration for ${DOMAIN} received an A grade"
    elif [ "$GRADE" = "B" ]; then
        STATUS="warning"
        MESSAGE="⚠️ SSL configuration for ${DOMAIN} received a B grade - review recommended"
    else
        STATUS="error"
        MESSAGE="❌ SSL configuration for ${DOMAIN} received a ${GRADE} grade - immediate action required"
    fi
    
    # Send notification
    DETAILS="Grade: ${GRADE}\nProtocol Support: ${PROTOCOL_SUPPORT} protocols\nCipher Strength: ${CIPHER_STRENGTH} bits\nKey Exchange: ${KEY_EXCHANGE} bits\nForward Secrecy: ${FORWARD_SECRECY}\nOCSP Stapling: ${OCSP_STAPLING}"
    notify_slack "${MESSAGE}\n${DETAILS}" "${STATUS}"
    
    # If not A+, check detailed issues
    if [ "$GRADE" != "A+" ]; then
        # Check common issues
        if [ "$(echo "$FINAL_RESULT" | jq -r '.endpoints[0].details.heartbleed')" = "true" ]; then
            log "CRITICAL: ${DOMAIN} is vulnerable to Heartbleed!"
            notify_slack "🚨 CRITICAL: ${DOMAIN} is vulnerable to Heartbleed!" "error"
        fi
        
        if [ "$(echo "$FINAL_RESULT" | jq -r '.endpoints[0].details.poodle')" = "true" ]; then
            log "CRITICAL: ${DOMAIN} is vulnerable to POODLE!"
            notify_slack "🚨 CRITICAL: ${DOMAIN} is vulnerable to POODLE!" "error"
        fi
        
        if [ "$(echo "$FINAL_RESULT" | jq -r '.endpoints[0].details.freak')" = "true" ]; then
            log "CRITICAL: ${DOMAIN} is vulnerable to FREAK!"
            notify_slack "🚨 CRITICAL: ${DOMAIN} is vulnerable to FREAK!" "error"
        fi
        
        if [ "$(echo "$FINAL_RESULT" | jq -r '.endpoints[0].details.logjam')" = "true" ]; then
            log "CRITICAL: ${DOMAIN} is vulnerable to Logjam!"
            notify_slack "🚨 CRITICAL: ${DOMAIN} is vulnerable to Logjam!" "error"
        fi
        
        if [ "$(echo "$FINAL_RESULT" | jq -r '.endpoints[0].details.drownVulnerable')" = "true" ]; then
            log "CRITICAL: ${DOMAIN} is vulnerable to DROWN!"
            notify_slack "🚨 CRITICAL: ${DOMAIN} is vulnerable to DROWN!" "error"
        fi
    fi
    
    # Save detailed report
    mkdir -p /var/log/ssl-tests
    echo "$FINAL_RESULT" > "/var/log/ssl-tests/${DOMAIN}-$(date +%Y%m%d).json"
    log "Saved detailed report to /var/log/ssl-tests/${DOMAIN}-$(date +%Y%m%d).json"
done

log "SSL testing completed"
exit 0 