import asyncio
import requests
import random
import os
import html
import re
from telegram import (
    Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)

# --- CONFIG ---
API1_URL   = "http://147.135.212.197/crapi/st/viewstats"
API1_TOKEN = os.environ["API1_TOKEN"]
API2_URL   = "http://147.135.212.197/crapi/st/viewstats"
API2_TOKEN = os.environ["API2_TOKEN"]
API3_URL   = "https://pscall.net/restapi/smsreport"
API3_KEY   = os.environ["API3_KEY"]
BOT_TOKEN  = os.environ["BOT_TOKEN"]
TARGET_CHAT = os.environ["TARGET_CHAT"]
GROUP_LINK  = os.environ.get("GROUP_LINK", "https://t.me/")

# --- STATE ---
sms_cache = []       # list of dicts: {service, number, message, date, country}
seen_ids  = set()
MAX_CACHE = 200

# --- COUNTRY DATABASE ---
country_db = {
    "1":"🇺🇸 USA/Canada","93":"🇦🇫 Afghanistan","355":"🇦🇱 Albania","213":"🇩🇿 Algeria",
    "376":"🇦🇩 Andorra","244":"🇦🇴 Angola","1264":"🇦🇮 Anguilla","1268":"🇦🇬 Antigua",
    "54":"🇦🇷 Argentina","374":"🇦🇲 Armenia","61":"🇦🇺 Australia","43":"🇦🇹 Austria",
    "994":"🇦🇿 Azerbaijan","1242":"🇧🇸 Bahamas","973":"🇧🇭 Bahrain","880":"🇧🇩 Bangladesh",
    "1246":"🇧🇧 Barbados","375":"🇧🇾 Belarus","32":"🇧🇪 Belgium","501":"🇧🇿 Belize",
    "229":"🇧🇯 Benin","1441":"🇧🇲 Bermuda","975":"🇧🇹 Bhutan","591":"🇧🇴 Bolivia",
    "387":"🇧🇦 Bosnia","267":"🇧🇼 Botswana","55":"🇧🇷 Brazil","673":"🇧🇳 Brunei",
    "359":"🇧🇬 Bulgaria","226":"🇧🇫 Burkina Faso","257":"🇧🇮 Burundi","855":"🇰🇭 Cambodia",
    "237":"🇨🇲 Cameroon","238":"🇨🇻 Cape Verde","1345":"🇰🇾 Cayman Islands",
    "236":"🇨🇫 Central African Republic","235":"🇹🇩 Chad","56":"🇨🇱 Chile","86":"🇨🇳 China",
    "57":"🇨🇴 Colombia","269":"🇰🇲 Comoros","242":"🇨🇬 Republic of Congo",
    "243":"🇨🇩 DR Congo","506":"🇨🇷 Costa Rica","385":"🇭🇷 Croatia","53":"🇨🇺 Cuba",
    "357":"🇨🇾 Cyprus","420":"🇨🇿 Czech Republic","45":"🇩🇰 Denmark","253":"🇩🇯 Djibouti",
    "1767":"🇩🇲 Dominica","1809":"🇩🇴 Dominican Republic","593":"🇪🇨 Ecuador",
    "20":"🇪🇬 Egypt","503":"🇸🇻 El Salvador","240":"🇬🇶 Equatorial Guinea",
    "291":"🇪🇷 Eritrea","372":"🇪🇪 Estonia","251":"🇪🇹 Ethiopia","679":"🇫🇯 Fiji",
    "358":"🇫🇮 Finland","33":"🇫🇷 France","689":"🇵🇫 French Polynesia","241":"🇬🇦 Gabon",
    "220":"🇬🇲 Gambia","995":"🇬🇪 Georgia","49":"🇩🇪 Germany","233":"🇬🇭 Ghana",
    "350":"🇬🇮 Gibraltar","30":"🇬🇷 Greece","1473":"🇬🇩 Grenada","502":"🇬🇹 Guatemala",
    "224":"🇬🇳 Guinea","245":"🇬🇼 Guinea-Bissau","592":"🇬🇾 Guyana","509":"🇭🇹 Haiti",
    "504":"🇭🇳 Honduras","852":"🇭🇰 Hong Kong","36":"🇭🇺 Hungary","354":"🇮🇸 Iceland",
    "91":"🇮🇳 India","62":"🇮🇩 Indonesia","98":"🇮🇷 Iran","964":"🇮🇶 Iraq",
    "353":"🇮🇪 Ireland","972":"🇮🇱 Israel","39":"🇮🇹 Italy","1876":"🇯🇲 Jamaica",
    "81":"🇯🇵 Japan","962":"🇯🇴 Jordan","254":"🇰🇪 Kenya","686":"🇰🇮 Kiribati",
    "965":"🇰🇼 Kuwait","996":"🇰🇬 Kyrgyzstan","856":"🇱🇦 Laos","371":"🇱🇻 Latvia",
    "961":"🇱🇧 Lebanon","266":"🇱🇸 Lesotho","231":"🇱🇷 Liberia","218":"🇱🇾 Libya",
    "370":"🇱🇹 Lithuania","352":"🇱🇺 Luxembourg","853":"🇲🇴 Macau","389":"🇲🇰 Macedonia",
    "261":"🇲🇬 Madagascar","265":"🇲🇼 Malawi","60":"🇲🇾 Malaysia","960":"🇲🇻 Maldives",
    "223":"🇲🇱 Mali","356":"🇲🇹 Malta","692":"🇲🇭 Marshall Islands","222":"🇲🇷 Mauritania",
    "230":"🇲🇺 Mauritius","52":"🇲🇽 Mexico","691":"🇫🇲 Micronesia","373":"🇲🇩 Moldova",
    "377":"🇲🇨 Monaco","976":"🇲🇳 Mongolia","382":"🇲🇪 Montenegro","1664":"🇲🇸 Montserrat",
    "212":"🇲🇦 Morocco","258":"🇲🇿 Mozambique","95":"🇲🇲 Myanmar","264":"🇳🇦 Namibia",
    "674":"🇳🇷 Nauru","977":"🇳🇵 Nepal","31":"🇳🇱 Netherlands","64":"🇳🇿 New Zealand",
    "505":"🇳🇮 Nicaragua","227":"🇳🇪 Niger","234":"🇳🇬 Nigeria","850":"🇰🇵 North Korea",
    "47":"🇳🇴 Norway","968":"🇴🇲 Oman","92":"🇵🇰 Pakistan","680":"🇵🇼 Palau",
    "970":"🇵🇸 Palestine","507":"🇵🇦 Panama","675":"🇵🇬 Papua New Guinea",
    "595":"🇵🇾 Paraguay","51":"🇵🇪 Peru","63":"🇵🇭 Philippines","48":"🇵🇱 Poland",
    "351":"🇵🇹 Portugal","1787":"🇵🇷 Puerto Rico","974":"🇶🇦 Qatar","40":"🇷🇴 Romania",
    "7":"🇷🇺 Russia/Kazakhstan","250":"🇷🇼 Rwanda","685":"🇼🇸 Samoa",
    "239":"🇸🇹 Sao Tome","966":"🇸🇦 Saudi Arabia","221":"🇸🇳 Senegal","381":"🇷🇸 Serbia",
    "248":"🇸🇨 Seychelles","232":"🇸🇱 Sierra Leone","65":"🇸🇬 Singapore",
    "421":"🇸🇰 Slovakia","386":"🇸🇮 Slovenia","677":"🇸🇧 Solomon Islands",
    "252":"🇸🇴 Somalia","27":"🇿🇦 South Africa","82":"🇰🇷 South Korea",
    "211":"🇸🇸 South Sudan","34":"🇪🇸 Spain","94":"🇱🇰 Sri Lanka","249":"🇸🇩 Sudan",
    "597":"🇸🇷 Suriname","268":"🇸🇿 Swaziland","46":"🇸🇪 Sweden","41":"🇨🇭 Switzerland",
    "963":"🇸🇾 Syria","886":"🇹🇼 Taiwan","992":"🇹🇯 Tajikistan","255":"🇹🇿 Tanzania",
    "66":"🇹🇭 Thailand","670":"🇹🇱 Timor-Leste","228":"🇹🇬 Togo","676":"🇹🇴 Tonga",
    "1868":"🇹🇹 Trinidad & Tobago","216":"🇹🇳 Tunisia","90":"🇹🇷 Turkey",
    "993":"🇹🇲 Turkmenistan","1649":"🇹🇨 Turks & Caicos","688":"🇹🇻 Tuvalu",
    "256":"🇺🇬 Uganda","380":"🇺🇦 Ukraine","971":"🇦🇪 UAE","44":"🇬🇧 UK",
    "598":"🇺🇾 Uruguay","998":"🇺🇿 Uzbekistan","678":"🇻🇺 Vanuatu",
    "58":"🇻🇪 Venezuela","84":"🇻🇳 Vietnam","1284":"🇻🇬 British Virgin Islands",
    "1340":"🇻🇮 US Virgin Islands","967":"🇾🇪 Yemen","260":"🇿🇲 Zambia","263":"🇿🇼 Zimbabwe",
    "700":"🇰🇿 Kazakhstan","701":"🇰🇿 Kazakhstan","702":"🇰🇿 Kazakhstan",
    "703":"🇰🇿 Kazakhstan","704":"🇰🇿 Kazakhstan","705":"🇰🇿 Kazakhstan",
    "706":"🇰🇿 Kazakhstan","707":"🇰🇿 Kazakhstan","708":"🇰🇿 Kazakhstan",
    "747":"🇰🇿 Kazakhstan","770":"🇰🇿 Kazakhstan","771":"🇰🇿 Kazakhstan",
    "777":"🇰🇿 Kazakhstan","778":"🇰🇿 Kazakhstan",
    "584":"🇻🇪 Venezuela","582":"🇻🇪 Venezuela","581":"🇻🇪 Venezuela",
}

