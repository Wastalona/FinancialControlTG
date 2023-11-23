from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder

menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="As needed"),
            KeyboardButton(text="Optional"),
            KeyboardButton(text="Storage")
        ],
        [
            KeyboardButton(text="Transaction"),
            KeyboardButton(text="Transfers"),
            KeyboardButton(text="Debts")
        ],
        [
            KeyboardButton(text="Info"),
            KeyboardButton(text="Statistics"),
            KeyboardButton(text="New transaction"),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Choose action",
)

work = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="+ Card"),
            KeyboardButton(text="+ Cash"),
            KeyboardButton(text="+ Debt")
        ],
        [
            KeyboardButton(text="- Card"),
            KeyboardButton(text="- Cash"),
            KeyboardButton(text="- Debt")
        ],
        [
            KeyboardButton(text="Transfer"),
            KeyboardButton(text="Menu"),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Choose action",
)


def expenses_categories():
    items = ("Food", "Home", "Phone", "Banking",
             "Internet", "Bills", "Rent", "Gift",
             "Closing", "Health", "Shopping",
             "Education", "Transport", "ForYourself",
             "Back")

    builder = ReplyKeyboardBuilder()
    [builder.button(text=item) for item in items]
    builder.adjust(4, 4, 3, 3, 1)

    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def income_categories():
    items = ("Salary", "Parttime", "Parents",
             "Competition", "Investments", "Freelancing",
             "Rent", "Gift", "Back")

    builder = ReplyKeyboardBuilder()
    [builder.button(text=item) for item in items]
    builder.adjust(*[3] * 3)

    return builder.as_markup(resize_keyboard=True)


specific_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Edit transaction"),
            InlineKeyboardButton(text="Remove transaction"),
        ],
        [
            InlineKeyboardButton(text="Prev month"),
            InlineKeyboardButton(text="Current month"),
        ]
    ]
)
