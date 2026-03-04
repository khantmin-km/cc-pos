# Database Schema (Phase 1)

## physical_tables
```
CREATE TABLE physical_tables (
    id              UUID PRIMARY KEY,
    table_code      VARCHAR(50) NOT NULL UNIQUE,
    created_at      TIMESTAMP NOT NULL DEFAULT now()
);
```

## table_groups
```
CREATE TABLE table_groups (
    id              UUID PRIMARY KEY,
    state           VARCHAR(20) NOT NULL,
    opened_at       TIMESTAMP NOT NULL DEFAULT now(),
    closed_at       TIMESTAMP NULL,

    CONSTRAINT table_group_state_check
        CHECK (state IN ('OPEN', 'BILL_REQUESTED', 'PAID', 'CLOSED'))
);
```

## table_group_tables (junction)
```
CREATE TABLE table_group_tables (
    table_group_id    UUID NOT NULL,
    physical_table_id UUID NOT NULL,

    PRIMARY KEY (table_group_id, physical_table_id),

    CONSTRAINT fk_tgt_table_group
        FOREIGN KEY (table_group_id)
        REFERENCES table_groups(id),

    CONSTRAINT fk_tgt_physical_table
        FOREIGN KEY (physical_table_id)
        REFERENCES physical_tables(id)
);
```

## orders
```
CREATE TABLE orders (
    id              UUID PRIMARY KEY,
    table_group_id  UUID NOT NULL,
    state           VARCHAR(20) NOT NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT now(),

    CONSTRAINT fk_orders_table_group
        FOREIGN KEY (table_group_id)
        REFERENCES table_groups(id),

    CONSTRAINT order_state_check
        CHECK (state IN ('CONFIRMED'))
);
```

## order_items
```
CREATE TABLE order_items (
    id                  UUID PRIMARY KEY,
    order_id            UUID NOT NULL,
    physical_table_id   UUID NOT NULL,
    menu_item_id        UUID NULL,
    menu_item_name_snap VARCHAR(200) NOT NULL,
    unit_price_snap     DECIMAL(10,2) NOT NULL,
    status              VARCHAR(20) NOT NULL,
    created_at          TIMESTAMP NOT NULL DEFAULT now(),
    voided_at           TIMESTAMP NULL,

    CONSTRAINT fk_order_items_order
        FOREIGN KEY (order_id)
        REFERENCES orders(id),

    CONSTRAINT fk_order_items_physical_table
        FOREIGN KEY (physical_table_id)
        REFERENCES physical_tables(id),

    CONSTRAINT order_item_state_check
        CHECK (status IN ('ACTIVE', 'VOIDED'))
);
```

## order_item_serving
```
CREATE TABLE order_item_serving (
    order_item_id  UUID PRIMARY KEY,
    served_at      TIMESTAMP NOT NULL,

    CONSTRAINT fk_serving_order_item
        FOREIGN KEY (order_item_id)
        REFERENCES order_items(id)
);
```

## order_item_printing
```
CREATE TABLE order_item_printing (
    order_item_id  UUID NOT NULL,
    printed_at     TIMESTAMP NOT NULL,
    printed_by     VARCHAR(50) NOT NULL,
    print_type     VARCHAR(20) NOT NULL,

    PRIMARY KEY (order_item_id, printed_at),

    CONSTRAINT fk_printing_order_item
        FOREIGN KEY (order_item_id)
        REFERENCES order_items(id)
,
    CONSTRAINT order_item_print_type_check
        CHECK (print_type IN ('ORIGINAL', 'DUPLICATE'))
);
```

## bill_print_events
```
CREATE TABLE bill_print_events (
    table_group_id  UUID NOT NULL,
    printed_at      TIMESTAMP NOT NULL,
    printed_by      VARCHAR(50) NOT NULL,

    PRIMARY KEY (table_group_id, printed_at),

    CONSTRAINT fk_bill_print_table_group
        FOREIGN KEY (table_group_id)
        REFERENCES table_groups(id)
);
```

## bill_adjustments
```
CREATE TABLE bill_adjustments (
    id                   UUID PRIMARY KEY,
    table_group_id       UUID NOT NULL,
    amount               DECIMAL(10,2) NOT NULL,
    description          TEXT NOT NULL,
    reference_order_item_id UUID NULL,
    reason               TEXT NULL,
    category             VARCHAR(20) NULL,
    created_by           VARCHAR(50) NOT NULL,
    created_at           TIMESTAMP NOT NULL DEFAULT now(),

    CONSTRAINT fk_bill_adj_table_group
        FOREIGN KEY (table_group_id)
        REFERENCES table_groups(id),

    CONSTRAINT fk_bill_adj_order_item
        FOREIGN KEY (reference_order_item_id)
        REFERENCES order_items(id),

    CONSTRAINT bill_adj_category_check
        CHECK (category IN ('WAIVER', 'MANUAL'))
);
```