def get_country(number):
    d = str(number).replace("+", "").replace(" ", "")
    for l in range(4, 0, -1):
        if d[:l] in country_db:
            return country_db[d[:l]]
    return "🌍 Unknown"

def extract_code(msg):
    match = re.search(r'\b\d{3}[-\s]\d{3}\b|\b\d{4,8}\b', str(msg))
    return match.group(0) if match else "N/A"

def mask_number(number):
    clean = str(number).replace("+", "")
    return clean[:6] + "****" + clean[-3:] if len(clean) > 7 else clean

# --- KEYBOARDS ---
def main_menu_kb():
    return ReplyKeyboardMarkup(
        [["📱 Get Number", "📊 Status"],
         ["🔴 Live Traffic", "🔗 Group Link"]],
        resize_keyboard=True
    )

def number_action_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Change Number", callback_data="change_number"),
         InlineKeyboardButton("🌍 Change Country", callback_data="change_country")],
        [InlineKeyboardButton("🔑 Group Link", url=GROUP_LINK),
         InlineKeyboardButton("⬅️ Back to Main", callback_data="back_main")]
    ])

def country_kb(countries):
    buttons = []
    row = []
    for i, c in enumerate(countries):
        row.append(InlineKeyboardButton(c, callback_data=f"country:{c}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("🌍 Any Country", callback_data="country:any")])
    buttons.append([InlineKeyboardButton("⬅️ Back", callback_data="back_main")])
    return InlineKeyboardMarkup(buttons)

# --- HELPERS ---
def get_available_numbers(country_filter=None):
    numbers = {}
    for entry in sms_cache:
        num = entry["number"]
        if not num:
            continue
        country = entry["country"]
        if country_filter and country_filter != "any" and country != country_filter:
            continue
        numbers[num] = country
    return numbers

def get_number_for_user(context: ContextTypes.DEFAULT_TYPE, country_filter=None):
    pool = get_available_numbers(country_filter)
    if not pool:
        pool = get_available_numbers()
    if not pool:
        return None, None
    number = random.choice(list(pool.keys()))
    country = pool[number]
    context.user_data["number"] = number
    context.user_data["country"] = country
    return number, country

def format_number_msg(number, country):
    clean = str(number).replace("+", "")
    return (
        f"{country} | <code>+{clean}</code>\n\n"
        f"📋 Use this number to receive your OTP,\n"
        f"then tap <b>📊 Status</b> to see it."
    )

# --- HANDLERS ---
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 <b>Welcome to OTP Bot!</b>\n\nChoose an option below:",
        parse_mode="HTML",
        reply_markup=main_menu_kb()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📱 Get Number":
        country_filter = context.user_data.get("country_filter")
        number, country = get_number_for_user(context, country_filter)
        if not number:
            await update.message.reply_text(
                "⏳ No numbers in pool yet. Please wait a few seconds and try again."
            )
            return
        await update.message.reply_text(
            format_number_msg(number, country),
            parse_mode="HTML",
            reply_markup=number_action_kb()
        )

    elif text == "📊 Status":
        number = context.user_data.get("number")
        if not number:
            await update.message.reply_text(
                "❌ You don't have a number yet. Tap 📱 Get Number first."
            )
            return
        matches = [e for e in sms_cache if e["number"] == number]
        if not matches:
            country = get_country(number)
            await update.message.reply_text(
                f"⏳ <b>Waiting for OTP...</b>\n\n"
                f"{country} | <code>+{str(number).replace('+','')}</code>\n\n"
                f"No messages received yet. Check back in a moment.",
                parse_mode="HTML",
                reply_markup=number_action_kb()
            )
        else:
            latest = matches[-1]
            code = extract_code(latest["message"])
            await update.message.reply_text(
                f"✅ <b>OTP Found!</b>\n\n"
                f"<b>Number:</b> <code>+{str(number).replace('+','')}</code>\n"
                f"<b>Country:</b> {latest['country']}\n"
                f"<b>Service:</b> <code>{html.escape(str(latest['service']))}</code>\n"
                f"<b>Code:</b> <code>{html.escape(str(code))}</code>\n\n"
                f"<b>Full Message:</b>\n<pre>{html.escape(str(latest['message']))}</pre>",
                parse_mode="HTML",
                reply_markup=number_action_kb()
            )

    elif text == "🔴 Live Traffic":
        if not sms_cache:
            await update.message.reply_text("📭 No traffic yet. Check back soon.")
            return
        recent = sms_cache[-10:][::-1]
        lines = ["🔴 <b>Live Traffic</b> (last 10 OTPs)\n━━━━━━━━━━━━━━━━━━━━━"]
        for e in recent:
            code = extract_code(e["message"])
            masked = mask_number(e["number"])
            lines.append(
                f"\n{e['country']}\n"
                f"📱 <code>{masked}</code>\n"
                f"🔑 <code>{html.escape(str(code))}</code>\n"
                f"🛠 {html.escape(str(e['service']))}\n"
                f"⌚ {html.escape(str(e['date']))}"
            )
        await update.message.reply_text(
            "\n".join(lines),
            parse_mode="HTML"
        )

    elif text == "🔗 Group Link":
        await update.message.reply_text(
            f"📢 Join our group:\n{GROUP_LINK}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 Join Group", url=GROUP_LINK)]
            ])
        )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "change_number":
        country_filter = context.user_data.get("country_filter")
        number, country = get_number_for_user(context, country_filter)
        if not number:
            await query.edit_message_text("⏳ No numbers available right now. Try again.")
            return
        await query.edit_message_text(
            format_number_msg(number, country),
            parse_mode="HTML",
            reply_markup=number_action_kb()
        )

    elif data == "change_country":
        pool = get_available_numbers()
        countries = sorted(set(v for v in pool.values() if v != "🌍 Unknown"))[:20]
        if not countries:
            await query.edit_message_text("⏳ No country data yet. Try again shortly.")
            return
        await query.edit_message_text(
            "🌍 <b>Select a country:</b>",
            parse_mode="HTML",
            reply_markup=country_kb(countries)
        )

    elif data.startswith("country:"):
        chosen = data.split(":", 1)[1]
        context.user_data["country_filter"] = None if chosen == "any" else chosen
        number, country = get_number_for_user(context, context.user_data.get("country_filter"))
        if not number:
            await query.edit_message_text(
                f"❌ No numbers available for {chosen}. Try another country.",
                reply_markup=number_action_kb()
            )
            return
        await query.edit_message_text(
            format_number_msg(number, country),
            parse_mode="HTML",
            reply_markup=number_action_kb()
        )

    elif data == "back_main":
        await query.edit_message_text(
            "👋 <b>Main Menu</b>\n\nChoose an option from the keyboard below.",
            parse_mode="HTML"
        )

