"""Checkout flow CMS seeder — shared by every billing-completing plugin.

Seeds the `checkout-confirmation` CMS layout, the `CheckoutConfirmation`
vue-component widget, and the `checkout-confirmation` CMS page that the
fe-user `checkout` plugin's `/checkout/confirmation` route loads via
`CmsPage.vue`.

Any plugin that lands a user on `/checkout/confirmation` after payment
(shop, booking, subscription billing, …) MUST call `populate_checkout_cms()`
from its own populate_db.py so the page exists in the CMS for that
instance. Idempotent — safe to call from multiple seeders.
"""
import logging
from uuid import uuid4

from vbwd.extensions import db

logger = logging.getLogger(__name__)


def populate_checkout_cms() -> None:
    """Seed checkout-confirmation layout + widget + page (idempotent).

    Skips silently when the CMS plugin is not installed.
    """
    try:
        from plugins.cms.src.models.cms_layout import CmsLayout
        from plugins.cms.src.models.cms_widget import CmsWidget
        from plugins.cms.src.models.cms_layout_widget import CmsLayoutWidget
        from plugins.cms.src.models.cms_page import CmsPage
    except ImportError:
        logger.info("[checkout] CMS plugin not installed — skipping CMS content")
        return

    def _get_or_create(model, slug, **kwargs):
        obj = db.session.query(model).filter_by(slug=slug).first()
        if obj:
            return obj, False
        obj = model(slug=slug, **kwargs)
        db.session.add(obj)
        db.session.flush()
        return obj, True

    def _assign_widget(layout, widget, area_name, sort_order=0):
        exists = (
            db.session.query(CmsLayoutWidget)
            .filter_by(layout_id=layout.id, widget_id=widget.id, area_name=area_name)
            .first()
        )
        if not exists:
            db.session.add(
                CmsLayoutWidget(
                    layout_id=layout.id,
                    widget_id=widget.id,
                    area_name=area_name,
                    sort_order=sort_order,
                )
            )
            db.session.flush()

    layout, layout_created = _get_or_create(
        CmsLayout,
        "checkout-confirmation",
        name="Checkout Confirmation",
        description="Post-payment confirmation — invoice details, status, support info",
        areas=[
            {"name": "header", "type": "header", "label": "Header"},
            {"name": "confirmation", "type": "vue", "label": "Order Confirmation"},
            {"name": "content-below", "type": "content", "label": "Support & Info"},
            {"name": "footer", "type": "footer", "label": "Footer"},
        ],
        sort_order=41,
        is_active=True,
    )
    if layout_created:
        logger.info("[checkout] Created CMS layout: checkout-confirmation")

    widget, _ = _get_or_create(
        CmsWidget,
        "checkout-confirmation",
        name="Checkout Confirmation",
        widget_type="vue-component",
        content_json={"component": "CheckoutConfirmation"},
        is_active=True,
    )
    _assign_widget(layout, widget, "confirmation", 0)

    header_nav = db.session.query(CmsWidget).filter_by(slug="header-nav").first()
    footer_nav = db.session.query(CmsWidget).filter_by(slug="footer-nav").first()
    if header_nav:
        _assign_widget(layout, header_nav, "header", 0)
    if footer_nav:
        _assign_widget(layout, footer_nav, "footer", 0)

    page, page_created = _get_or_create(
        CmsPage,
        "checkout-confirmation",
        name="Order Confirmation",
        language="en",
        content_json={"type": "doc", "content": []},
        is_published=True,
        layout_id=layout.id,
        meta_title="Order Confirmation",
        meta_description="Your order has been received",
        robots="noindex,nofollow",
    )

    if page_created:
        try:
            from plugins.cms.src.models.cms_page_content_block import (
                CmsPageContentBlock,
            )

            support_html = (
                '<div class="login-cta" style="text-align:center;padding:32px 24px;background:#fff;'
                'border-radius:12px;margin-bottom:24px;box-shadow:0 1px 3px rgba(0,0,0,0.08)">'
                '<p style="color:#666;font-size:15px;margin-bottom:16px">'
                "Your account is ready. Log in to access your dashboard and manage your orders.</p>"
                '<a href="/login" style="display:inline-block;padding:14px 40px;background:#1a1a1a;'
                'color:#fff;text-decoration:none;border-radius:8px;font-weight:600;font-size:15px">'
                "Log in to your account</a></div>"
                '<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:24px">'
                '<div style="background:#fff;border-radius:12px;padding:24px;box-shadow:0 1px 3px rgba(0,0,0,0.08)">'
                '<h3 style="font-size:16px;font-weight:600;margin-bottom:10px">Need help?</h3>'
                '<ul style="list-style:none;padding:0">'
                '<li style="padding:6px 0;font-size:14px">Email: <a href="mailto:support@example.com" '
                'style="color:#3b82f6;text-decoration:none">support@example.com</a></li>'
                '<li style="padding:6px 0;font-size:14px">Response time: within 24 hours</li></ul></div>'
                '<div style="background:#fff;border-radius:12px;padding:24px;box-shadow:0 1px 3px rgba(0,0,0,0.08)">'
                '<h3 style="font-size:16px;font-weight:600;margin-bottom:10px">Frequently asked</h3>'
                '<ul style="list-style:none;padding:0">'
                '<li><a href="/faq#delivery" style="display:block;padding:8px 0;font-size:14px;'
                'color:#1a1a1a;text-decoration:none;border-bottom:1px solid #f0f0f0">Delivery and activation</a></li>'
                '<li><a href="/faq#returns" style="display:block;padding:8px 0;font-size:14px;'
                'color:#1a1a1a;text-decoration:none;border-bottom:1px solid #f0f0f0">Return and refund policy</a></li>'
                '<li><a href="/faq#billing" style="display:block;padding:8px 0;font-size:14px;'
                'color:#1a1a1a;text-decoration:none">Billing and invoices</a></li></ul></div></div>'
            )

            db.session.add(
                CmsPageContentBlock(
                    id=uuid4(),
                    page_id=page.id,
                    area_name="content-below",
                    content_html=support_html,
                    sort_order=0,
                )
            )
            logger.info("[checkout] Seeded checkout-confirmation content-below block")
        except ImportError:
            pass

    db.session.commit()
    logger.info("[checkout] Checkout-confirmation CMS content populated")


if __name__ == "__main__":
    from vbwd.app import create_app

    app = create_app()
    with app.app_context():
        populate_checkout_cms()
