#!/bin/bash
# SSL Certificate Health Check Script for Eventia Backend

set -e

# Log function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a /var/log/cert-health.log
}

# Variables
DOMAIN="api.eventia.live"
CERT_DIR="/etc/letsencrypt/live/$DOMAIN"
WEBHOOK_URL="${SLACK_WEBHOOK_SSL}"
SSL_TEST_API="https://api.ssllabs.com/api/v3/analyze"

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
            --data "{\"attachments\":[{\"color\":\"$color\",\"title\":\"SSL Certificate Health - $DOMAIN\",\"text\":\"$message\"}]}" \
            "$WEBHOOK_URL"
    else
        log "Slack webhook URL not defined, skipping notification"
    fi
}

# Check if certificate exists
if [ ! -f "$CERT_DIR/fullchain.pem" ]; then
    log "ERROR: Certificate does not exist for $DOMAIN"
    notify_slack "❌ Certificate does not exist for $DOMAIN" "error"
    exit 1
fi

# Check certificate expiry
expiry=$(openssl x509 -enddate -noout -in "$CERT_DIR/fullchain.pem" | cut -d= -f2)
expiry_date=$(date -d "$expiry" +%s)
current_date=$(date +%s)
days_left=$(( (expiry_date - current_date) / 86400 ))

log "Certificate for $DOMAIN expires in $days_left days"

# Alert if certificate is expiring soon
if [ $days_left -lt 14 ]; then
    log "WARNING: Certificate for $DOMAIN is expiring in $days_left days"
    notify_slack "⚠️ SSL certificate for $DOMAIN is expiring in $days_left days" "warning"
elif [ $days_left -lt 7 ]; then
    log "CRITICAL: Certificate for $DOMAIN is expiring in $days_left days"
    notify_slack "🚨 SSL certificate for $DOMAIN is expiring in $days_left days" "error"
    # Force renewal if less than 7 days left
    /etc/periodic/daily/renew-cert.sh
fi

# Check certificate validity
openssl x509 -in "$CERT_DIR/fullchain.pem" -noout -checkend 0
if [ $? -ne 0 ]; then
    log "ERROR: Certificate for $DOMAIN is not valid"
    notify_slack "❌ SSL certificate for $DOMAIN is not valid" "error"
    exit 1
fi

# Check OCSP stapling
ocsp_status=$(echo QUIT | openssl s_client -connect "$DOMAIN:443" -servername "$DOMAIN" -status 2>/dev/null | grep -A 17 'OCSP response:' | grep -i 'OCSP Response Status' | awk '{print $4}')
if [ "$ocsp_status" != "successful" ]; then
    log "WARNING: OCSP stapling is not working properly for $DOMAIN"
    notify_slack "⚠️ OCSP stapling is not working properly for $DOMAIN" "warning"
fi

# Check security headers
headers=$(curl -s -I "https://$DOMAIN/ssl-health" | grep -i 'strict-transport-security\|content-security-policy\|x-content-type-options\|x-frame-options\|x-xss-protection' | wc -l)
if [ $headers -lt 5 ]; then
    log "WARNING: Some security headers are missing for $DOMAIN"
    notify_slack "⚠️ Some security headers are missing for $DOMAIN" "warning"
fi

# Run SSL Labs test if API key is available
if [ -n "$SSLLABS_API_KEY" ]; then
    log "Running SSL Labs test for $DOMAIN..."
    
    # Start the assessment
    start_response=$(curl -s "$SSL_TEST_API?host=$DOMAIN&startNew=on")
    sleep 60  # Wait for assessment to complete
    
    # Get the results
    result=$(curl -s "$SSL_TEST_API?host=$DOMAIN")
    grade=$(echo "$result" | grep -o '"grade":"[^"]*"' | cut -d'"' -f4)
    
    if [ "$grade" = "A+" ]; then
        log "SSL Labs test passed with A+ grade for $DOMAIN"
    elif [ "$grade" = "A" ]; then
        log "SSL Labs test passed with A grade for $DOMAIN"
    else
        log "WARNING: SSL Labs test resulted in grade $grade for $DOMAIN"
        notify_slack "⚠️ SSL Labs grade for $DOMAIN is $grade, expected A or A+" "warning"
    fi
fi

log "Certificate health check completed"
exit 0 