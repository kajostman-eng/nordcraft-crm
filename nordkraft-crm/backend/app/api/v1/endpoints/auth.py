from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password, create_access_token, hash_password
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.models import User
from app.schemas.schemas import AuthLoginRequest, AuthToken, UserOut, BootstrapAdminRequest


router = APIRouter()


@router.post("/bootstrap", response_model=UserOut, status_code=201)
async def bootstrap_admin(payload: BootstrapAdminRequest, db: AsyncSession = Depends(get_db)):
    """
    Create the first admin user.
    Only allowed when there are no users yet.
    """
    users_count = await db.execute(select(func.count(User.id)))
    if (users_count.scalar() or 0) > 0:
        raise HTTPException(status_code=403, detail="Bootstrap already completed")

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        role="admin",
        is_active=True,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=AuthToken)
async def login(payload: AuthLoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.password_hash:
        raise HTTPException(status_code=401, detail="Password login not configured for this user")
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(subject=user.id, role=user.role)
    return AuthToken(access_token=token)


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user)):
    return user

