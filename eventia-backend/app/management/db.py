from ..db.mongodb import engine
from ..config.settings import settings
from odmantic import query


async def init_db():
    """
    Checks if all the necessary settings are in the database and adds them if they are missing.
    """
    settings_collection_name = "settings"  # Name of the settings collection

    # Check if the settings collection exists
    collection_names = await engine.client[settings.DATABASE_NAME].list_collection_names()
    if settings_collection_name not in collection_names:
        # Create the collection if it doesn't exist
        await engine.client[settings.DATABASE_NAME].create_collection(settings_collection_name)
        print(f"Created '{settings_collection_name}' collection.")

    # Define the required settings
    required_settings = {
        "PAYMENT_VPA": settings.PAYMENT_VPA,
        "QR_ENABLED": settings.QR_ENABLED,
        "FRONTEND_BASE_URL": settings.FRONTEND_BASE_URL,
        "API_DOMAIN": settings.API_DOMAIN,
    }

    # Check and add missing settings
    for setting_name, setting_value in required_settings.items():
        setting_exists = await engine.client[settings.DATABASE_NAME][settings_collection_name].find_one(
            {"name": setting_name}
        )

        if not setting_exists:
            await engine.client[settings.DATABASE_NAME][settings_collection_name].insert_one(
                {"name": setting_name, "value": setting_value}
            )
            print(f"Added missing setting: '{setting_name}' with value '{setting_value}'.")