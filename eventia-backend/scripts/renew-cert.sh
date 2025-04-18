#!/bin/bash
# SSL Certificate Renewal Script for Eventia Backend (api.eventia.live)

set -e

# Log function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a /var/log/cert-renewal.log
}

# Variables
DOMAIN="api.eventia.live"
CERT_DIR="/etc/letsencrypt/live/$DOMAIN"
ACME_EMAIL="ssl@eventia.live"
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
            --data "{\"attachments\":[{\"color\":\"$color\",\"title\":\"SSL Certificate Event - $DOMAIN\",\"text\":\"$message\"}]}" \
            "$WEBHOOK_URL"
    else
        log "Slack webhook URL not defined, skipping notification"
    fi
}

# Check if certificate exists and create if not
if [ ! -f "$CERT_DIR/fullchain.pem" ]; then
    log "Certificate does not exist. Issuing new certificate for $DOMAIN..."
    
    # Issue new certificate
    acme.sh --issue --webroot /var/www/certbot -d "$DOMAIN" --keylength 2048 --accountemail "$ACME_EMAIL" \
        --cert-file "$CERT_DIR/cert.pem" \
        --key-file "$CERT_DIR/privkey.pem" \
        --fullchain-file "$CERT_DIR/fullchain.pem" \
        --chain-file "$CERT_DIR/chain.pem" \
        --reloadcmd "nginx -s reload"
    
    if [ $? -eq 0 ]; then
        log "Certificate issued successfully for $DOMAIN"
        notify_slack "✅ New SSL certificate issued for $DOMAIN" "success"
    else
        log "Failed to issue certificate for $DOMAIN"
        notify_slack "❌ Failed to issue new SSL certificate for $DOMAIN" "error"
        exit 1
    fi
else
    # Check certificate expiry
    expiry=$(openssl x509 -enddate -noout -in "$CERT_DIR/fullchain.pem" | cut -d= -f2)
    expiry_date=$(date -d "$expiry" +%s)
    current_date=$(date +%s)
    days_left=$(( (expiry_date - current_date) / 86400 ))
    
    log "Certificate for $DOMAIN expires in $days_left days"
    
    # Renew if less than 30 days left
    if [ $days_left -lt 30 ]; then
        log "Renewing certificate for $DOMAIN..."
        
        # Create backup of existing certificate
        backup_dir="/etc/letsencrypt/backup/$(date +%Y%m%d)"
        mkdir -p "$backup_dir"
        cp -r "$CERT_DIR" "$backup_dir"
        
        # Attempt to renew
        acme.sh --renew -d "$DOMAIN" --force --ecc
        
        if [ $? -eq 0 ]; then
            log "Certificate renewed successfully for $DOMAIN"
            notify_slack "🔄 SSL certificate renewed for $DOMAIN" "success"
            nginx -s reload
        else
            log "Certificate renewal failed, restoring backup..."
            cp -r "$backup_dir/$DOMAIN" "/etc/letsencrypt/live/"
            notify_slack "⚠️ SSL certificate renewal failed for $DOMAIN. Backup restored." "warning"
        fi
    else
        log "Certificate still valid, no renewal needed"
    fi
fi

# Update CAA record if DNS provider is set
if [ -n "$DNS_PROVIDER_TOKEN" ]; then
    log "Updating CAA records..."
    # Call external script to update CAA records
    /app/scripts/update-caa-records.sh "$DOMAIN" "letsencrypt.org"
fi

# Verify SSL configuration
log "Verifying SSL configuration..."
nginx -t

if [ $? -eq 0 ]; then
    log "SSL configuration verified successfully"
else
    log "SSL configuration verification failed"
    notify_slack "⚠️ SSL configuration verification failed for $DOMAIN" "error"
fi

log "Certificate renewal check completed"
exit 0 