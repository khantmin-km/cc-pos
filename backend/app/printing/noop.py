# backend/app/printing/noop.py
from app.printing.adapter import KitchenTicketItem, PrinterAdapter


class NoopPrinterAdapter(PrinterAdapter):
    def print_kitchen_ticket(self, items: list[KitchenTicketItem], mode: str) -> bool:
        return True
