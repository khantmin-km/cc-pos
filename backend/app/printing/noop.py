# backend/app/printing/noop.py
from app.printing.adapter import KitchenTicketItem, PrinterAdapter
from app.printing.renderer import render_kitchen_ticket_lines


class NoopPrinterAdapter(PrinterAdapter):
    def print_kitchen_ticket(self, items: list[KitchenTicketItem], mode: str) -> bool:
        if mode == "text":
            render_kitchen_ticket_lines(items)
        return True
