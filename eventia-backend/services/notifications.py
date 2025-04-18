"""
Notifications service module.

This module provides functionality for sending email and SMS notifications
to users of the Eventia ticketing system.
"""
import smtplib
import asyncio
import aiohttp
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional, Union
import json
import os
from datetime import datetime

from ..core.config import settings, logger

class EmailNotification:
    """
    Email notification handler class.
    
    This class handles the creation and sending of email notifications
    through SMTP.
    """
    
    @staticmethod
    async def send_email(
        recipients: List[str],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        reply_to: Optional[str] = None,
        sender: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send an email to recipients.
        
        Args:
            recipients: List of email addresses to send to
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text content of the email (fallback for HTML)
            cc: List of CC recipients
            bcc: List of BCC recipients
            reply_to: Reply-to email address
            sender: Sender email address (defaults to configured sender)
            
        Returns:
            Dictionary with sending result
        """
        if not settings.SMTP_HOST or not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            logger.warning("SMTP is not configured properly. Email not sent.")
            return {
                "success": False,
                "message": "SMTP is not configured properly",
                "error": "Missing SMTP configuration"
            }
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = sender or f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
            message["To"] = ", ".join(recipients)
            
            if cc:
                message["Cc"] = ", ".join(cc)
            if reply_to:
                message["Reply-To"] = reply_to
                
            # Add text and HTML parts
            if text_content:
                part1 = MIMEText(text_content, "plain")
                message.attach(part1)
                
            part2 = MIMEText(html_content, "html")
            message.attach(part2)
            
            # Combine all recipients for sending
            all_recipients = recipients.copy()
            if cc:
                all_recipients.extend(cc)
            if bcc:
                all_recipients.extend(bcc)
            
            # Send email asynchronously
            await asyncio.to_thread(
                EmailNotification._send_smtp_email,
                message, 
                all_recipients
            )
            
            logger.info(f"Email sent to {len(recipients)} recipients. Subject: {subject}")
            
            return {
                "success": True,
                "message": f"Email sent to {len(recipients)} recipients",
                "recipients": recipients
            }
        
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return {
                "success": False,
                "message": "Failed to send email",
                "error": str(e)
            }
    
    @staticmethod
    def _send_smtp_email(message: MIMEMultipart, recipients: List[str]) -> None:
        """
        Send email via SMTP (sync method for running in thread).
        
        Args:
            message: The email message to send
            recipients: List of recipient email addresses
        """
        try:
            # Connect to SMTP server
            if settings.SMTP_TLS:
                server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT)
                
            # Login
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            
            # Send email
            server.sendmail(
                settings.EMAILS_FROM_EMAIL,
                recipients,
                message.as_string()
            )
            
            # Quit session
            server.quit()
        
        except Exception as e:
            logger.error(f"SMTP error: {str(e)}")
            raise
    
    @staticmethod
    async def send_booking_confirmation(
        booking: Dict[str, Any],
        event: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send booking confirmation email.
        
        Args:
            booking: Booking data
            event: Event data
            
        Returns:
            Email sending result
        """
        # Get recipient email
        recipient = booking["customer_info"]["email"]
        
        # Prepare subject
        subject = f"Booking Confirmation - {event['title']}"
        
        # Get booking date in readable format
        booking_date = datetime.fromisoformat(booking["booking_date"].replace("Z", "+00:00"))
        formatted_booking_date = booking_date.strftime("%d %b %Y, %I:%M %p")
        
        # Prepare email content
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                <div style="text-align: center; margin-bottom: 20px;">
                    <h1 style="color: #0052cc;">Booking Confirmed</h1>
                </div>
                
                <p>Dear {booking["customer_info"]["name"]},</p>
                
                <p>Thank you for your booking. Your tickets for <strong>{event["title"]}</strong> have been confirmed.</p>
                
                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h2 style="margin-top: 0; color: #0052cc;">Booking Details</h2>
                    <p><strong>Booking ID:</strong> {booking["booking_id"]}</p>
                    <p><strong>Event:</strong> {event["title"]}</p>
                    <p><strong>Date:</strong> {event["date"]}</p>
                    <p><strong>Time:</strong> {event["time"]}</p>
                    <p><strong>Venue:</strong> {event["venue"]}</p>
                    <p><strong>Quantity:</strong> {booking["quantity"]}</p>
                    <p><strong>Total Amount:</strong> ₹{booking["total_amount"]}</p>
                    <p><strong>Booking Date:</strong> {formatted_booking_date}</p>
                </div>
                
                <p>Your tickets will be available for download from your account once payment is verified.</p>
                
                <p>If you have any questions, please contact our support team.</p>
                
                <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
                    <p style="font-size: 12px; color: #777;">
                        &copy; {datetime.now().year} Eventia Ticketing. All rights reserved.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Booking Confirmed
        
        Dear {booking["customer_info"]["name"]},
        
        Thank you for your booking. Your tickets for {event["title"]} have been confirmed.
        
        Booking Details:
        Booking ID: {booking["booking_id"]}
        Event: {event["title"]}
        Date: {event["date"]}
        Time: {event["time"]}
        Venue: {event["venue"]}
        Quantity: {booking["quantity"]}
        Total Amount: ₹{booking["total_amount"]}
        Booking Date: {formatted_booking_date}
        
        Your tickets will be available for download from your account once payment is verified.
        
        If you have any questions, please contact our support team.
        
        © {datetime.now().year} Eventia Ticketing. All rights reserved.
        """
        
        # Send email
        return await EmailNotification.send_email(
            recipients=[recipient],
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
    
    @staticmethod
    async def send_payment_confirmation(
        booking: Dict[str, Any],
        event: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send payment confirmation email.
        
        Args:
            booking: Booking data
            event: Event data
            
        Returns:
            Email sending result
        """
        # Get recipient email
        recipient = booking["customer_info"]["email"]
        
        # Prepare subject
        subject = f"Payment Confirmed - {event['title']}"
        
        # Generate QR code URL (if available)
        qr_code_url = booking.get("qr_code", "")
        qr_code_html = ""
        if qr_code_url:
            qr_code_html = f"""
            <div style="text-align: center; margin: 20px 0;">
                <h3>Your Ticket QR Code</h3>
                <img src="{qr_code_url}" alt="Ticket QR Code" style="max-width: 200px; border: 1px solid #ddd; padding: 10px;">
                <p style="font-size: 12px; color: #777;">Show this QR code at the venue entrance</p>
            </div>
            """
        
        # Prepare email content
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                <div style="text-align: center; margin-bottom: 20px;">
                    <h1 style="color: #00a650;">Payment Confirmed</h1>
                </div>
                
                <p>Dear {booking["customer_info"]["name"]},</p>
                
                <p>Great news! Your payment for <strong>{event["title"]}</strong> has been confirmed.</p>
                
                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h2 style="margin-top: 0; color: #00a650;">Payment Details</h2>
                    <p><strong>Booking ID:</strong> {booking["booking_id"]}</p>
                    <p><strong>Event:</strong> {event["title"]}</p>
                    <p><strong>Total Amount Paid:</strong> ₹{booking["total_amount"]}</p>
                    <p><strong>Payment Method:</strong> {booking["payment_method"].upper()}</p>
                    <p><strong>Payment Status:</strong> COMPLETED</p>
                </div>
                
                {qr_code_html}
                
                <p>Thank you for your purchase. We look forward to seeing you at the event!</p>
                
                <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
                    <p style="font-size: 12px; color: #777;">
                        &copy; {datetime.now().year} Eventia Ticketing. All rights reserved.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Payment Confirmed
        
        Dear {booking["customer_info"]["name"]},
        
        Great news! Your payment for {event["title"]} has been confirmed.
        
        Payment Details:
        Booking ID: {booking["booking_id"]}
        Event: {event["title"]}
        Total Amount Paid: ₹{booking["total_amount"]}
        Payment Method: {booking["payment_method"].upper()}
        Payment Status: COMPLETED
        
        Thank you for your purchase. We look forward to seeing you at the event!
        
        © {datetime.now().year} Eventia Ticketing. All rights reserved.
        """
        
        # Send email
        return await EmailNotification.send_email(
            recipients=[recipient],
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )


class SMSNotification:
    """
    SMS notification handler class.
    
    This class handles the creation and sending of SMS notifications
    through various SMS gateway providers.
    """
    
    @staticmethod
    async def send_sms(
        phone_number: str,
        message: str,
        sender_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send an SMS to a phone number.
        
        Args:
            phone_number: Recipient phone number
            message: SMS message content
            sender_id: Sender ID (optional)
            
        Returns:
            Dictionary with sending result
        """
        # Check if SMS configuration is available
        if not hasattr(settings, "SMS_API_KEY") or not settings.SMS_API_KEY:
            logger.warning("SMS API is not configured. SMS not sent.")
            return {
                "success": False,
                "message": "SMS API is not configured",
                "error": "Missing SMS configuration"
            }
        
        try:
            # In a real implementation, this would call an SMS gateway API
            # This is a placeholder for demonstration purposes
            
            # For demonstration, logging the SMS that would be sent
            logger.info(f"SMS would be sent to {phone_number}: {message}")
            
            # Simulate API call to SMS gateway
            await asyncio.sleep(0.5)  # Simulate API delay
            
            return {
                "success": True,
                "message": "SMS sent successfully",
                "recipient": phone_number
            }
        
        except Exception as e:
            logger.error(f"Error sending SMS: {str(e)}")
            return {
                "success": False,
                "message": "Failed to send SMS",
                "error": str(e)
            }
    
    @staticmethod
    async def send_booking_confirmation_sms(
        booking: Dict[str, Any],
        event: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send booking confirmation SMS.
        
        Args:
            booking: Booking data
            event: Event data
            
        Returns:
            SMS sending result
        """
        # Get recipient phone number
        phone_number = booking["customer_info"]["phone"]
        
        # Prepare SMS content
        message = (
            f"Booking Confirmed for {event['title']}. "
            f"Booking ID: {booking['booking_id']}. "
            f"Amount: ₹{booking['total_amount']}. "
            f"Thank you for booking with Eventia!"
        )
        
        # Send SMS
        return await SMSNotification.send_sms(
            phone_number=phone_number,
            message=message
        )
    
    @staticmethod
    async def send_payment_confirmation_sms(
        booking: Dict[str, Any],
        event: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send payment confirmation SMS.
        
        Args:
            booking: Booking data
            event: Event data
            
        Returns:
            SMS sending result
        """
        # Get recipient phone number
        phone_number = booking["customer_info"]["phone"]
        
        # Prepare SMS content
        message = (
            f"Payment Confirmed for {event['title']}. "
            f"Booking ID: {booking['booking_id']}. "
            f"Amount: ₹{booking['total_amount']}. "
            f"Show your booking ID at the venue. Thank you!"
        )
        
        # Send SMS
        return await SMSNotification.send_sms(
            phone_number=phone_number,
            message=message
        )


async def send_booking_notifications(
    booking: Dict[str, Any],
    event: Dict[str, Any],
    notification_types: List[str] = ["email", "sms"]
) -> Dict[str, Any]:
    """
    Send booking notifications (email and/or SMS).
    
    Args:
        booking: Booking data
        event: Event data
        notification_types: List of notification types to send
        
    Returns:
        Dictionary with sending results
    """
    results = {}
    
    try:
        # Send email notification
        if "email" in notification_types:
            email_result = await EmailNotification.send_booking_confirmation(booking, event)
            results["email"] = email_result
        
        # Send SMS notification
        if "sms" in notification_types:
            sms_result = await SMSNotification.send_booking_confirmation_sms(booking, event)
            results["sms"] = sms_result
        
        return {
            "success": True,
            "message": "Notifications sent successfully",
            "results": results
        }
    
    except Exception as e:
        logger.error(f"Error sending booking notifications: {str(e)}")
        return {
            "success": False,
            "message": "Failed to send notifications",
            "error": str(e),
            "results": results
        }

async def send_payment_notifications(
    booking: Dict[str, Any],
    event: Dict[str, Any],
    notification_types: List[str] = ["email", "sms"]
) -> Dict[str, Any]:
    """
    Send payment confirmation notifications (email and/or SMS).
    
    Args:
        booking: Booking data
        event: Event data
        notification_types: List of notification types to send
        
    Returns:
        Dictionary with sending results
    """
    results = {}
    
    try:
        # Send email notification
        if "email" in notification_types:
            email_result = await EmailNotification.send_payment_confirmation(booking, event)
            results["email"] = email_result
        
        # Send SMS notification
        if "sms" in notification_types:
            sms_result = await SMSNotification.send_payment_confirmation_sms(booking, event)
            results["sms"] = sms_result
        
        return {
            "success": True,
            "message": "Payment notifications sent successfully",
            "results": results
        }
    
    except Exception as e:
        logger.error(f"Error sending payment notifications: {str(e)}")
        return {
            "success": False,
            "message": "Failed to send payment notifications",
            "error": str(e),
            "results": results
        }
