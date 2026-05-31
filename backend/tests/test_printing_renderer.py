from uuid import uuid4

from app.printing.adapter import KitchenTicketItem, KitchenTicketModifierGroup
from app.printing.renderer import render_kitchen_ticket_lines


def test_render_kitchen_ticket_lines_groups_modifier_options() -> None:
    items = [
        KitchenTicketItem(
            order_item_id=uuid4(),
            table_code="A1",
            menu_item_name="Thai Noodle",
            note="less spicy",
            modifier_groups=(
                KitchenTicketModifierGroup(
                    group_name="Add-on",
                    option_labels=("Boiled Egg", "Pork Crackling"),
                ),
            ),
        )
    ]

    lines = render_kitchen_ticket_lines(items, line_width=60)

    assert lines == [
        "[A1] Thai Noodle",
        "  Add-on: Boiled Egg, Pork Crackling",
        "  Note: less spicy",
    ]


def test_render_kitchen_ticket_lines_wraps_long_modifier_line() -> None:
    items = [
        KitchenTicketItem(
            order_item_id=uuid4(),
            table_code="A1",
            menu_item_name="Thai Noodle",
            note=None,
            modifier_groups=(
                KitchenTicketModifierGroup(
                    group_name="Add-on",
                    option_labels=(
                        "Boiled Egg",
                        "Pork Crackling",
                        "Century Egg",
                        "Fish Ball",
                        "Meat Ball",
                    ),
                ),
            ),
        )
    ]

    lines = render_kitchen_ticket_lines(items, line_width=32)

    assert lines[0] == "[A1] Thai Noodle"
    assert lines[1].startswith("  Add-on: ")
    assert len(lines) >= 3
    for line in lines[2:]:
        assert line.startswith("          ")
