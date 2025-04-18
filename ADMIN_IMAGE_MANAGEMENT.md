# Admin Image Management

This document explains how to use the admin image management functionality in Eventia.

## Overview

The admin image management feature allows authorized administrators to upload and manage:

1. **Event Posters** - Images displayed on event cards and detail pages
2. **Venue Images** - Images of venues where events take place
3. **Team Logos** - Logos for sports teams (e.g., IPL teams)

## Accessing the Image Management

1. Log in to the admin dashboard using your admin credentials
2. Click on the "Image Management" tab in the dashboard
3. Alternatively, navigate directly to `/admin-images`

## Uploading Images

### Event Posters

1. In the Image Management page, select the "Event Posters" tab
2. Enter the Event ID in the input field
   - You can find Event IDs in the Events Management section
   - If coming from an event edit page, the ID will be pre-filled
3. Click "Choose File" to select your event poster image
   - Supported formats: PNG, JPG, JPEG, WEBP
   - Recommended size: 1200x630 pixels (16:9 ratio)
4. Click "Upload Image"
5. The image will be uploaded and automatically associated with the event

### Team Logos

1. In the Image Management page, select the "Team Logos" tab
2. Enter the Team Code in the input field (e.g., "CSK", "MI")
   - Use the official team code in lowercase
3. Click "Choose File" to select your team logo image
   - Supported formats: PNG, JPG, JPEG, WEBP
   - Recommended size: 500x500 pixels (square with transparent background)
4. Click "Upload Image"
5. The logo will be uploaded and available both on the backend and frontend

### Venue Images

1. In the Image Management page, select the "Venue Images" tab
2. Enter the Venue ID in the input field
3. Click "Choose File" to select your venue image
   - Supported formats: PNG, JPG, JPEG, WEBP
   - Recommended size: 1600x900 pixels
4. Click "Upload Image"
5. The image will be uploaded and associated with the venue

## Image Storage Locations

Images are stored in two locations:

1. **Backend**: 
   - Event posters: `backend/app/static/events/`
   - Venue images: `backend/app/static/venues/`
   - Team logos: `backend/app/static/teams/`

2. **Frontend**: 
   - Team logos are also saved to `eventia-ticketing-flow/public/assets/teams/`
   - This enables fallback loading if the backend is unavailable

## URL Patterns

Images are accessible through these URL patterns:

- Event posters: `{API_BASE_URL}/static/events/{eventId}.{extension}`
- Venue images: `{API_BASE_URL}/static/venues/{venueId}.{extension}`
- Team logos: `{API_BASE_URL}/static/teams/{teamCode}.{extension}`
- Team logos (frontend): `/assets/teams/{teamCode}.{extension}`

## Security

- Only authenticated administrators can upload or update images
- File format validation prevents uploading non-image files
- Images are named after their associated IDs to prevent collisions
- Authorization checks are performed at the API level

## Troubleshooting

If you encounter issues:

1. **Image Not Showing**: Check that the file was uploaded successfully in the preview
2. **Upload Error**: Ensure you're providing a valid ID and file format
3. **Permission Error**: Make sure you're logged in as an administrator

For persistent issues, check the server logs for error details. 