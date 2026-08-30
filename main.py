import json
import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Cole aqui o Token do seu Bot do Telegram (pegue com o @BotFather)
TOKEN = "8882509587:AAGtBR4gtIIdH1dNdJconBEedT67NDLK6ck"

bot = telebot.TeleBot(TOKEN)

# Função para carregar o arquivo JSON com os dados dos jogos
def carregar_dados():
    if not os.path.exists("database.json"):
        return {"jogos": [], "multipla_seguranca": "Nenhuma múltipla cadastrada."}
    with open("database.json", "r", encoding="utf-8") as f:
        return json.load(f)

# Comando /start - O ponto de partida do usuário no bot
@bot.message_handler(commands=['start'])
def enviar_welcome(message):
    nome_usuario = message.from_user.first_name
    
    texto = (
        f"⚽ **Bem-vindo ao PALPITES DA IA, {nome_usuario}!** 🤖🔥\n\n"
        "Aqui você encontra as análises estatísticas profissionais dos jogos do dia, "
        "com médias detalhadas de gols, escanteios, cartões e os nossos palpites de maior confiança.\n\n"
        "Escolha uma das opções abaixo para começar:"
    )
    
    # Criando os botões principais do menu
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📅 JOGOS DE HOJE", callback_data="listar_jogos"))
    markup.add(InlineKeyboardButton("🎟️ MÚLTIPLA DE SEGURANÇA", callback_data="ver_multipla"))
    
    bot.send_message(message.chat.id, texto, parse_mode="Markdown", reply_markup=markup)

# Callback para listar os jogos cadastrados
@bot.callback_query_handler(func=lambda call: call.data == "listar_jogos")
def callback_listar_jogos(call):
    dados = carregar_dados()
    jogos = dados.get("jogos", [])
    
    if not jogos:
        bot.answer_callback_query(call.id, "Nenhum jogo cadastrado no momento!")
        return
    
    markup = InlineKeyboardMarkup()
    for jogo in jogos:
        # Cria um botão para cada jogo usando o ID dele
        markup.add(InlineKeyboardButton(f"⚽ {jogo['confronto']}", callback_data=f"jogo_{jogo['id']}"))
    
    markup.add(InlineKeyboardButton("⬅️ Voltar ao Menu", callback_data="voltar_menu"))
    
    bot.edit_message_text(
        "📋 **Selecione abaixo o confronto que deseja analisar:**",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown",
        reply_markup=markup
    )

# Callback quando o usuário clica em um jogo específico
@bot.callback_query_handler(func=lambda call: call.data.startswith("jogo_"))
detalhes_jogo = 0 # apenas para escopo
def callback_detalhes_jogo(call):
    jogo_id = call.data.split("_")[1]
    dados = carregar_dados()
    jogos = dados.get("jogos", [])
    
    # Busca o jogo correspondente pelo ID
    jogo_selecionado = None
    for j in jogos:
        if j["id"] == jogo_id:
            jogo_selecionado = j
            break
            
    if not jogo_selecionado:
        bot.answer_callback_query(call.id, "Jogo não encontrado!")
        return
        
    # Monta o card detalhado do jogo
    texto = (
        f"⚔️ **{jogo_selecionado['confronto']}**\n"
        f"🏆 *Campeonato:* {jogo_selecionado['campeonato']}\n"
        f"⏰ *Horário:* {jogo_selecionado['horario']}\n\n"
        f"📊 **PROBABILIDADES DE RESULTADO:**\n{jogo_selecionado['probabilidades']}\n\n"
        f"⚽ **MÉDIAS DE GOLS:**\n{jogo_selecionado['gols']}\n\n"
        f"🚩 **ESCANTEIOS:**\n{jogo_selecionado['escanteios']}\n\n"
        f"🟨 **CARTÕES:**\n{jogo_selecionado['cartoes']}\n\n"
        f"🎯 **AMBAS MARCAM:** {jogo_selecionado['ambas_marcam']}\n\n"
        f"💡 **PALPITE DE CONFIANÇA:**\n👉 *{jogo_selecionado['palpite_confianca']}*"
    )
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅️ Voltar para a Lista", callback_data="listar_jogos"))
    
    bot.edit_message_text(
        texto,
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown",
        reply_markup=markup
    )

# Callback para exibir a múltipla de segurança
@bot.callback_query_handler(func=lambda call: call.data == "ver_multipla")
def callback_ver_multipla(call):
    dados = carregar_dados()
    multipla = dados.get("multipla_seguranca", "Sem dados.")
    
    texto = (
        f"🎟️ **MÚLTIPLA DE SEGURANÇA DO DIA**\n\n"
        f"{multipla}\n\n"
        "*(Linhas validadas com base estatística para proteção e alta assertividade)*"
    )
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅️ Voltar ao Menu", callback_data="voltar_menu"))
    
    bot.edit_message_text(
        texto,
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown",
        reply_markup=markup
    )

# Callback para voltar ao menu principal
@bot.callback_query_handler(func=lambda call: call.data == "voltar_menu")
def callback_voltar_menu(call):
    texto = (
        "⚽ **PALPITES DA IA - Menu Principal**\n\n"
        "Escolha uma das opções abaixo:"
    )
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📅 JOGOS DE HOJE", callback_data="listar_jogos"))
    markup.add(InlineKeyboardButton("🎟️ MÚLTIPLA DE SEGURANÇA", callback_data="ver_multipla"))
    
    bot.edit_message_text(
        texto,
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown",
        reply_markup=markup
    )

# Inicia o Bot
if __name__ == "__main__":
    print("🤖 Bot PALPITES DA IA iniciado com sucesso...")
    bot.infinity_polling()
