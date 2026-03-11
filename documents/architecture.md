# Архитектура сервиса платежей

## Слои приложения

```mermaid
graph TD
    API[API Router] --> Services[Services]
    Services --> UoW[Unit of Work]
    UoW --> Repos[Repositories]
    Repos --> Models[SQLAlchemy Models]
    Services --> BankClient[Bank Client]
    BankClient --> BankAPI[Bank API]
```

## Депозит — создание платежа

```mermaid
flowchart TD
    A[POST /payments/deposit] --> B{Заказ существует?}
    B -- Нет --> C[404 Not Found]
    B -- Да --> D{Сумма платежей + новый <= сумма заказа?}
    D -- Нет --> E[400 Сумма превышена]
    D -- Да --> F{Тип платежа}
    F -- cash --> G[Создать платёж, status=completed]
    G --> H[Пересчитать payment_status заказа]
    F -- acquiring --> I[BankClient.acquiring_start]
    I -- Ошибка --> J[502 Ошибка банка]
    I -- Успех --> K[Создать платёж, status=pending]
    K --> H
    H --> L[Вернуть платёж]
```

## Возврат платежа

```mermaid
flowchart TD
    A[POST /payments/refund] --> B{Платёж существует?}
    B -- Нет --> C[404 Not Found]
    B -- Да --> D{Статус = completed?}
    D -- Нет --> E[400 Возврат невозможен]
    D -- Да --> F[Статус = refunded]
    F --> G[Пересчитать payment_status заказа]
    G --> H[Вернуть платёж]
```

## Синхронизация с банком

```mermaid
flowchart TD
    A[POST /payments/sync] --> B{Платёж существует?}
    B -- Нет --> C[404 Not Found]
    B -- Да --> D{Есть bank_payment_id?}
    D -- Нет --> E[400 Не банковский платёж]
    D -- Да --> F[BankClient.acquiring_check]
    F -- Ошибка --> G[502 Ошибка банка]
    F -- Успех --> H[Обновить status, paid_at]
    H --> I[Пересчитать payment_status заказа]
    I --> J[Вернуть платёж]
```

## Статусы

### Статус оплаты заказа (PaymentStatus)

| Значение | Описание |
| --- | --- |
| `not_paid` | Не оплачен — нет завершённых платежей |
| `partially_paid` | Частично оплачен — сумма платежей меньше суммы заказа |
| `paid` | Оплачен — сумма платежей равна сумме заказа |

### Тип платежа (PaymentType)

| Значение | Описание |
| --- | --- |
| `cash` | Наличные — платёж завершается сразу |
| `acquiring` | Эквайринг — платёж через банк, требует подтверждения |

### Статус платежа (TransactionStatus)

| Значение | Описание |
| --- | --- |
| `pending` | Ожидает подтверждения от банка |
| `completed` | Завершён — деньги получены |
| `refunded` | Возвращён |
| `failed` | Ошибка — платёж не прошёл |

## Пересчёт статуса заказа

```mermaid
flowchart TD
    A[Сумма completed-платежей] --> B{= 0?}
    B -- Да --> C[not_paid]
    B -- Нет --> D{= сумма заказа?}
    D -- Да --> E[paid]
    D -- Нет --> F[partially_paid]
```
