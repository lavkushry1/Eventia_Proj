# Admin User Setup Guide

This guide explains how to set up admin users for the Eventia platform. The platform now supports username/password authentication for admin users instead of just using access tokens.

## Setting Up the First Admin User

There are two ways to set up the first admin user:

### Option 1: Using the API (Recommended)

1. Make sure the backend server is running.
2. Run the provided script:

```bash
python scripts/create_admin.py
```

The script will prompt you for:
- Username
- Email
- Password
- Admin token (this is the existing token from your .env file, like "devsecrettoken123")

You can also provide these values as command-line arguments:

```bash
python scripts/create_admin.py --username admin --email admin@example.com --password yourpassword --admin-token devsecrettoken123
```

### Option 2: Direct MongoDB Insertion (Advanced)

If you have direct access to the MongoDB database, you can use the bootstrap script:

```bash
python eventia-backend/seed_admin.py
```

This will prompt for the same information but will insert the user directly into MongoDB.

## Logging In

Once you've created an admin user, you can log in through the admin login page at:

```
http://localhost:8080/admin-login
```

The login page now supports both:
- Username and password authentication
- Legacy token-based authentication

## Creating Additional Admin Users

Additional admin users can only be created by existing admins. This feature will be available in a future update to the admin dashboard.

## Security Notes

1. Always use strong passwords for admin accounts.
2. The admin token is still required for initial setup but can be phased out once user accounts are established.
3. Admin sessions expire after 24 hours, requiring re-login.
4. All admin API actions are logged for security auditing.

## Troubleshooting

- If you encounter issues with admin login, check that the backend server is running.
- For password reset, use the `seed_admin.py` script with MongoDB access or contact a system administrator.
- The token-based login remains available as a fallback authentication method. 