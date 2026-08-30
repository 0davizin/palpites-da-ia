import os
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

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
            return {"paises": []}

@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("⚽ JOGOS DE HOJE", callback_data="jogos_hoje"),
        InlineKeyboardButton("📊 Estatísticas", callback_data="estatisticas"),
        InlineKeyboardButton("🎯 Múltipla do Dia", callback_data="multipla")
    )
    bot.reply_to(message, "👋 Olá! Bem-vindo ao *PALPITES DA IA*!\n\nEscolha uma opção no menu abaixo:", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    dados = carregar_dados()
    paises = dados.get("paises", [])

    if call.data == "jogos_hoje":
        if not paises:
            bot.answer_callback_query(call.id, "Nenhum país cadastrado para hoje.")
            return
        
        markup = InlineKeyboardMarkup()
        for p in paises:
            markup.add(InlineKeyboardButton(f"{p['pais_nome']} - {p['campeonato']}", callback_data=f"pais_{p['id']}"))
        
        bot.edit_message_text("🌍 *Escolha o País / Liga:*", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data.startswith("pais_"):
        pais_id = call.data.replace("pais_", "")
        pais_selecionado = next((p for p in paises if p["id"] == pais_id), None)
        
        if not pais_selecionado or not pais_selecionado.get("jogos"):
            bot.answer_callback_query(call.id, "Nenhum jogo encontrado para este país.")
            return
        
        markup = InlineKeyboardMarkup()
        for jogo in pais_selecionado["jogos"]:
            nome_jogo = f"{jogo['time_casa']} x {jogo['time_fora']}"
            markup.add(InlineKeyboardButton(f"⚽ {nome_jogo}", callback_data=f"jogo_{pais_id}_{jogo['id']}"))
        
        markup.add(InlineKeyboardButton("⬅️ Voltar aos Países", callback_data="jogos_hoje"))
        bot.edit_message_text(f"🏆 *Jogos - {pais_selecionado['pais_nome']}*:\nEscolha a partida:", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data.startswith("jogo_"):
        partes = call.data.split("_")
        pais_id = partes[1]
        jogo_id = partes[2]
        
        pais_selecionado = next((p for p in paises if p["id"] == pais_id), None)
        if pais_selecionado:
            jogo = next((j for j in pais_selecionado["jogos"] if j["id"] == jogo_id), None)
            if jogo:
                msg = f"🔥 *{pais_selecionado['pais_nome']} - {pais_selecionado['campeonato']}* 🔥\n\n"
                msg += f"🏟️ *{jogo['time_casa']} x {jogo['time_fora']}*\n\n"
                msg += f"⚽ *Média de Gols:* {jogo['media_gols']}\n"
                msg += f"🚩 *Média de Escanteios:* {jogo['media_escanteios']}\n"
                msg += f"🟨 *Média de Cartões:* {jogo['media_cartoes']}\n\n"
                msg += f"🎯 *(ENTRADA DA IA)*:\n👉 *{jogo['entrada_ia']}*"

                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton("⬅️ Voltar aos Jogos", callback_data=f"pais_{pais_id}"))
                
                bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "estatisticas":
        bot.answer_callback_query(call.id, "Taxa de assertividade atual: 78.5%")

    elif call.data == "multipla":
        bot.answer_callback_query(call.id, "Consulte os jogos no menu de Jogos de Hoje!")

    bot.answer_callback_query(call.id)

if __name__ == "__main__":
    bot.infinity_polling()
    
