from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart,Command
from aiogram import F
from aiogram.types import Message,CallbackQuery
from data import config
import asyncio
import logging
import sys
from menucommands.set_bot_commands  import set_default_commands
from baza.sqlite import Database
from filters.admin import IsBotAdminFilter
from filters.check_sub_channel import IsCheckSubChannels
from keyboard_buttons import admin_keyboard,calculator_button
from aiogram.fsm.context import FSMContext
from middlewares.throttling import ThrottlingMiddleware #new
from states.reklama import Adverts
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import time 
from aiogram.types import CallbackQuery

#sozlash
ADMINS = config.ADMINS
TOKEN = config.BOT_TOKEN
CHANNELS = config.CHANNELS

dp = Dispatcher()



#start komandasi uchun javob
@dp.message(CommandStart())
async def start_command(message:Message):
    full_name = message.from_user.full_name
    telegram_id = message.from_user.id
    try:
        db.add_user(full_name=full_name,telegram_id=telegram_id)
        await message.answer(text=f"salom")
    except:
        await message.answer(text=f"salom {full_name} /calc deb yozing")






#calculator
@dp.message(Command("calc"))
async def open_calc_answer(message: Message):
    await message.answer("|", reply_markup=calculator_button.calculator_builder)



#calculator tugmalariga javob yaratish
@dp.callback_query()
async def callback_answer(callback: CallbackQuery):

    if callback.message.text == "|":
        if callback.data in "DC": await callback.answer(f"❗ O'chirish uchun ifoda mavjud emas!", show_alert=True)
        elif callback.data in "+-*/=,":
            await callback.answer(f"❗ Siz ifodani {callback.data} belgisi bilan boshlay olmaysiz", show_alert=True)
        else:
            await callback.message.edit_text(callback.data + callback.message.text)

            await callback.message.edit_reply_markup(
                reply_markup=calculator_button.calculator_builder
            )
    else:
        if callback.data == "D":
            await callback.message.edit_text(callback.message.text[:-2] + "|", reply_markup=calculator_button.calculator_builder)
        elif callback.data == "C":
            await callback.message.edit_text("|", reply_markup=calculator_button.calculator_builder)

        elif (callback.message.text[-2].isdigit()) and callback.data == "=" and ("+" in callback.message.text or "-" in callback.message.text or "*" in callback.message.text or "/" in callback.message.text):
            ifoda = callback.message.text.replace(",", ".")

            await callback.message.edit_text(
                str(eval(ifoda[:-1])) + "|"
            )
            await callback.message.edit_reply_markup(
                reply_markup=calculator_button.calculator_builder
            )
        elif callback.data == "=":
            await callback.answer("❗ Ifoda to'liq emas!", show_alert=True)

        elif callback.message.text[-2].isdigit() or callback.data.isdigit():
            await callback.message.edit_text(
                callback.message.text[:-1] + callback.data + callback.message.text[-1],
            )
            await callback.message.edit_reply_markup(
                reply_markup=calculator_button.calculator_builder
            )
        elif callback.data in "+-*/":
            await callback.message.edit_text(
                callback.message.text[:-2] + callback.data + "|",
                reply_markup=calculator_button.calculator_builder
            )
        elif callback.data == ",":
            await callback.answer("❗Noto'g'ri buyruq!", show_alert=True)















#kanalga obuna bo'lishni tekshirish uchun
@dp.message(IsCheckSubChannels())
async def kanalga_obuna(message:Message):
    text = ""
    inline_channel = InlineKeyboardBuilder()
    for index,channel in enumerate(CHANNELS):
        ChatInviteLink = await bot.create_chat_invite_link(channel)
        inline_channel.add(InlineKeyboardButton(text=f"{index+1}-kanal",url=ChatInviteLink.invite_link))
    inline_channel.adjust(1,repeat=True)
    button = inline_channel.as_markup()
    await message.answer(f"{text} kanallarga azo bo'ling",reply_markup=button)





#Admin komandalari uchun
@dp.message(Command("admin"),IsBotAdminFilter(ADMINS))
async def is_admin(message:Message):
    await message.answer(text="Admin menu",reply_markup=admin_keyboard.admin_button)

@dp.message(Command("about"))
async def is_admin(message:Message):
    await message.answer(text="bu bot sifat uquv markazi \nuquvchilari tomonidan yaratilagan \n bu bot sizning qiyin misollaringizni\n yechishingizga yordam beradi beradi")

@dp.message(F.text=="Foydalanuvchilar soni",IsBotAdminFilter(ADMINS))
async def users_count(message:Message):
    counts = db.count_users()
    text = f"Botimizda {counts[0]} ta foydalanuvchi bor"
    await message.answer(text=text)

@dp.message(F.text=="Reklama yuborish",IsBotAdminFilter(ADMINS))
async def advert_dp(message:Message,state:FSMContext):
    await state.set_state(Adverts.adverts)
    await message.answer(text="Reklama yuborishingiz mumkin !")

@dp.message(Adverts.adverts)
async def send_advert(message:Message,state:FSMContext):
    
    message_id = message.message_id
    from_chat_id = message.from_user.id
    users = db.all_users_id()
    count = 0
    for user in users:
        try:
            await bot.copy_message(chat_id=user[0],from_chat_id=from_chat_id,message_id=message_id)
            count += 1
        except:
            pass
        time.sleep(0.5)
    
    await message.answer(f"Reklama {count}ta foydalanuvchiga yuborildi")
    await state.clear()



#bot ishga tushganini xabarini yuborish
@dp.startup()
async def on_startup_notify(bot: Bot):
    for admin in ADMINS:
        try:
            await bot.send_message(chat_id=int(admin),text="Bot ishga tushdi")
        except Exception as err:
            logging.exception(err)


#bot ishni yakunlaganining xabarini yuborish
@dp.shutdown()
async def off_startup_notify(bot: Bot):
    for admin in ADMINS:
        try:
            await bot.send_message(chat_id=int(admin),text="Bot ishdan to'xtadi!")
        except Exception as err:
            logging.exception(err)




#nimadur xabar yozsa "/calc" komandasidan foydalaning deb chiqarishi kerak
@dp.message()
async def xabar(message: Message):
    full_name = message.from_user.full_name
    await message.answer(f"xurmatli {full_name} agar botimizdan foydalanmoqchi bo`lsangiz /calc kommandasidan foydalaning")



async def main() -> None:

    global bot,db
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    
    #malumotlar bazasini yaratish
    db = Database(path_to_db="users.db")

    #flood ni oldini olish
    dp.message.middleware(ThrottlingMiddleware(slow_mode_delay=0.5))

    #foydalanuvchilar jadvalini yaratish
    db.create_table_users()

    #birlamchi komandalar
    await set_default_commands(bot)

    #botni ishga tushirish
    await dp.start_polling(bot)
    




if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    asyncio.run(main())