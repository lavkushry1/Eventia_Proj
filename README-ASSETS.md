# Team Assets Management

## Team Logos

### Current Setup
The project includes placeholder logos for all IPL teams:
- CSK (Chennai Super Kings)
- MI (Mumbai Indians)
- RCB (Royal Challengers Bangalore)
- KKR (Kolkata Knight Riders)
- DC (Delhi Capitals)
- SRH (Sunrisers Hyderabad)
- RR (Rajasthan Royals)
- PBKS (Punjab Kings)
- GT (Gujarat Titans)
- LSG (Lucknow Super Giants)

### Logo Locations
Team logos are stored in two locations:

1. **Backend**: `backend/app/static/teams/`
   - These files are served via the FastAPI backend at `/static/teams/{team_code}.png`
   - Example URL: `http://localhost:8000/static/teams/csk.png`

2. **Frontend**: `eventia-ticketing-flow/public/assets/teams/`
   - These files are served directly by the frontend server
   - Example URL: `/assets/teams/csk.png`

### Adding Real Logos
To replace the placeholder logos with real team logos:

1. Prepare your logo images:
   - Format: PNG with transparent background recommended
   - Size: 500×500 pixels (square)
   - Filename: Use the team code in lowercase (e.g., `csk.png`, `mi.png`)

2. Add the images to both locations:
   - Copy to `backend/app/static/teams/`
   - Copy to `eventia-ticketing-flow/public/assets/teams/`

3. No code changes are needed - the application will automatically use your new logos

### Usage in Components
Team logos are displayed using the `TeamLogo` component:

```tsx
<TeamLogo 
  teamCode="csk" 
  size={50} 
  useBackendPath={false} 
/>
```

- Set `useBackendPath={true}` to load from backend API
- Set `useBackendPath={false}` (default) to load from frontend public directory

### Notes
- The fallback mechanism will try the frontend path if the backend path fails
- All team codes should be lowercase
- If you need to add new teams, make sure to update both directories with the new team logos 