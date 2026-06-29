"""Checkout plugin — seeds the shared checkout-confirmation CMS flow.

This plugin ships no routes of its own. It exists to provide the
``checkout-confirmation`` CMS layout, widget, and page (see ``populate_db.py``)
that every billing-completing plugin (shop, booking, subscription) lands users
on after payment. The ``BasePlugin`` subclass gives it real metadata so the
platform's version scheme and dependency tooling can see it like any other
plugin.
"""
from vbwd.plugins.base import BasePlugin, PluginMetadata


class CheckoutPlugin(BasePlugin):
    """Checkout-confirmation CMS seeder plugin (no routes of its own)."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="checkout",
            version="26.6.1",
            author="VBWD Team",
            description="Shared checkout-confirmation CMS flow seeder",
            dependencies=[],
        )
