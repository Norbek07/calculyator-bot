from aiogram import Bot
from aiogram.methods.set_my_commands import BotCommand
from aiogram.types import BotCommandScopeAllPrivateChats


async def set_default_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Botni ishga tushirish"),
        BotCommand(command="/help", description="calculyatorni menusini chiqarish uchun /calc ni yozing"),
        BotCommand(command="/about", description="bu bot sifat uquv markazi \nuquvchilari tomonidan yaratilagan \n bu bot sizning qiyin misollaringizni\n yechishingizga yordam beradi beradi"),

    ]
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeAllPrivateChats())