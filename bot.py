import os, random, logging, json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = "8637209240:AAGieFcLTbAeclcPzEuoxx2LM4at8HCumNE"
logging.basicConfig(level=logging.INFO)

def load_questions():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    questions_path = os.path.join(base_dir, "questions.json")
    with open(questions_path, "r", encoding="utf-8") as f:
        return json.load(f)

QUESTIONS = load_questions()

user_state = {}

MODE_SIZES = {
    "20": 20,
    "50": 50,
    "all": len(QUESTIONS),
}


def new_quiz(uid, mode="20"):
    pool = QUESTIONS.copy()
    random.shuffle(pool)
    size = MODE_SIZES.get(mode, 20)
    user_state[uid] = {"q": pool[: min(size, len(pool))], "i": 0, "score": 0, "mode": mode}
    return user_state[uid]

def get_state(uid):
    if uid not in user_state:
        user_state[uid] = {"q": [], "i": 0, "score": 0}
    return user_state[uid]

async def send_q(target, state, edit=False):
    i = state["i"]
    q = state["q"][i]
    total = len(state["q"])
    ru_opts = q.get("opts_ru", [])
    ru_lines = []
    if q.get("q_ru"):
        ru_lines.append(f"🇷🇺 _{q['q_ru']}_")
    if ru_opts and len(ru_opts) == len(q["opts"]):
        for j, opt_ru in enumerate(ru_opts):
            ru_lines.append(f"_{chr(65 + j)}. {opt_ru}_")
    ru_block = "\n".join(ru_lines)
    text = f"❓ *Klausimas {i+1}/{total}*\n\n{q['q']}"
    if ru_block:
        text += f"\n\n{ru_block}"
    btns = [[InlineKeyboardButton(f"{chr(65+j)}. {o}", callback_data=f"ans_{j}")] for j,o in enumerate(q["opts"])]
    markup = InlineKeyboardMarkup(btns)
    if edit:
        await target.edit_message_text(text, reply_markup=markup, parse_mode="Markdown")
    else:
        msg = target.message if hasattr(target,"message") else target
        await msg.reply_text(text, reply_markup=markup, parse_mode="Markdown")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("20 klausimų", callback_data="mode_20")],
        [InlineKeyboardButton("50 klausimų", callback_data="mode_50")],
        [InlineKeyboardButton("Visas bankas", callback_data="mode_all")],
    ])
    await update.message.reply_text(
        f"тест для картошечкав\n\n"
        f"🇱🇹 *Konstitucijos treniruoklis*\n\n"
        f"Банк: *{len(QUESTIONS)} вопросов*.\n"
        f"Выбери режим: *20*, *50* или *весь банк*.\n"
        f"Вопросы и кнопки — на литовском, русский текст даётся как справка.\n"
        f"85%+ = сдал ✅\n\n"
        f"Варианты команд:\n"
        f"/start — начать тест\n"
        f"/restart — начать заново\n\n"
        f"Выбери режим ниже 👇",
        reply_markup=keyboard,
        parse_mode="Markdown")

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)


async def handle_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = update.effective_user.id
    mode = query.data.split("_", 1)[1]
    state = new_quiz(uid, mode=mode)
    mode_label = "20" if mode == "20" else "50" if mode == "50" else f"visas ({len(QUESTIONS)})"
    await query.edit_message_text(
        f"✅ Pasirinktas režimas: *{mode_label}* klausimų.\nPradedame!",
        parse_mode="Markdown",
    )
    await send_q(query, state, edit=False)

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    uid = update.effective_user.id; state = get_state(uid)
    if not state["q"]:
        await query.edit_message_text("Spustelėk /start"); return
    chosen = int(query.data.split("_")[1])
    i = state["i"]; q = state["q"][i]; correct = q["answer"]
    opts_text = ""
    for j,o in enumerate(q["opts"]):
        if j==correct and j==chosen: opts_text += f"✅ *{chr(65+j)}. {o}*\n"
        elif j==correct: opts_text += f"✅ *{chr(65+j)}. {o}*\n"
        elif j==chosen: opts_text += f"❌ {chr(65+j)}. {o}\n"
        else: opts_text += f"▫️ {chr(65+j)}. {o}\n"
    if chosen==correct:
        state["score"] += 1; result = "✅ *Teisingai!*"
    else:
        result = f"❌ *Neteisingai.* Teisingas: *{chr(65+correct)}*"
    explain = f"\n\n📖 _{q.get('explain','')}_"
    state["i"] += 1; total = len(state["q"])
    btn = [[InlineKeyboardButton("➡️ Kitas", callback_data="next")]] if state["i"]<total else [[InlineKeyboardButton("🔄 Iš naujo", callback_data="restart")]]
    ru_q = f"\n🇷🇺 _{q['q_ru']}_" if q.get("q_ru") else ""
    await query.edit_message_text(
        f"❓ *Klausimas {i+1}*\n_{q['q']}_{ru_q}\n\n{opts_text}\n{result}{explain}",
        reply_markup=InlineKeyboardMarkup(btn), parse_mode="Markdown")

async def handle_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    uid = update.effective_user.id; state = get_state(uid)
    if state["i"] >= len(state["q"]):
        s=state["score"]; t=len(state["q"]); p=round(s/t*100)
        v = "🎉 *Puikiai! Išlaikytumėte!*" if p>=85 else "👍 *Gerai, bet tobulinkite.*" if p>=70 else "📚 *Reikia daugiau praktikos.*"
        await query.edit_message_text(f"🏁 *Тест завершён!*\n\n*{s}/{t}* ({p}%)\n\n{v}\n\n/start — снова", parse_mode="Markdown"); return
    await send_q(query, state, edit=True)

async def handle_restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    uid = update.effective_user.id
    prev_mode = get_state(uid).get("mode", "20")
    state = new_quiz(uid, mode=prev_mode)
    await query.edit_message_text("🔄 Новый тест! Поехали 💪", parse_mode="Markdown")
    await send_q(query, state, edit=False)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("restart", restart))
    app.add_handler(CallbackQueryHandler(handle_mode, pattern="^mode_(20|50|all)$"))
    app.add_handler(CallbackQueryHandler(handle_answer, pattern="^ans_"))
    app.add_handler(CallbackQueryHandler(handle_next, pattern="^next$"))
    app.add_handler(CallbackQueryHandler(handle_restart, pattern="^restart$"))
    print(f"✅ Бот запущен! Вопросов: {len(QUESTIONS)}")
    app.run_polling()

if __name__ == "__main__":
    main()