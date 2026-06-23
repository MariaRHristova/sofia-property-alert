# ruff: noqa: E501
from __future__ import annotations

import secrets
from dataclasses import dataclass

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models import Listing, ListingMatch, Subscription
from app.schemas import SubscriptionCreate


@dataclass(slots=True)
class SubscriptionView:
    id: int
    user_id: int | None
    email: str
    transaction_type: str
    property_type: str
    city: str
    districts: list[str]
    min_price_eur: float | None
    max_price_eur: float | None
    rooms: str | None
    min_area_sqm: float | None
    unsubscribe_token: str
    active: bool
    initialized: bool


class SubscriptionService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_subscription(self, payload: SubscriptionCreate, *, user_id: int, email: str) -> Subscription:
        subscription = Subscription(
            user_id=user_id,
            email=email,
            transaction_type=payload.transaction_type,
            property_type=payload.property_type,
            city=payload.city,
            districts=",".join(payload.districts),
            min_price_eur=payload.min_price_eur,
            max_price_eur=payload.max_price_eur,
            rooms=payload.rooms,
            min_area_sqm=payload.min_area_sqm,
            unsubscribe_token=secrets.token_urlsafe(24),
        )
        self.session.add(subscription)
        self.session.commit()
        self.session.refresh(subscription)
        return subscription

    def list_subscriptions(self, *, user_id: int) -> list[Subscription]:
        statement = (
            select(Subscription)
            .where(Subscription.user_id == user_id)
            .order_by(Subscription.created_at.desc())
        )
        return list(self.session.scalars(statement))

    def deactivate_subscription(self, token: str, *, user_id: int | None = None) -> bool:
        subscription = self._get_subscription(token, user_id=user_id)
        if subscription is None:
            return False
        self._remove_subscription_matches(subscription.id)
        subscription.active = False
        self.session.commit()
        return True

    def reactivate_subscription(self, token: str, *, user_id: int) -> Subscription | None:
        subscription = self._get_subscription(token, user_id=user_id)
        if subscription is None:
            return None
        subscription.active = True
        self.session.commit()
        self.session.refresh(subscription)
        return subscription

    def delete_subscription(self, token: str, *, user_id: int) -> bool:
        subscription = self._get_subscription(token, user_id=user_id)
        if subscription is None:
            return False
        self._remove_subscription_matches(subscription.id)
        self.session.delete(subscription)
        self.session.flush()
        self._delete_orphan_listings()
        self.session.commit()
        return True

    def _get_subscription(self, token: str, *, user_id: int | None) -> Subscription | None:
        statement = select(Subscription).where(Subscription.unsubscribe_token == token)
        if user_id is not None:
            statement = statement.where(Subscription.user_id == user_id)
        return self.session.scalar(statement)

    def _remove_subscription_matches(self, subscription_id: int) -> None:
        self.session.execute(
            delete(ListingMatch).where(
                ListingMatch.subscription_id == subscription_id
            )
        )
        self.session.flush()
        self._delete_orphan_listings()

    def _delete_orphan_listings(self) -> None:
        self.session.execute(
            delete(Listing).where(~Listing.id.in_(select(ListingMatch.listing_id)))
        )


def to_subscription_view(subscription: Subscription) -> SubscriptionView:
    districts = [
        value.strip() for value in subscription.districts.split(",") if value.strip()
    ]
    return SubscriptionView(
        id=subscription.id,
        user_id=subscription.user_id,
        email=subscription.email,
        transaction_type=subscription.transaction_type,
        property_type=subscription.property_type,
        city=subscription.city,
        districts=districts,
        min_price_eur=subscription.min_price_eur,
        max_price_eur=subscription.max_price_eur,
        rooms=subscription.rooms,
        min_area_sqm=subscription.min_area_sqm,
        unsubscribe_token=subscription.unsubscribe_token,
        active=subscription.active,
        initialized=subscription.initialized,
    )

