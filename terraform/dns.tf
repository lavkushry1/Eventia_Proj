/**
 * Eventia DNS Configuration
 * This Terraform configuration sets up DNS records for the Eventia platform
 * with a focus on SSL/TLS security.
 */

// Google Cloud provider configuration
provider "google" {
  project     = var.project_id
  region      = var.region
  credentials = file(var.credentials_file)
}

// DNS Zone for eventia.live
resource "google_dns_managed_zone" "eventia_zone" {
  name        = "eventia-live-zone"
  dns_name    = "eventia.live."
  description = "DNS zone for Eventia platform"
  
  dnssec_config {
    state = "on"
    default_key_specs {
      algorithm  = "rsasha256"
      key_length = 2048
      key_type   = "keySigning"
    }
    default_key_specs {
      algorithm  = "rsasha256"
      key_length = 1024
      key_type   = "zoneSigning"
    }
  }
  
  labels = {
    environment = var.environment
    service     = "eventia"
  }
}

// A record for the root domain (eventia.live)
resource "google_dns_record_set" "root_domain" {
  name         = "eventia.live."
  type         = "A"
  ttl          = 300
  managed_zone = google_dns_managed_zone.eventia_zone.name
  
  rrdatas = [var.frontend_ip_address]
}

// A record for the API subdomain (api.eventia.live)
resource "google_dns_record_set" "api_subdomain" {
  name         = "api.eventia.live."
  type         = "A"
  ttl          = 300
  managed_zone = google_dns_managed_zone.eventia_zone.name
  
  rrdatas = [var.backend_ip_address]
}

// CNAME record for www subdomain
resource "google_dns_record_set" "www_subdomain" {
  name         = "www.eventia.live."
  type         = "CNAME"
  ttl          = 300
  managed_zone = google_dns_managed_zone.eventia_zone.name
  
  rrdatas = ["eventia.live."]
}

// CAA records for Let's Encrypt
resource "google_dns_record_set" "caa_records" {
  name         = "eventia.live."
  type         = "CAA"
  ttl          = 300
  managed_zone = google_dns_managed_zone.eventia_zone.name
  
  rrdatas = [
    "0 issue \"letsencrypt.org\"",
    "0 issuewild \"letsencrypt.org\"",
    "0 iodef \"mailto:security@eventia.live\""
  ]
}

// TXT record for domain verification (Firebase Hosting)
resource "google_dns_record_set" "firebase_verification" {
  name         = "eventia.live."
  type         = "TXT"
  ttl          = 300
  managed_zone = google_dns_managed_zone.eventia_zone.name
  
  rrdatas = ["\"google-site-verification=${var.firebase_verification_token}\""]
}

// TXT record for domain verification (Google Cloud)
resource "google_dns_record_set" "gcp_verification" {
  name         = "_cloud-site-verification.eventia.live."
  type         = "TXT"
  ttl          = 300
  managed_zone = google_dns_managed_zone.eventia_zone.name
  
  rrdatas = ["\"google-site-verification=${var.gcp_verification_token}\""]
}

// MX records for email security
resource "google_dns_record_set" "mx_records" {
  name         = "eventia.live."
  type         = "MX"
  ttl          = 3600
  managed_zone = google_dns_managed_zone.eventia_zone.name
  
  rrdatas = [
    "10 mail.eventia.live.",
    "20 alt.mail.eventia.live."
  ]
}

// SPF record for email validation
resource "google_dns_record_set" "spf_record" {
  name         = "eventia.live."
  type         = "TXT"
  ttl          = 3600
  managed_zone = google_dns_managed_zone.eventia_zone.name
  
  rrdatas = ["\"v=spf1 include:_spf.google.com ~all\""]
}

// DMARC record for email security
resource "google_dns_record_set" "dmarc_record" {
  name         = "_dmarc.eventia.live."
  type         = "TXT"
  ttl          = 3600
  managed_zone = google_dns_managed_zone.eventia_zone.name
  
  rrdatas = ["\"v=DMARC1; p=quarantine; rua=mailto:security@eventia.live; ruf=mailto:security@eventia.live; pct=100; adkim=s; aspf=s\""]
}

// Security TXT record location
resource "google_dns_record_set" "security_txt" {
  name         = "_security.eventia.live."
  type         = "TXT"
  ttl          = 3600
  managed_zone = google_dns_managed_zone.eventia_zone.name
  
  rrdatas = ["\"security-txt-location=/.well-known/security.txt\""]
}

// Variables
variable "project_id" {
  description = "Google Cloud Project ID"
  type        = string
}

variable "region" {
  description = "Google Cloud Region"
  type        = string
  default     = "us-central1"
}

variable "credentials_file" {
  description = "Path to the Google Cloud credentials file"
  type        = string
}

variable "environment" {
  description = "Deployment environment (production, staging)"
  type        = string
  default     = "production"
}

variable "frontend_ip_address" {
  description = "IP address for the frontend application"
  type        = string
}

variable "backend_ip_address" {
  description = "IP address for the backend API"
  type        = string
}

variable "firebase_verification_token" {
  description = "Firebase verification token for domain ownership"
  type        = string
}

variable "gcp_verification_token" {
  description = "Google Cloud verification token for domain ownership"
  type        = string
} 