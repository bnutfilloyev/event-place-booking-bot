from aiogram import Router, types
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from keyboards.common_kb import contact_kb, remove_kb
from structures.database import db
from structures.states import RegState, BroadcastState
from datetime import datetime

start_router = Router()

      
@start_router.message(CommandStart(deep_link=True, deep_link_encoded=True))
async def start_command(
    message: types.Message, state: FSMContext, command: CommandObject
):
    """Start command with deep link support."""
    args = command.args.strip()
    tariff, badge_number = args.split(":")

    if not tariff or not badge_number:
        text = (
            "🚫 <b>Noto‘g‘ri havola!</b>\n\n"
            "Siz yuborgan havola noto‘g‘ri yoki eskirgan.\n\n"
            "🧐 <b>Iltimos tekshirib ko‘ring:</b>\n"
            "– Havola to‘g‘ri yozilganmi?\n"
            "– Havola eskirmaganmi?\n\n"
            "ℹ️ <b>Yordam kerak bo‘lsa:</b> @AvazMarketer"
        )
        await message.answer(text=text, reply_markup=remove_kb())
        return await state.clear()


    user_info = await db.get_user_by_badge(badge_number, tariff)

    if user_info is None:
        text = (
            "❌ <b>Ma'lumot bazasi bo‘yicha topilmadi.</b>\n\n"
            "Siz hali ro‘yxatdan o‘tmagansiz yoki chipta raqamingiz noto‘g‘ri.\n\n"
            "🧐 <b>Iltimos, quyidagi ma'lumotlarni tekshirib ko‘ring:</b>\n"
            "– Chipta raqami to‘g‘ri kiritilganmi?\n"
            "– Ro‘yxatdan o‘tganmisiz?\n\n"
            "💡 <b>Agar muammo davom etsa, iltimos, administrator bilan bog‘laning:</b> @AvazMarketer"
        )
        await message.answer(text=text, reply_markup=remove_kb())
        return await state.clear()

    badge_number = user_info.get("badge_number")
    badge_fullname = user_info.get("badge_name")
    phone_number = user_info.get("input_phone", "Noma'lum")

    # Update scan times
    scan_times = user_info.get("scan_times", [])
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    scan_times.append(current_time)
    await db.user_update(user_id=message.from_user.id, data={"scan_times": scan_times})

    first_scan = scan_times[0]
    last_scan = scan_times[-1]

    text = (
        "✅ <b>Tizim sizni aniqladi!</b>\n\n"
        "🎉 <b>Mehmon ma'lumotlari:</b>\n"
        f"👤 F.I.O: <b>{badge_fullname}</b>\n"
        f"💳 Chipta raqami: <b>{badge_number}</b>\n"
        f"🎫 Tarif: <b>{tariff}</b>\n"
        f"📞 Telefon: <b>{phone_number}</b>\n\n"
        "🎊 <b>Sizga tadbirimiz eshiklari ochiq!</b>\n"
        "📲 <b>Iltimos, ushbu QR-kodni nazorat punktida ko‘rsating.</b>\n\n"
        "💡 <b>Tavsiyalar:</b>\n"
        "– QR-kodni rasm ko‘rinishida saqlang\n"
        "– Faqat <b>6-7 iyul kunlari</b> foydalanish mumkin\n\n"
        f"🕒 <b>Tekshirish vaqtlari:</b>\n"
        f"– Birinchi tekshirish: <b>{first_scan}</b>\n"
        f"– Oxirgi tekshirish: <b>{last_scan}</b>"
    )
    await message.answer(text=text)
    return await state.clear()


@start_router.message(CommandStart())
async def start_command_no_deep_link(message: types.Message, state: FSMContext):
    """Start command without deep link."""
    user_data = {
        "username": message.from_user.username,
        "fullname": message.from_user.full_name,
    }

    user_info = await db.user_update(user_id=message.from_user.id, data=user_data)

    if user_info.get("input_fullname") is None:
        text = (
            "🌟 <b>Assalomu alaykum!</b>\n\n"
            "Siz hali ro‘yxatdan o‘tmagansiz.\n"
            "✍️ <b>To‘liq ismingizni kiriting:</b>"
        )
        await message.answer(text=text, reply_markup=remove_kb())
        return await state.set_state(RegState.fullname)

    if user_info.get("input_phone") is None:
        text = (
            "📱 <b>Telefon raqam kerak!</b>\n\n"
            "⚡️ <b>Quyidagi tugma orqali raqamingizni yuboring:</b>"
        )
        await message.answer(text=text, reply_markup=contact_kb())
        return await state.set_state(RegState.phone_number)

    text = (
        "👋 <b>Yana siz bilan ko‘rishib turganimizdan xursandmiz!</b>\n\n"
        "🎉 <b>Siz allaqon ro‘yxatdan o‘tgansiz!</b>"
    )
    await message.answer(text=text)


@start_router.message(Command("help"))
async def help_command(message: types.Message, state: FSMContext):
    """Help command."""
    text = (
        "🆘 <b>Yordam markazi</b>\n\n"
        "🎯 <b>Bizning bot orqali siz:</b>\n"
        "📍 Premium tadbir joylarini bron qilishingiz\n"
        "🎊 Maxsus takliflardan foydalanishingiz\n"
        "📞 Onlayn qo'llab-quvvatlash olishingiz mumkin\n\n"
        "❓ <b>Qo'shimcha yordam kerakmi?</b>\n"
        "👨‍💼 <b>Administrator bilan bog'laning!</b>"
    )
    await message.answer(text=text)
    return await state.clear()


@start_router.message(Command("broadcast"))
async def broadcast_command(message: types.Message, state: FSMContext):
    text = (
        "📢 <b>Ommaviy xabar yuborish</b>\n\n"
        "✨ <b>Barcha foydalanuvchilarga yubormoqchi bo'lgan</b>\n"
        "📝 <b>Maxsus xabaringizni yozing:</b>\n\n"
        "💡 <b>Eslatma:</b> Xabar barcha botdan foydalanuvchilarga yetkaziladi"
    )
    await message.answer(text=text)
    return await state.set_state(BroadcastState.broadcast)


@start_router.message(Command("guest"))
async def guest_command(message: types.Message, state: FSMContext):
    text = (
        "👥 <b>Mehmon qo'shish</b>\n\n"
        "📋 <b>Iltimos, mehmon ma'lumotlarini kiriting:</b>\n"
        "– F.I.O\n\n"
        "💡 <b>Eslatma:</b> Mehmon ma'lumotlari bot orqali saqlanadi va tadbirga kirishda ishlatiladi."
    )
    await message.answer(text=text, reply_markup=remove_kb())
    return await state.set_state(RegState.guest_fullname)

