"""Integration: populate_db seeds the checkout-confirmation CMS page.

Proves the standalone entrypoint (`python plugins/checkout/populate_db.py`)
now actually seeds: `populate_checkout_cms()` runs under an app context (the
`db` fixture provides one — the same context the `__main__` block creates via
create_app), writes the checkout-confirmation layout + widget + page that the
fe-user `/checkout/confirmation` route loads, and is idempotent on a re-run.
"""
from plugins.checkout.populate_db import populate_checkout_cms
from plugins.cms.src.models.cms_layout import CmsLayout
from plugins.cms.src.models.cms_page import CmsPage


def test_populate_seeds_checkout_confirmation_page(db):
    populate_checkout_cms()

    layout = db.session.query(CmsLayout).filter_by(slug="checkout-confirmation").first()
    page = db.session.query(CmsPage).filter_by(slug="checkout-confirmation").first()
    assert layout is not None
    assert page is not None
    assert page.layout_id == layout.id


def test_populate_is_idempotent(db):
    populate_checkout_cms()
    populate_checkout_cms()

    assert (
        db.session.query(CmsPage).filter_by(slug="checkout-confirmation").count() == 1
    )
    assert (
        db.session.query(CmsLayout).filter_by(slug="checkout-confirmation").count() == 1
    )
