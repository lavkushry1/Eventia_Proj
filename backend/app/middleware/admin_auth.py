from fastapi import Request, HTTPException, status, Depends
from ..core.auth import get_current_user
from ..models.user import User

async def admin_required(current_user: User = Depends(get_current_user)):
    """
    Dependency that checks if the current user has admin privileges.
    Raises HTTP 403 if not an admin.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user 