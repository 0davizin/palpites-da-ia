import os
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Servidor web falso para o Render não cair
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

# 🔑 COLOQUE SEU ID DO TELEGRAM AQUI ABAIXO PARA SER O ADMIN EXCLUSIVO:
ADMIN_ID = 8271721680  # Substitua pelo seu ID real

def carregar_dados():
    try:
        with open("database.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"paises": []}

def salvar_dados(dados):
    with open("database.json", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

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

# 🧠 MODO INTELIGENTE: ADMIN ALIMENTANDO O ROBÔ POR TEXTO
@bot.message_handler(func=lambda message: message.from_user.id == ADMIN_ID and "ANÁLISE IA:" in message.text)
def cadastrar_jogo_automatico(message):
    texto = message.text
    try:
        linhas = [l.strip() for l in texto.split("\n") if l.strip()]
        
        # Extração inteligente dos dados baseada no seu texto
        pais_campeonato = linhas[1].replace("🌍", "").strip() # Ex: 🇧🇷 Brasil - Brasileirão Série A
        partida = linhas[2].replace("🏟️", "").replace("⚽", "").strip() # Ex: Flamengo x Botafogo
        gols = linhas[3].replace("⚽ Média de Gols:", "").strip()
        escanteios = linhas[4].replace("🚩 Média de Escanteios:", "").strip()
        cartoes = linhas[5].replace("🟨 Média de Cartões:", "").strip()
        entrada = linhas[6].replace("🎯 ENTRADA DA IA:", "").replace("👉", "").strip()

        # Separar país e campeonato
        if "-" in pais_campeonato:
            pais_nome, campeonato = pais_campeonato.split("-", 1)
            pais_nome = pais_nome.strip()
            campeonato = campeonato.strip()
        else:
            pais_nome = pais_campeonato
            campeonato = "Geral"

        # Separar times
        if " x " in partida:
            time_casa, time_fora = partida.split(" x ", 1)
        elif " vs " in partida:
            time_casa, time_fora = partida.split(" vs ", 1)
        else:
            time_casa, time_fora = partida, "Adversário"

        # Gerar IDs limpos
        pais_id = pais_nome.lower().replace(" ", "").replace("🇧🇷", "brasil").replace("🇳🇱", "holanda")
        jogo_id = f"{time_casa.lower().replace(' ', '')}_{time_fora.lower().replace(' ', '')}"

        dados = carregar_dados()
        
        # Procurar se o país já existe
        pais_obj = next((p for p in dados["paises"] if p["id"] == pais_id), None)
        
        novo_jogo = {
            "id": jogo_id,
            "time_casa": time_casa.strip(),
            "time_fora": time_fora.strip(),
            "media_gols": gols,
            "media_escanteios": escanteios,
            "media_cartoes": cartoes,
            "entrada_ia": entrada
        }

        if pais_obj:
            # Evitar duplicata do mesmo jogo
            pais_obj["jogos"] = [j for j in pais_obj["jogos"] if j["id"] != jogo_id]
            pais_obj["jogos"].append(novo_jogo)
        else:
            novo_pais = {
                "id": pais_id,
                "pais_nome": pais_nome,
                "campeonato": campeonato,
                "jogos": [novo_jogo]
            }
            dados["paises"].append(novo_pais)

        salvar_dados(dados)
        bot.reply_to(message, "✅ *Jogo cadastrado e organizado com sucesso pela IA!* 🚀", parse_mode="Markdown")

    except Exception as e:
        bot.reply_to(message, f"❌ Erro ao processar o texto. Verifique o formato.\nDetalhes: {e}")

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    dados = carregar_dados()
    paises = dados.get("paises", [])

    if call.data == "jogos_hoje":
        if not paises:
            bot.answer_callback_query(call.id, "Nenhum jogo cadastrado para hoje.")
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
    
