# backend/app/printing/renderer.py
import textwrap

from app.printing.adapter import KitchenTicketItem


DEFAULT_PRINTER_WIDTH = 42


def _render_modifier_group_line(group_name: str, option_labels: tuple[str, ...], line_width: int) -> list[str]:
    prefix = f"  {group_name}: "
    options_text = ", ".join(option_labels)
    available_width = max(1, line_width - len(prefix))
    wrapped_options = textwrap.wrap(
        options_text,
        width=available_width,
        break_long_words=False,
        break_on_hyphens=False,
    )
    if not wrapped_options:
        return [prefix.rstrip()]
    lines = [f"{prefix}{wrapped_options[0]}"]
    continuation_indent = " " * len(prefix)
    for continuation in wrapped_options[1:]:
        lines.append(f"{continuation_indent}{continuation}")
    return lines


def render_kitchen_ticket_lines(
    items: list[KitchenTicketItem],
    *,
    line_width: int = DEFAULT_PRINTER_WIDTH,
) -> list[str]:
    lines: list[str] = []
    for item in items:
        lines.append(f"[{item.table_code}] {item.menu_item_name}")
        for modifier_group in item.modifier_groups:
            lines.extend(
                _render_modifier_group_line(
                    modifier_group.group_name,
                    modifier_group.option_labels,
                    line_width,
                )
            )
        if item.note:
            lines.append(f"  Note: {item.note}")
    return lines
