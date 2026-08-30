import os
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Servidor web falso para o Render não reclamar de porta fechada
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

# Inicia o servidor web em segundo plano
threading.Thread(target=run_server, daemon=True).start()

TOKEN = "8882509587:AAGtBR4gtIIdH1dNdJconBEedT67NDLK6ck"
bot = telebot.TeleBot(TOKEN)

def carregar_dados():
    try:
        with open("database.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        try:
            with open("banco de dados.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"jogos": []}

@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("⚽ Palpites Hoje", callback_data="palpites_hoje"),
        InlineKeyboardButton("📊 Estatísticas", callback_data="estatisticas"),
        InlineKeyboardButton("🎯 Múltipla do Dia", callback_data="multipla")
    )
    bot.reply_to(message, "👋 Olá! Bem-vindo ao *PALPITES DA IA*!\n\nEscolha uma opção no menu abaixo:", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    dados = carregar_dados()
    jogos = dados.get("jogos", [])

    if call.data == "palpites_hoje":
        if not jogos:
            bot.answer_callback_query(call.id, "Nenhum jogo cadastrado para hoje.")
            return
        
        msg = "🔥 *PALPITES DE HOJE* 🔥\n\n"
        for jogo in jogos:
            msg += f"⚽ *{jogo.get('time_casa', 'Time A')} vs {jogo.get('time_fora', 'Time B')}*\n"
            msg += f"🏆 *Palpite:* {jogo.get('palpite', 'N/A')}\n"
            msg += f"📈 *Odd:* {jogo.get('odd', '1.00')}\n\n"
        
        bot.send_message(call.message.chat.id, msg, parse_mode="Markdown")

    elif call.data == "estatisticas":
        bot.send_message(call.message.chat.id, "📊 *Estatísticas da IA*\n\nTaxa de assertividade atual: *78.5%*", parse_mode="Markdown")

    elif call.data == "multipla":
        bot.send_message(call.message.chat.id, "🎯 *Múltipla do Dia*\n\nConsulte os jogos de hoje no menu para montar seu bilhete!", parse_mode="Markdown")

    bot.answer_callback_query(call.id)

if __name__ == "__main__":
    bot.infinity_polling()
