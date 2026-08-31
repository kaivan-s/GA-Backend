"""Dodo Payments adapter.

Handles checkout session creation and webhook verification for subscription management.
Kept isolated so billing logic stays provider-agnostic (LLD §5).
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from dodopayments import DodoPayments


@dataclass
class CheckoutSession:
    session_id: str
    checkout_url: str


@dataclass
class WebhookEvent:
    event_type: str
    subscription_id: str | None
    customer_id: str | None
    product_id: str | None
    status: str | None
    payload: dict


class DodoClient:
    def __init__(self):
        api_key = os.environ.get("DODO_PAYMENTS_API_KEY")
        webhook_key = os.environ.get("DODO_PAYMENTS_WEBHOOK_KEY")
        environment = os.environ.get("DODO_PAYMENTS_ENV", "live_mode")
        
        self._client = DodoPayments(
            bearer_token=api_key,
            webhook_key=webhook_key,
            environment=environment,
        )

    def create_checkout_session(
        self,
        product_id: str,
        customer_id: str | None = None,
        customer_email: str | None = None,
        return_url: str | None = None,
        metadata: dict | None = None,
    ) -> CheckoutSession:
        """Create a checkout session for a subscription product."""
        params = {
            "product_cart": [{"product_id": product_id, "quantity": 1}],
        }
        
        if return_url:
            params["return_url"] = return_url
        
        if customer_id:
            params["customer"] = {"customer_id": customer_id}
        elif customer_email:
            params["customer"] = {"email": customer_email}
        
        if metadata:
            params["metadata"] = metadata
        
        session = self._client.checkout_sessions.create(**params)
        
        return CheckoutSession(
            session_id=session.session_id,
            checkout_url=session.checkout_url,
        )

    def verify_webhook(self, raw_body: str, headers: dict) -> WebhookEvent:
        """Verify and parse a webhook from Dodo Payments."""
        webhook_headers = {
            "webhook-id": headers.get("webhook-id", ""),
            "webhook-signature": headers.get("webhook-signature", ""),
            "webhook-timestamp": headers.get("webhook-timestamp", ""),
        }
        
        event = self._client.webhooks.unwrap(raw_body, headers=webhook_headers)
        
        data = event.get("data", {})
        
        return WebhookEvent(
            event_type=event.get("type", ""),
            subscription_id=data.get("subscription_id"),
            customer_id=data.get("customer_id") or data.get("customer", {}).get("customer_id"),
            product_id=data.get("product_id"),
            status=data.get("status"),
            payload=event,
        )

    def get_subscription(self, subscription_id: str) -> dict:
        """Get subscription details."""
        return self._client.subscriptions.retrieve(subscription_id)

    def cancel_subscription(self, subscription_id: str) -> dict:
        """Cancel a subscription."""
        return self._client.subscriptions.update(subscription_id, status="cancelled")
