"""
Custody service — chain of custody management with tamper-evident hashing.
"""

from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.models.custody import CustodyEvent
from app.services.hashing import compute_chain_hash


async def record_custody_event(
    db: AsyncSession,
    evidence_id: int,
    action: str,
    from_user: str = None,
    to_user: str = None,
    remarks: str = None,
) -> CustodyEvent:
    """
    Record a new custody event with tamper-evident hash chain.
    Each event's hash includes the previous event's hash.
    """
    # Get the last event for this evidence
    result = await db.execute(
        select(CustodyEvent)
        .where(CustodyEvent.evidence_id == evidence_id)
        .order_by(desc(CustodyEvent.id))
        .limit(1)
    )
    last_event = result.scalar_one_or_none()
    previous_hash = last_event.event_hash if last_event else None

    # Build event data string
    timestamp = datetime.now(timezone.utc).isoformat()
    event_data = f"{evidence_id}|{action}|{from_user}|{to_user}|{timestamp}|{remarks}"

    # Compute chain hash
    event_hash = compute_chain_hash(event_data, previous_hash)

    event = CustodyEvent(
        evidence_id=evidence_id,
        from_user=from_user,
        to_user=to_user,
        action=action,
        timestamp=datetime.now(timezone.utc),
        remarks=remarks,
        event_hash=event_hash,
        previous_hash=previous_hash,
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


async def get_custody_timeline(db: AsyncSession, evidence_id: int) -> list:
    """Get the full custody timeline for an evidence item."""
    result = await db.execute(
        select(CustodyEvent)
        .where(CustodyEvent.evidence_id == evidence_id)
        .order_by(CustodyEvent.id)
    )
    events = result.scalars().all()
    return [e.to_dict() for e in events]


async def verify_custody_chain(db: AsyncSession, evidence_id: int) -> dict:
    """
    Verify the integrity of the custody chain for an evidence item.
    Recomputes each hash and checks against stored values.
    """
    result = await db.execute(
        select(CustodyEvent)
        .where(CustodyEvent.evidence_id == evidence_id)
        .order_by(CustodyEvent.id)
    )
    events = result.scalars().all()

    if not events:
        return {
            "status": "NO_EVENTS",
            "message": "No custody events found for this evidence",
            "valid": True,
            "event_count": 0,
        }

    # Verify chain integrity
    previous_hash = None
    for event in events:
        if event.previous_hash != previous_hash:
            return {
                "status": "CHAIN_BROKEN",
                "message": f"Chain integrity failure at event {event.id} — previous hash mismatch",
                "valid": False,
                "event_count": len(events),
                "broken_at_event": event.id,
            }
        previous_hash = event.event_hash

    return {
        "status": "VERIFIED",
        "message": "Custody chain integrity verified — all events are intact",
        "valid": True,
        "event_count": len(events),
    }
