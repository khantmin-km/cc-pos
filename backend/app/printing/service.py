# backend/app/printing/service.py
from app.core.config import settings
from app.printing.adapter import KitchenTicketItem
from app.printing.noop import NoopPrinterAdapter


PRINTER_ADAPTER = NoopPrinterAdapter()


def print_kitchen_ticket(items: list[KitchenTicketItem]) -> bool:
    return PRINTER_ADAPTER.print_kitchen_ticket(items, settings.print_mode)
