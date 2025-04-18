# Eventia SSL Setup and Management

This document outlines the SSL certificate management setup for Eventia, covering the setup, maintenance, and troubleshooting procedures for both the frontend and backend applications.

## Architecture Overview

The Eventia platform uses a secure SSL/TLS setup with the following components:

- **Frontend**: Hosted on Firebase Hosting at `eventia.live`
- **Backend API**: Deployed on Google Cloud Run at `api.eventia.live`
- **Certificate Management**: Using acme.sh (a lightweight alternative to Certbot)
- **Automation**: GitHub Actions for certificate issuance and renewal
- **Monitoring**: SSL health checks and Slack notifications

## DNS Configuration

DNS is managed through Google Cloud DNS with DNSSEC enabled:

- A records for `eventia.live` and `api.eventia.live`
- CNAME for `www.eventia.live` redirecting to the root domain
- CAA records allowing certificates from Let's Encrypt
- TXT records for domain verification
- DMARC, SPF, and MX records for email security

## Certificate Management

### Initial Certificate Issuance

To issue SSL certificates for the first time:

1. Ensure DNS records are properly configured and propagated
2. Run the GitHub Actions workflow `ssl-issuance.yml` via the Actions tab
3. Select the environment (staging or production)
4. The workflow will:
   - Verify DNS configuration
   - Issue certificates via Let's Encrypt using DNS challenge
   - Store certificates in Google Cloud Secret Manager
   - Send a notification upon completion

### Automated Certificate Renewal

Certificates are automatically renewed through:

1. **Container-level renewal**: Each container runs a daily cron job to check and renew certificates
2. **System-level renewal**: A monthly GitHub Actions workflow (`ssl-renewal.yml`) runs to check all certificates and renew as needed

The renewal process includes:

- Certificate expiry checking
- Creating backups of existing certificates
- Issuing new certificates
- Updating deployment configurations
- Sending notifications

### Manual Certificate Renewal

To manually trigger certificate renewal:

1. Go to GitHub Actions
2. Select the `SSL Certificate Renewal` workflow
3. Click "Run workflow"
4. Select "Force renewal" if needed
5. Monitor the workflow output

## Security Configuration

### Security Headers

All applications use the following security headers:

- `Strict-Transport-Security`: HSTS with preloading
- `Content-Security-Policy`: Restrictive CSP to prevent XSS
- `X-Content-Type-Options`: Prevent MIME-type sniffing
- `X-Frame-Options`: Prevent clickjacking
- `Referrer-Policy`: Control referrer information
- `Feature-Policy/Permissions-Policy`: Restrict browser features

### SSL Configuration

Nginx is configured with:

- TLS 1.2 and 1.3 only (older protocols disabled)
- Strong cipher suite configuration
- OCSP stapling enabled
- HTTP/2 support
- Automatic HTTP to HTTPS redirection
- Perfect Forward Secrecy with strong DH parameters

## Deployment

### Backend Deployment

The backend uses a custom Dockerfile with Nginx and acme.sh:

1. Build the Docker image:
   ```bash
   docker build -f Dockerfile.ssl -t eventia-backend:ssl .
   ```

2. Deploy to Cloud Run:
   ```bash
   gcloud run deploy eventia-backend \
     --image eventia-backend:ssl \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars="DOMAIN=api.eventia.live" \
     --set-secrets="SSL_CERT=api-eventia-live-fullchain:latest,SSL_KEY=api-eventia-live-privkey:latest"
   ```

### Frontend Deployment

For the frontend:

1. Build the application:
   ```bash
   yarn build
   ```

2. Deploy to Firebase Hosting:
   ```bash
   firebase deploy --only hosting
   ```

Firebase hosting automatically manages SSL certificates once domain verification is complete.

## Monitoring and Testing

### SSL Health Checks

SSL health is monitored through:

1. Periodic checks in the containers
2. The `monitor-ssl-health` job in the `ssl-renewal.yml` workflow
3. Running the `ssl-test.sh` script manually

### Alerts

SSL-related alerts are sent to Slack when:

- Certificates are issued or renewed
- Certificates are approaching expiration
- SSL configuration scores below A rating
- Security vulnerabilities are detected

## Troubleshooting

### Common Issues

#### DNS Propagation

If domain validation fails:

1. Verify DNS records using:
   ```bash
   dig +short eventia.live
   dig +short api.eventia.live
   dig +short CAA eventia.live
   ```

2. Check propagation status with:
   ```bash
   https://dnschecker.org/#A/eventia.live
   ```

#### Certificate Issuance Failures

If certificate issuance fails:

1. Check the acme.sh logs:
   ```bash
   docker exec <container_id> cat /root/.acme.sh/acme.sh.log
   ```

2. Verify Let's Encrypt status:
   ```bash
   https://letsencrypt.status.io/
   ```

#### Security Testing

To manually test the SSL configuration:

1. Use SSL Labs:
   ```
   https://www.ssllabs.com/ssltest/analyze.html?d=eventia.live
   https://www.ssllabs.com/ssltest/analyze.html?d=api.eventia.live
   ```

2. Check security headers:
   ```
   https://securityheaders.com/?q=eventia.live
   https://securityheaders.com/?q=api.eventia.live
   ```

## Required GitHub Secrets

- `ACME_ACCOUNT_EMAIL`: Email address for Let's Encrypt account
- `DNS_PROVIDER_TOKEN`: Token for DNS provider API access
- `GCP_SSL_SA`: Google Cloud service account key with Secret Manager access
- `GCP_PROJECT_ID`: Google Cloud project ID
- `GCP_REGION`: Google Cloud region
- `SLACK_WEBHOOK_SSL`: Slack webhook URL for notifications
- `FIREBASE_DEPLOY_KEY`: Firebase deployment token
- `SSLLABS_API_KEY`: (Optional) SSL Labs API key

## HSTS Preloading

To configure HSTS preloading:

1. Ensure your site meets all requirements:
   - Serves valid certificates
   - Redirects from HTTP to HTTPS
   - Has proper HSTS headers with `includeSubDomains` and `preload`

2. Submit the domain at:
   ```
   https://hstspreload.org/
   ```

## Additional Resources

- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [acme.sh GitHub Repository](https://github.com/acmesh-official/acme.sh)
- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)
- [SSL Labs Grading Criteria](https://github.com/ssllabs/research/wiki/SSL-Server-Rating-Guide) 