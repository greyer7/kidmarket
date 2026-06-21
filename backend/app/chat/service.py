from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from app.auth.models import User
from app.chat.models import Message
from app.chat.schemas import MessageCreate, MessageResponse, ConversationResponse, MessageShortResponse
from app.users.schemas import UserPublicResponse


async def get_message_by_id(message_id: int, db: AsyncSession) -> Message | None:
    result = await db.execute(select(Message).where(Message.id == message_id))
    return result.scalar_one_or_none()


async def get_conversation_messages(
    user_id: int,
    other_user_id: int,
    listing_id: int,
    db: AsyncSession,
) -> list[Message]:
    result = await db.execute(
        select(Message)
        .where(
            Message.listing_id == listing_id,
            or_(
                and_(Message.sender_id == user_id, Message.receiver_id == other_user_id),
                and_(Message.sender_id == other_user_id, Message.receiver_id == user_id),
            ),
        )
        .order_by(Message.created_at.asc())
    )
    return list(result.scalars().all())


async def get_user_conversations(user_id: int, db: AsyncSession) -> list[ConversationResponse]:
    result = await db.execute(
        select(Message)
        .where(
            or_(
                Message.sender_id == user_id,
                Message.receiver_id == user_id,
            )
        )
        .order_by(Message.created_at.desc())
    )
    messages = list(result.scalars().all())

    conversations: dict[tuple, ConversationResponse] = {}

    for message in messages:
        other_user = message.receiver if message.sender_id == user_id else message.sender
        key = (message.listing_id, other_user.id)

        if key not in conversations:
            unread_count = sum(
                1 for m in messages
                if m.listing_id == message.listing_id
                and m.sender_id == other_user.id
                and m.receiver_id == user_id
                and not m.is_read
            )

            conversations[key] = ConversationResponse(
                listing_id=message.listing_id,
                other_user=UserPublicResponse.model_validate(other_user),
                last_message=MessageShortResponse.model_validate(message),
                unread_count=unread_count,
            )

    return list(conversations.values())


async def send_message(
    data: MessageCreate,
    sender: User,
    db: AsyncSession,
) -> Message:
    if data.receiver_id == sender.id:
        raise ValueError("Не можна надсилати повідомлення самому собі")

    message = Message(
        content=data.content,
        sender_id=sender.id,
        receiver_id=data.receiver_id,
        listing_id=data.listing_id,
    )

    db.add(message)
    await db.flush()
    await db.refresh(message)
    return message


async def mark_as_read(
    user_id: int,
    other_user_id: int,
    listing_id: int,
    db: AsyncSession,
) -> None:
    result = await db.execute(
        select(Message).where(
            Message.listing_id == listing_id,
            Message.sender_id == other_user_id,
            Message.receiver_id == user_id,
            Message.is_read == False,
        )
    )
    messages = list(result.scalars().all())

    for message in messages:
        message.is_read = True

    await db.flush()


async def delete_message(message: Message, db: AsyncSession) -> None:
    await db.delete(message)
    await db.flush()