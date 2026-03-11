# Схема базы данных

## ER-диаграмма

```mermaid
erDiagram
    orders {
        uuid id PK
        decimal(12_2) amount "NOT NULL"
        varchar(20) payment_status "NOT NULL, default 'not_paid'"
        timestamp created_at "NOT NULL"
        timestamp updated_at "NOT NULL"
    }

    payments {
        uuid id PK
        uuid order_id FK "NOT NULL, ON DELETE RESTRICT"
        varchar(20) type "NOT NULL (cash / acquiring)"
        varchar(20) status "NOT NULL (pending / completed / refunded / failed)"
        decimal(12_2) amount "NOT NULL"
        varchar(255) bank_payment_id "NULL"
        timestamp paid_at "NULL"
        timestamp created_at "NOT NULL"
        timestamp updated_at "NOT NULL"
    }

    orders ||--o{ payments : "has"
```

## Таблица orders

Заказы предзаполнены через seed-миграцию. CRUD не предусмотрен — сервис работает только с платежами.

| Поле | Тип | Описание |
| --- | --- | --- |
| `id` | `uuid` PK | Идентификатор заказа |
| `amount` | `decimal(12,2)` | Сумма заказа |
| `payment_status` | `varchar(20)` | Статус оплаты: `not_paid`, `partially_paid`, `paid` |
| `created_at` | `timestamp` | Дата создания |
| `updated_at` | `timestamp` | Дата обновления |

## Таблица payments

| Поле | Тип | Описание |
| --- | --- | --- |
| `id` | `uuid` PK | Идентификатор платежа |
| `order_id` | `uuid` FK → `orders.id` | Заказ, к которому привязан платёж |
| `type` | `varchar(20)` | Тип: `cash`, `acquiring` |
| `status` | `varchar(20)` | Статус: `pending`, `completed`, `refunded`, `failed` |
| `amount` | `decimal(12,2)` | Сумма платежа |
| `bank_payment_id` | `varchar(255)` NULL | ID платежа в банке (только для acquiring) |
| `paid_at` | `timestamp` NULL | Дата оплаты |
| `created_at` | `timestamp` | Дата создания |
| `updated_at` | `timestamp` | Дата обновления |

## Связи

- `payments.order_id` → `orders.id` с `ON DELETE RESTRICT` — удаление заказа при наличии платежей запрещено
- Один заказ может иметь множество платежей (1:N)
