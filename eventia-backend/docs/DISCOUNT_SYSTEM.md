# Eventia Discount System Documentation

This document provides a comprehensive guide to the discount system in Eventia, covering both the technical implementation and administrative usage.

## Overview

The Eventia discount system allows administrators to create and manage promotional codes that customers can apply during checkout to receive price reductions. The system supports both percentage-based and fixed amount discounts, with flexible rules for usage limits, minimum order values, and event-specific promotions.

## For Administrators

### Creating Discount Codes

1. Navigate to the Admin Dashboard → Discount Management section
2. Click "Create New Discount" button
3. Fill in the discount details:
   - **Code**: The discount code customers will enter (e.g., SUMMER25)
   - **Description**: Internal description of the discount
   - **Type**: Percentage or Fixed Amount
   - **Value**: The discount percentage or fixed amount value
   - **Start/End Date**: The validity period
   - **Max Uses**: Maximum number of times this code can be used (optional)
   - **Min Ticket Count**: Minimum number of tickets required to apply the discount
   - **Min Order Value**: Minimum order amount required (optional)
   - **Active**: Whether the code is currently active

### Bulk Generation

For promotional campaigns requiring multiple unique codes:

1. Click "Bulk Generate" button
2. Set the discount parameters:
   - **Prefix**: Optional 1-3 character prefix for generated codes (e.g., SUM for SUMMER)
   - **Quantity**: Number of unique codes to generate (1-100)
   - **Common Parameters**: Type, value, dates, etc.

### Analytics

The analytics dashboard provides insights into discount performance:

1. **Overview Tab**: Shows total usage, total discount amount, and percentage of total revenue
2. **Effectiveness Tab**: Compares conversion rates and average order values between discounted and non-discounted orders
3. **Discount-Specific Analytics**: Click on a specific discount to view its detailed usage stats

### Best Practices

- Create descriptive discount codes that are memorable (e.g., WELCOME25 for 25% off for new customers)
- Set appropriate expiry dates to create urgency
- Use the analytics to determine which discount strategies are most effective
- Regularly archive expired discounts to keep the system clean

## For Developers

### Architecture

The discount system follows the modular architecture pattern defined in ARCHITECTURE.md:

- **Models**: `/app/models/discount.py` - Data schemas and database operations
- **Routers**: 
  - `/app/routers/discounts.py` - Public endpoints
  - `/app/routers/admin_discounts.py` - Admin-only endpoints
- **Utils**: `/app/utils/discount_analytics.py` - Analytics functions
- **Frontend**: 
  - `/src/components/DiscountSection.tsx` - User-facing component
  - `/src/components/DiscountManagement.tsx` - Admin dashboard component

### Database Schema

Discounts are stored in the `discounts` collection with the following structure:

```json
{
  "id": "disc-20250418-abc12345",
  "code": "SUMMER25",
  "description": "Summer sale discount",
  "discount_type": "percentage",
  "value": 25,
  "start_date": "2025-04-18",
  "end_date": "2025-05-18",
  "max_uses": 100,
  "current_uses": 0,
  "min_ticket_count": 1,
  "min_order_value": 500,
  "is_active": true,
  "event_specific": false,
  "event_id": null,
  "created_at": "2025-04-18T10:00:00.000Z",
  "updated_at": "2025-04-18T10:00:00.000Z"
}
```

### API Endpoints

#### Public Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/discounts/` | Create a new discount (admin only) |
| POST | `/discounts/verify` | Verify a discount code applicability |
| GET | `/discounts/` | List all discounts (admin only) |
| GET | `/discounts/{discount_id}` | Get a specific discount |
| PUT | `/discounts/{discount_id}` | Update a discount (admin only) |
| DELETE | `/discounts/{discount_id}` | Delete a discount (admin only) |

#### Admin Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/discounts/analytics/overview` | Get discount usage overview |
| GET | `/admin/discounts/analytics/effectiveness` | Get discount effectiveness report |
| GET | `/admin/discounts/analytics/{discount_id}` | Get analytics for a specific discount |
| POST | `/admin/discounts/bulk-create` | Create multiple discounts |
| POST | `/admin/discounts/generate-codes` | Generate discount codes based on a template |
| POST | `/admin/discounts/archive-expired` | Archive all expired discounts |

### Integration with Bookings

Discounts are applied during the booking process:

1. Customer enters a code in the `DiscountSection` component
2. Frontend calls `/bookings/calculate` endpoint with ticket info and discount code
3. Backend verifies the code's validity and calculates the discount amount
4. If valid, the discount is applied to the order and stored with the booking
5. Upon payment confirmation, the discount usage counter is incremented

### Migration

When transitioning from an old discount system, use the migration script:

```bash
python scripts/migrate_discounts.py
```

This will convert any existing discounts to the new format and create the necessary indexes.

## Troubleshooting

### Common Issues

1. **Discount code not working**: Check that the code is active, within its validity period, and hasn't reached its maximum usage limit.

2. **Missing analytics data**: Ensure both the discount and booking collections have the required indexes.

3. **Bulk generation errors**: Check that the prefix is 3 characters or fewer and the quantity is between 1-100.

### Developer Notes

- The discount verification logic is in `verify_discount()` function in `app/models/discount.py`
- To add new discount types or rules, extend the verification logic and update the frontend components
- All discount codes are stored in uppercase for case-insensitive matching

## Future Enhancements

Planned improvements for the discount system:

1. User-specific discount codes
2. Tiered discounts based on order value
3. Bundle discounts for specific ticket combinations
4. Referral-based discount generation
5. Integration with customer loyalty program

---

Last Updated: April 18, 2025
