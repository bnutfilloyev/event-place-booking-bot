from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from keyboards.common_kb import contact_kb
from structures.states import RegState
from structures.database import db
import datetime

register_router = Router()


@register_router.message(RegState.fullname, ~F.text.startswith("/"))
async def input_firstname(message: types.Message, state: FSMContext):
    await state.update_data(input_fullname=message.text)
    text = "📱 <b>Telefon raqamingizni kiriting:</b>\n\n💡 <i>Pastdagi tugmani bosing yoki qo'lda kiriting</i>"
    await message.answer(text=text, reply_markup=contact_kb(), parse_mode="HTML")
    await state.set_state(RegState.phone_number)


@register_router.message(
    RegState.phone_number, ~F.text.startswith("/") | F.text | F.contact
)
async def input_phone(message: types.Message, state: FSMContext):
    """Enter phone number."""
    if message.contact:
        phone = message.contact.phone_number

    if message.text:
        phone = message.text

    await state.update_data(input_phone=phone)
    data = await state.get_data()
    await db.user_update(user_id=message.from_user.id, data=data)
    text = "🎉 <b>Ajoyib!</b> Ro'yxatdan o'tish muvaffaqiyatli yakunlandi!\n\n✨ <i>Siz bilan tez orada yana ko'rishamiz</i> 👋"
    await message.answer(text=text, parse_mode="HTML")
    return await state.clear()


@register_router.message(RegState.guest_fullname, ~F.text.startswith("/"))
async def input_guest_firstname(message: types.Message, state: FSMContext):
    """Input guest's full name."""
    await state.update_data(guest_fullname=message.text)
    text = ("📞 <b>Mehmon telefon raqamini kiriting:</b>\n\n"
            "📋 <i>Namuna:</i> <code>+998901234567</code>\n\n"
            "💡 <i>Telefon raqamini to'g'ri formatda kiriting</i>")

    await message.answer(text=text, parse_mode="HTML")
    await state.set_state(RegState.guest_phone_number)

@register_router.message(
    RegState.guest_phone_number, ~F.text.startswith("/") | F.text | F.contact
)
async def input_guest_phone(message: types.Message, state: FSMContext):
    """Input guest's phone number."""
    if message.contact:
        phone = message.contact.phone_number

    if message.text:
        phone = message.text

    await state.update_data(guest_phone=phone)
    
    text = "🎫 <b>Mehmon uchun beyjik raqamini kiriting:</b>\n\n📝 <i>Raqamni aniq va to'g'ri kiriting</i>"
    await message.answer(text=text, parse_mode="HTML")
    await state.set_state(RegState.guest_badge_number)


@register_router.message(
    RegState.guest_badge_number, ~F.text.startswith("/") | F.text
)
async def input_guest_badge(message: types.Message, state: FSMContext):
    """Input guest's badge number."""
    badge_number = message.text
    data = await state.get_data()
    guest_fullname = data.get("guest_fullname")
    guest_phone = data.get("guest_phone")
    registered_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    guest_data = {
        "badge_name": guest_fullname,
        "input_phone": guest_phone,
        "badge_tariff": "guest",
        "registered_by": message.from_user.id,
        "registered_at": registered_time,
    }
    await db.guest_update(badge_number=badge_number, data=guest_data)

    text = (
        "🎉 <b>Ajoyib!</b> Mehmoningiz muvaffaqiyatli ro'yxatga olindi!\n\n"
        "✅ <i>Barcha ma'lumotlar saqlandi:</i>\n"
        f"👤 F.I.O: <b>{guest_fullname}</b>\n"
        f"📞 Telefon: <b>{guest_phone}</b>\n"
        f"💳 Beyjik raqami: <b>{badge_number}</b>\n"
        f"🎫 Tarif: <b>Mehmon</b>"
    )
    await message.answer(text=text, parse_mode="HTML")
    return await state.clear()
