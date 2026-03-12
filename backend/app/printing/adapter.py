# backend/app/printing/adapter.py
from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True)
class KitchenTicketItem:
    order_item_id: UUID
    table_code: str
    menu_item_name: str
    note: str | None


class PrinterAdapter(Protocol):
    def print_kitchen_ticket(self, items: list[KitchenTicketItem], mode: str) -> bool:
        ...
