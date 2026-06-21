from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.auth.models import User
from app.auth.dependencies import get_current_active_user
from app.chat.schemas import (
    MessageCreate,
    MessageResponse,
    ConversationResponse,
)
from app.chat.service import (
    get_message_by_id,
    get_conversation_messages,
    get_user_conversations,
    send_message,
    mark_as_read,
    delete_message,
)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get(
    "/conversations",
    response_model=list[ConversationResponse],
)
async def list_conversations(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> list[ConversationResponse]:
    return await get_user_conversations(current_user.id, db)


@router.get(
    "/conversations/{other_user_id}/{listing_id}",
    response_model=list[MessageResponse],
)
async def get_conversation(
    other_user_id: int,
    listing_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> list[MessageResponse]:
    messages = await get_conversation_messages(
        current_user.id,
        other_user_id,
        listing_id,
        db,
    )
    await mark_as_read(current_user.id, other_user_id, listing_id, db)
    return [MessageResponse.model_validate(m) for m in messages]


@router.post(
    "/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def send_new_message(
    data: MessageCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    try:
        message = await send_message(data, current_user, db)
        return MessageResponse.model_validate(message)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/messages/{message_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_existing_message(
    message_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    message = await get_message_by_id(message_id, db)
    if message is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Повідомлення не знайдено",
        )
    if message.sender_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ви не можете видалити чуже повідомлення",
        )
    await delete_message(message, db)