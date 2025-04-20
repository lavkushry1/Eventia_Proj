# Backend Migration Notice

This folder is no longer actively used for development. Important components have been migrated to the `eventia-backend` folder.

## Migration Status

The following components have been migrated:

1. **Stadium Data and Management**: 
   - Data models for Indian stadiums (`app/data/indian_stadiums.py`) -> `eventia-backend/app/data/indian_stadiums.py`
   - Stadium routes -> `eventia-backend/app/views/stadium_routes.py` 
   - Stadium model -> `eventia-backend/app/models/stadium.py`
   - Stadium controller -> `eventia-backend/app/controllers/stadium_controller.py`

## Using the Migrated Code

To use the migrated stadium functionality in the eventia-backend:

1. Access the stadium APIs at the same routes as before
2. Use the stadium seeding script: `python eventia-backend/seed_stadiums.py`
3. The stadium model and controller follow the same pattern as other eventia-backend components

## Notes

This folder is kept for reference but should not be used for new development. Please direct all new work to the `eventia-backend` folder. 