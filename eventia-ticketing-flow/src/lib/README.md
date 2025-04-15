# Schema Synchronization

This directory contains files that ensure schema consistency between the backend Pydantic models and frontend TypeScript interfaces.

## Key Files

- **types.ts**: Contains TypeScript interfaces that mirror the backend Pydantic models
- **validation.ts**: Contains Zod validation schemas that mirror the backend validation rules
- **adapters.ts**: Contains functions to convert between API and UI models
- **api.ts**: Contains API client functions that use the typed interfaces

## Maintaining Schema Consistency

When changes are made to the backend Pydantic models, make corresponding changes to:

1. `types.ts` - Update the TypeScript interfaces
2. `validation.ts` - Update the Zod validation schemas
3. Ensure any component that uses these models is updated accordingly

## Type Hierarchy

The type hierarchy follows the backend structure:

1. Base models (e.g., `EventBase`) define common fields
2. Create models (e.g., `EventCreate`) extend base models and are used for creating new resources
3. Update models (e.g., `EventUpdate`) make all fields optional and are used for partial updates
4. Response models (e.g., `EventResponse`) represent what the API returns, including IDs and timestamps

## Using Validation

Example of validating a form with Zod before submission:

```typescript
import { eventCreateSchema } from '../lib/validation';
import { EventCreate } from '../lib/types';

// In your form submission handler
const formData = {
  title: 'My Event',
  description: 'Event description',
  // ... other fields
};

try {
  // Validate against the schema
  const validatedData = eventCreateSchema.parse(formData);
  // Submit valid data to API
  await api.adminCreateEvent(validatedData);
} catch (error) {
  // Handle validation errors
  if (error instanceof z.ZodError) {
    const formattedErrors = error.errors.map(err => ({
      path: err.path.join('.'),
      message: err.message
    }));
    console.error('Validation errors:', formattedErrors);
    // Update form error state
  }
}
```

## Legacy API Support

For backward compatibility, there are some additional interfaces like:

- `LegacyApiEvent`: Extends `ApiEvent` with legacy fields that might exist in older API responses
- `LegacyApiBookingResponse`: Similar extension for booking responses

These are used in adapter functions to handle legacy API formats while maintaining type safety. 