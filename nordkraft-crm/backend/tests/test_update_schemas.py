import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.schemas.schemas import (  # noqa: E402
    ClientUpdate,
    OfferItemUpdate,
    OfferUpdate,
    ProductUpdate,
)


class UpdateSchemaTests(unittest.TestCase):
    def test_client_update_ignores_relationship_fields(self):
        payload = ClientUpdate.model_validate(
            {
                "company_name": "NordKraft",
                "projects": [],
                "tasks": [],
                "contacts": [],
            }
        )

        self.assertEqual(payload.model_dump(exclude_unset=True), {"company_name": "NordKraft"})

    def test_offer_update_ignores_relationship_and_owner_fields(self):
        payload = OfferUpdate.model_validate(
            {
                "title": "Renewal",
                "items": [],
                "created_by": "attacker-user-id",
            }
        )

        self.assertEqual(payload.model_dump(exclude_unset=True), {"title": "Renewal"})

    def test_offer_item_update_ignores_reparenting_fields(self):
        payload = OfferItemUpdate.model_validate(
            {
                "quantity": 3,
                "offer_id": "other-offer-id",
                "product_id": "other-product-id",
            }
        )

        self.assertEqual(payload.model_dump(exclude_unset=True), {"quantity": 3})

    def test_product_update_ignores_identity_fields(self):
        payload = ProductUpdate.model_validate(
            {
                "name": "Automation sprint",
                "id": "replacement-product-id",
                "created_at": "2026-05-15T11:00:00",
            }
        )

        self.assertEqual(payload.model_dump(exclude_unset=True), {"name": "Automation sprint"})


if __name__ == "__main__":
    unittest.main()
