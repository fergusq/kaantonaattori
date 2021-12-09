import logging

from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, Updater
from telegram.ext import MessageHandler, Filters

import salaisuus
from käännä import Kääntäjä

import stanza

import shelve

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

updater = Updater(token=salaisuus.TOKEN)

nlp = stanza.Pipeline(lang='multilingual', processors='langid', langid_lang_subset=['en','fi'])
kääntäjät = {'en':Kääntäjä("en", "fi"), 'fi':Kääntäjä("fi", "en")}


def tee_komento(kääntäjä):
	def komento(update: Update, context: CallbackContext):
		reply = update.effective_message.reply_to_message
		if reply:
			teksti = reply.text
			nimi = ""
			if reply.from_user:
				nimi = reply.from_user.full_name + ": "

		else:
			teksti = " ".join(context.args)
			nimi = ""
			if update.effective_user:
				nimi = update.effective_user.full_name + ": "

		käännös = kääntäjä.käännä(teksti)
		context.bot.send_message(chat_id=update.effective_chat.id, text=nimi+käännös)
	
	return komento

updater.dispatcher.add_handler(CommandHandler("ensu", tee_komento(kääntäjät['en'])))
updater.dispatcher.add_handler(CommandHandler("suen", tee_komento(kääntäjät['fi'])))

def muokkaa(update: Update, context: CallbackContext):
	teksti = " ".join(context.args)
	update.effective_message.reply_to_message.edit_text(teksti)
	update.effective_message.delete()

updater.dispatcher.add_handler(CommandHandler("edit", muokkaa))
updater.dispatcher.add_handler(CommandHandler("muokkaa", muokkaa))

def automaattipäälle(update: Update, context: CallbackContext):
	with shelve.open('idt') as hylly:
		hylly[str(update.effective_chat.id)] = True
	context.bot.send_message(chat_id=update.effective_chat.id, text="Automaattikääntäminen päällä.\nAutomatic translating on.")

updater.dispatcher.add_handler(CommandHandler("automation_on", automaattipäälle))
updater.dispatcher.add_handler(CommandHandler("automaatti", automaattipäälle))

def automaattipois(update: Update, context: CallbackContext):
	with shelve.open('idt') as hylly:
		del hylly[str(update.effective_chat.id)]
	context.bot.send_message(chat_id=update.effective_chat.id, text="Automaattikääntäminen pois päältä.\nAutomatic translating off.")

updater.dispatcher.add_handler(CommandHandler("automation_off", automaattipois))
updater.dispatcher.add_handler(CommandHandler("automaatti_pois", automaattipois))

def kaiku(update: Update, context: CallbackContext):
	with shelve.open('idt') as hylly:
		if str(update.effective_chat.id) in hylly:
			doc = nlp(update.message.text)
			käännös = kääntäjät[doc.lang].käännä(update.message.text)
			nimi = ""
			if update.effective_user:
				nimi = update.effective_user.full_name + ": "
			context.bot.send_message(chat_id=update.effective_chat.id, text=nimi+käännös)

updater.dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), kaiku))

updater.start_polling()

