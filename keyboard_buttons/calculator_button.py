from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

# 7 8 9 +
# 4 5 6 -
# 1 2 3 *
# , 0 / =

calculator_builder = InlineKeyboardBuilder()
for i in "789+456-123*,0/=DC":
    calculator_builder.add(InlineKeyboardButton(text=i, callback_data=i))
calculator_builder.adjust(4, repeat=True)
calculator_builder = calculator_builder.as_markup()

 