# --- API POLLING (background job) ---
def add_to_cache(service, number, message, date):
    global sms_cache
    uid = f"{date}|{number}|{message[:30]}"
    if uid in seen_ids:
        return False
    seen_ids.add(uid)
    country = get_country(number)
    sms_cache.append({
        "service": service,
        "number": str(number),
        "message": str(message),
        "date": str(date),
        "country": country
    })
    if len(sms_cache) > MAX_CACHE:
        sms_cache = sms_cache[-MAX_CACHE:]
    return True

async def forward_to_group(bot: Bot, service, number, message, date):
    country = get_country(number)
    code = extract_code(message)
    clean = str(number).replace("+", "")
    masked = clean[:6] + "****" + clean[-3:] if len(clean) > 7 else clean
    text = (
        f"💐 <b>『 ɴᴇᴡ ᴏᴛᴘ ʀᴇᴄᴇɪᴠᴇᴅ 』</b> ✨\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<b>⌚ ᴛɪᴍᴇ:</b> <code>{html.escape(str(date))}</code>\n"
        f"<b>🌍 ᴄᴏᴜɴᴛʀʏ:</b> {html.escape(str(country))}\n"
        f"<b>📱 ɴᴜᴍʙᴇʀ:</b> <code>{html.escape(str(masked))}</code>\n"
        f"<b>🛠 ꜱᴇʀᴠɪᴄᴇ:</b> <code>{html.escape(str(service))}</code>\n"
        f"<b>🔑 ᴄᴏᴅᴇ:</b> <code>{html.escape(str(code))}</code>\n\n"
        f"<b>💬 ᴍᴇssᴀɢᴇ:</b>\n<pre>{html.escape(str(message))}</pre>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 Channel", url=GROUP_LINK),
         InlineKeyboardButton("🔑 Group Link", url=GROUP_LINK)]
    ])
    try:
        await bot.send_message(
            chat_id=TARGET_CHAT, text=text,
            parse_mode="HTML", reply_markup=kb,
            disable_web_page_preview=True
        )
        print(f"✅ {service} | {masked} | {country}")
    except Exception as e:
        print(f"❌ Telegram error: {e}")

