# Frontend-Backend Schema Synchronization

This documentation explains how we've synchronized the backend Pydantic models with the frontend TypeScript interfaces to ensure type safety across the entire application.

## Implementation

### 1. Centralized Type Definitions

We've created a centralized `types.ts` file that contains TypeScript interfaces matching the backend Pydantic models. These types follow the same structure and naming conventions as the backend models.

```typescript
// Example: types.ts defining EventBase, EventCreate, EventResponse, etc.
export interface EventBase {
  title: string;
  description: string;
  date: string; // Format: YYYY-MM-DD
  time: string; // Format: HH:MM (24-hour)
  venue: string;
  category: string;
}

export interface EventCreate extends EventBase {
  // ... additional fields for creation
}

export interface EventResponse extends EventBase {
  id: string;
  // ... additional fields returned by the API
}
```

### 2. Zod Validation Schemas

We've created a `validation.ts` file with Zod validation schemas that mirror the backend Pydantic validation rules. These schemas ensure consistent validation between frontend and backend.

```typescript
// Example: validation.ts defining eventBaseSchema, eventCreateSchema, etc.
export const eventBaseSchema = z.object({
  title: z.string().min(3, "Title must be at least 3 characters"),
  description: z.string().min(10, "Description must be at least 10 characters"),
  date: z.string().regex(dateRegex, "Date must be in YYYY-MM-DD format"),
  // ... other validations
});
```

### 3. Type-Safe API Client

We've updated the API client functions to use these types, ensuring type safety when making API calls.

```typescript
// Example: api.ts using the defined types
export async function adminCreateEvent(eventData: EventCreate): Promise<EventResponse> {
  // Implementation...
}
```

### 4. Adapter Functions

We've created adapter functions to convert between API and UI models, preserving backward compatibility while using strongly typed interfaces.

```typescript
// Example: adapters.ts converting between API and UI models
export const mapApiEventToUIEvent = (apiEvent: ApiEvent): UIEvent => {
  // Implementation...
};
```

### 5. Form Components with Validation

We've created React form components that use Zod validation schemas to validate form inputs before submitting to the API.

```tsx
// Example: EventForm.tsx using Zod validation
const form = useForm<EventCreate>({
  resolver: zodResolver(eventCreateSchema),
  // Implementation...
});
```

## Benefits

### 1. Type Safety

- **Compile-time Errors**: TypeScript catches type errors at compile time, reducing runtime errors.
- **Intellisense Support**: Developers get autocomplete and type hints for API responses and form fields.
- **Refactoring Safety**: When renaming or changing fields, TypeScript helps identify all places that need updating.

### 2. Consistency

- **Single Source of Truth**: Backend Pydantic models are the single source of truth, with frontend types mirroring them.
- **Validation Rules**: Same validation rules applied in both frontend and backend.
- **Naming Conventions**: Consistent naming between frontend and backend.

### 3. Developer Experience

- **Reduced Guesswork**: Developers don't need to guess the shape of API responses.
- **Documentation**: Types serve as documentation for the API.
- **Confidence**: Developers can be confident that their form submissions will be accepted by the backend.

## Maintaining and Updating

When making changes to the backend Pydantic models:

1. Update the corresponding TypeScript interfaces in `types.ts`
2. Update the Zod validation schemas in `validation.ts`
3. Update any adapter functions if needed
4. Update React components and forms that use these types

For advanced scenarios, consider using automatic generation of TypeScript interfaces from OpenAPI schemas or directly from Pydantic models. 