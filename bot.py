import os
import requests

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Store unclear attempts for each Telegram user
failed_attempts = {}


def is_assignment_request(text):
    keywords = [
        "do my assignment",
        "do my homework",
        "complete my assignment",
        "answer my exam",
        "do my exam",
        "give me exam answers",
        "buat assignment saya",
        "buat kerja sekolah saya",
        "jawab exam saya",
        "buat homework saya"
    ]

    text = text.lower()

    return any(keyword in text for keyword in keywords)


def is_academic(text):
    academic_keywords = [
        "network",
        "computer",
        "programming",
        "programming language",
        "database",
        "sql",
        "java",
        "python",
        "html",
        "css",
        "mathematics",
        "math",
        "physics",
        "chemistry",
        "biology",
        "history",
        "sejarah",
        "bahasa melayu",
        "english",
        "formula",
        "algorithm",
        "algorithm",
        "server",
        "linux",
        "windows",
        "cybersecurity",
        "database",
        "rangkaian",
        "pengaturcaraan"
    ]

    text = text.lower()

    return any(keyword in text for keyword in academic_keywords)


def explain_topic(text):
    text = text.lower()

    if "network" in text or "rangkaian" in text:
        return (
            "🌐 **Network dalam bahasa mudah**\n\n"
            "Network ialah sekumpulan komputer atau peranti "
            "yang disambungkan supaya boleh berkomunikasi dan "
            "berkongsi data atau sumber.\n\n"
            "📌 Contoh:\n"
            "Telefon → Wi-Fi → Router → Internet\n\n"
            "Bayangkan network seperti jalan raya. "
            "Peranti ialah kenderaan dan data ialah barang "
            "yang bergerak melalui jalan tersebut."
        )

    if "database" in text:
        return (
            "🗄️ **Database dalam bahasa mudah**\n\n"
            "Database ialah tempat untuk menyimpan dan "
            "mengurus data secara tersusun.\n\n"
            "Contohnya, sistem sekolah boleh menyimpan:\n"
            "• Nama pelajar\n"
            "• ID pelajar\n"
            "• Kelas\n"
            "• Markah\n\n"
            "Database memudahkan kita mencari dan mengurus "
            "maklumat tersebut."
        )

    if "programming" in text or "pengaturcaraan" in text:
        return (
            "💻 **Programming dalam bahasa mudah**\n\n"
            "Programming ialah proses memberikan arahan "
            "kepada komputer supaya komputer melakukan sesuatu.\n\n"
            "Contohnya:\n"
            "Input → Proses → Output\n\n"
            "Kita memberikan arahan, komputer memproses arahan "
            "tersebut dan menghasilkan output."
        )

    return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = (
        "🤖 **Welcome to Ponder Bot!**\n\n"
        "Saya membantu anda memahami sesuatu topik, bukan "
        "membuat kerja akademik anda untuk anda.\n\n"
        "📚 Contoh soalan:\n"
        "• Explain network in simple terms\n"
        "• Explain this formula\n"
        "• Give me a practice question on network\n\n"
        "💡 Jika anda tidak memberikan subjek atau topik, "
        "saya akan minta anda nyatakan topik tersebut."
    )

    await update.message.reply_text(
        message,
        parse_mode="Markdown"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = (
        "📖 **Cara menggunakan Ponder Bot**\n\n"
        "Try asking:\n\n"
        "🌐 Explain network in simple terms\n"
        "🧮 Explain this formula\n"
        "📝 Give me a practice question on database\n"
        "💻 Explain programming\n\n"
        "Saya akan membantu anda memahami konsep tersebut."
    )

    await update.message.reply_text(
        message,
        parse_mode="Markdown"
    )


async def github_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    username = os.getenv("GITHUB_USERNAME")
    token = os.getenv("GITHUB_TOKEN")

    if not username or not token:
        await update.message.reply_text(
            "⚠️ GitHub belum disambungkan.\n\n"
            "Pastikan GITHUB_USERNAME dan GITHUB_TOKEN "
            "telah dimasukkan ke dalam .env."
        )
        return

    url = f"https://api.github.com/users/{username}/repos"

    try:
        response = requests.get(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json"
            },
            timeout=10
        )

        if response.status_code != 200:
            await update.message.reply_text(
                "❌ Tidak dapat mendapatkan repository GitHub."
            )
            return

        repositories = response.json()

        if not repositories:
            await update.message.reply_text(
                "📂 Tiada repository dijumpai."
            )
            return

        message = "🐙 **GitHub Repositories**\n\n"

        for repo in repositories[:10]:
            message += f"• [{repo['name']}]({repo['html_url']})\n"

        await update.message.reply_text(
            message,
            parse_mode="Markdown"
        )

    except Exception:
        await update.message.reply_text(
            "❌ Berlaku masalah ketika menyambung ke GitHub."
        )


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id
    text = update.message.text.strip()

    # Assignment / exam protection
    if is_assignment_request(text):

        await update.message.reply_text(
            "📚 Saya tak boleh membuat assignment, homework "
            "atau exam untuk anda.\n\n"
            "Tetapi saya boleh membantu anda dengan:\n"
            "• menerangkan konsep\n"
            "• memberikan hint\n"
            "• menunjukkan langkah penyelesaian\n"
            "• memberikan soalan latihan\n"
            "• menyemak percubaan jawapan anda\n\n"
            "Jika perlukan bantuan lanjut, saya boleh sambungkan "
            "anda kepada manusia."
        )
        return

    # Academic explanation
    answer = explain_topic(text)

    if answer:
        failed_attempts[user_id] = 0

        await update.message.reply_text(
            answer,
            parse_mode="Markdown"
        )
        return

    # Formula request
    if "formula" in text.lower():

        failed_attempts[user_id] = 0

        await update.message.reply_text(
            "🧮 Sure! Send me the formula you don't understand.\n\n"
            "I'll break it down into:\n"
            "1️⃣ What each symbol means\n"
            "2️⃣ What the formula is used for\n"
            "3️⃣ The steps to use it\n"
            "4️⃣ A simple example"
        )
        return

    # Practice question
    if "practice question" in text.lower():

        failed_attempts[user_id] = 0

        await update.message.reply_text(
            "📝 Sure! What subject or topic should the "
            "practice question be about?\n\n"
            "Example: `network`, `database`, `Java`"
        )
        return

    # No topic
    if len(text.split()) <= 2:

        await update.message.reply_text(
            "📚 Sure! What subject or topic would you "
            "like help with?\n\n"
            "For example:\n"
            "• Network\n"
            "• Database\n"
            "• Java\n"
            "• Mathematics"
        )
        return

    # Unknown question
    failed_attempts[user_id] = failed_attempts.get(user_id, 0) + 1

    if failed_attempts[user_id] < 2:

        await update.message.reply_text(
            "🤔 Sorry, I'm not quite sure what you mean.\n\n"
            "Could you rephrase your question or give me "
            "more details?"
        )

    else:

        failed_attempts[user_id] = 0

        await update.message.reply_text(
            "🤔 I'm still having trouble understanding this.\n\n"
            "I don't want to give you incorrect information.\n\n"
            "Would you like me to connect you with a human "
            "for further help?"
        )


def main():

    if not TELEGRAM_TOKEN:
        print("❌ TELEGRAM_TOKEN belum dimasukkan dalam .env")
        return

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("github", github_command))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    print("🤖 Ponder Bot is running...")

    app.run_polling()


if __name__ == "__main__":
    main()