ts1 = None
ts2 = None
ts3 = None

async def poll_apis(context: ContextTypes.DEFAULT_TYPE):
    global ts1, ts2, ts3
    bot = context.bot

    # API 1
    try:
        r = requests.get(API1_URL, params={"token": API1_TOKEN},
                         headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list) and data:
                if ts1 is None:
                    ts1 = data[0][3]
                else:
                    new = [row for row in data if str(row[3]) > ts1]
                    for row in reversed(new):
                        is_new = add_to_cache(str(row[0] or "Unknown"), str(row[1] or ""), str(row[2] or ""), str(row[3] or ""))
                        if is_new:
                            await forward_to_group(bot, str(row[0] or "Unknown"), str(row[1] or ""), str(row[2] or ""), str(row[3] or ""))
                    if new:
                        ts1 = data[0][3]
    except Exception as e:
        print(f"❌ API1 error: {e}")

    # API 2
    try:
        r = requests.get(API2_URL, params={"token": API2_TOKEN},
                         headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if r.status_code == 200 and r.text.strip().startswith("["):
            data = r.json()
            if isinstance(data, list) and data:
                if ts2 is None:
                    ts2 = data[0][3]
                else:
                    new = [row for row in data if str(row[3]) > ts2]
                    for row in reversed(new):
                        is_new = add_to_cache(str(row[0] or "Unknown"), str(row[1] or ""), str(row[2] or ""), str(row[3] or ""))
                        if is_new:
                            await forward_to_group(bot, str(row[0] or "Unknown"), str(row[1] or ""), str(row[2] or ""), str(row[3] or ""))
                    if new:
                        ts2 = data[0][3]
    except Exception as e:
        print(f"❌ API2 error: {e}")

    # API 3
    try:
        import urllib3
        urllib3.disable_warnings()
        r = requests.get(API3_URL, params={"key": API3_KEY, "start": 0, "length": 20},
                         headers={"User-Agent": "Mozilla/5.0"}, timeout=10, verify=False)
        if r.status_code == 200:
            data = r.json()
            if data.get("result") == "success":
                items = data.get("data", [])
                if items:
                    if ts3 is None:
                        ts3 = items[0]["dateadded"]
                    else:
                        new = [i for i in items if str(i["dateadded"]) > ts3]
                        for item in reversed(new):
                            is_new = add_to_cache(
                                str(item.get("cli", "Unknown")),
                                str(item.get("num", "")),
                                str(item.get("sms", "")),
                                str(item.get("dateadded", ""))
                            )
                            if is_new:
                                await forward_to_group(bot,
                                    str(item.get("cli", "Unknown")),
                                    str(item.get("num", "")),
                                    str(item.get("sms", "")),
                                    str(item.get("dateadded", ""))
                                )
                        if new:
                            ts3 = items[0]["dateadded"]
    except Exception as e:
        print(f"❌ API3 error: {e}")

# --- MAIN ---
def main():
    print("🚀 OTP Bot Started!")
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.job_queue.run_repeating(poll_apis, interval=7, first=2)

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
