#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.
"""
This Bot uses the Updater class to handle the bot.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic inline bot example. Applies different text transformations.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
##botfather change commands format
##
##accompagnatori_ag - Elenco accompagnatori
##calendario_ag - Calendario AG
##gita_ag - Info prossima gita AG
##prossima_gita_ag - Info prossima gita AG
##ultima_gita_ag - Info ultima gita AG effettuata
##sede - Orari e riferimenti sede
##per_il_resto_chiedete_a_ivan - Il vostro aiutante di fiducia

from uuid import uuid4

import re
import os
import sys
import xml.etree.cElementTree as StringParseXML
from telegram import InlineQueryResultArticle, ParseMode, \
    InputTextMessageContent
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
import logging

#get current working directory
#http://stackoverflow.com/questions/4060221/how-to-reliably-open-a-file-in-the-same-directory-as-a-python-script
__location__ = os.path.dirname(os.path.abspath(sys.argv[0]))
#print os.path.basename(sys.argv[0])
#print __location__

#XML Config is located in same path of script.
#Configuration name is same as script name, but with an "xml" extension instead of "py"
ScriptName = os.path.basename(sys.argv[0])
XMLConfig = os.path.join(__location__, ScriptName.replace(".py", ".xml"))
#print XMLConfig

tree = StringParseXML.parse(XMLConfig)
StringParse = tree.getroot()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

#populate strings

#accompagnatori
text_elenco_accompagnatori = ''
for elem in tree.findall('accompagnatori_ag/accompagnatore'):
  text_elenco_accompagnatori += elem.text
  text_elenco_accompagnatori += '\n'
##print elenco_accompagnatori

text_calendario = ''
text_calendario = 'Calendario AG ' 
text_calendario += tree.find('anno').text
text_calendario += '\n'
for elem in tree.findall('calendario_ag/gita'):
  text_calendario += '\n\nData: '
  text_calendario += elem.find('date').text
  text_calendario += '\n Destinazione: \n  '
  text_calendario += elem.find('destinazione').text
  if elem.find('percorso').text != "no":
    text_calendario += '\nPercorso:\n'
    text_calendario += elem.find('percorso').text
  if elem.find('altimetria').text != "no":
    text_calendario += '\nProfilo altimetrico:\n'
    text_calendario += elem.find('altimetria').text
  if elem.find('foto').text != "no":
    text_calendario += '\nGalleria Fotografica:\n'
    text_calendario += elem.find('foto').text
text_calendario += '\n\n\nScarica l\'agendina:\n'
text_calendario += tree.find('calendario_ag/url_agendina').text

#print index_prossima_gita
text_prossima_gita = ''
index_prossima_gita = tree.find('gita_ag/prossima_gita').text
text_prossima_gita = 'La prossima gita sarà:\n'
text_prossima_gita += tree.find(".//calendario_ag/gita[@name='" + index_prossima_gita + "']/date").text
text_prossima_gita += '\nDestinazione:\n'
text_prossima_gita += tree.find(".//calendario_ag/gita[@name='" + index_prossima_gita + "']/destinazione").text
text_prossima_gita += '\n'
if tree.find(".//calendario_ag/gita[@name='" + index_prossima_gita + "']/ritrovo").text != "no":
    text_prossima_gita += tree.find(".//calendario_ag/gita[@name='" + index_prossima_gita + "']/ritrovo").text
text_prossima_gita += '\nAdesione alla gita:\n'
text_prossima_gita += tree.find(".//calendario_ag/gita[@name='" + index_prossima_gita + "']/conferma_data").text
if tree.find(".//calendario_ag/gita[@name='" + index_prossima_gita + "']/disdetta_data").text != "no":
    text_prossima_gita += '\nDisdetta alla gita:\n'
    text_prossima_gita += tree.find(".//calendario_ag/gita[@name='" + index_prossima_gita + "']/disdetta_data").text
text_prossima_gita += '\nCome aderire: '
text_prossima_gita += tree.find(".//calendario_ag/gita[@name='" + index_prossima_gita + "']/conferma_rif").text
if tree.find(".//calendario_ag/gita[@name='" + index_prossima_gita + "']/costo").text != "no":
    text_prossima_gita += '\nCosto gita: '
    text_prossima_gita += tree.find(".//calendario_ag/gita[@name='" + index_prossima_gita + "']/costo").text
text_prossima_gita += '\nNotiziario:\n'
text_prossima_gita += tree.find(".//calendario_ag/gita[@name='" + index_prossima_gita + "']/notiziario").text
##print text_prossima_gita

#informazioni sede
text_sede_cai = ''
text_sede_cai = 'La sede è aperta '
text_sede_cai += tree.find('sede/apertura').text
text_sede_cai += '\nIndirizzo: '
text_sede_cai += tree.find('sede/indirizzo').text
text_sede_cai += '\nTelefono: '
text_sede_cai += tree.find('sede/telefono').text
text_sede_cai += '\nemail: '
text_sede_cai += tree.find('sede/email').text
text_sede_cai += '\ngruppo telegram AG: \n '
text_sede_cai += tree.find('sede/telegram_group').text

#dati ultima gita
text_ultima_gita = ''
index_ultima_gita = tree.find('gita_ag/ultima_gita').text
text_ultima_gita = 'L\'ultima gita è stata: \n'
text_ultima_gita += tree.find(".//calendario_ag/gita[@name='" + index_ultima_gita + "']/date").text
text_ultima_gita += '\nDestinazione: '
text_ultima_gita += tree.find(".//calendario_ag/gita[@name='" + index_ultima_gita + "']/destinazione").text
if tree.find(".//calendario_ag/gita[@name='" + index_ultima_gita + "']/percorso").text != "no":
    text_ultima_gita += '\nPercorso:\n'
    text_ultima_gita += tree.find(".//calendario_ag/gita[@name='" + index_ultima_gita + "']/percorso").text
if tree.find(".//calendario_ag/gita[@name='" + index_ultima_gita + "']/altimetria").text != "no":
    text_ultima_gita += '\nProfilo altimetrico:\n'
    text_ultima_gita += tree.find(".//calendario_ag/gita[@name='" + index_ultima_gita + "']/altimetria").text
##print tree.find(".//calendario_ag/gita[@name='" + index_ultima_gita + "']/foto").text
if tree.find(".//calendario_ag/gita[@name='" + index_ultima_gita + "']/foto").text != "no":
    text_ultima_gita += '\nGalleria Fotografica:\n'
    text_foto = tree.find(".//calendario_ag/gita[@name='" + index_ultima_gita + "']/foto").text
    text_ultima_gita += text_foto.replace("%26", "&")

##ivan_help
text_ivan_help = 'Ivan, il vostro nerd/climber/accompagnatore AG/massaggiatore thai di fiducia \n'
text_ivan_help += 'e\' contattabile al numero +393288660991, o su telegram come @theQuillan'

#weekhook setup
#webhooks.xml usually contains two sets of webhooks: test and production webhooks,
#so you can test configuration files
WebhooksXMLConfig = os.path.join(__location__, "webhooks.xml")
WebHooks = StringParseXML.parse(WebhooksXMLConfig)
WebHooksStringParse = WebHooks.getroot()
if tree.find('usetestwebhook').text == "0":
    UpdaterWebHook=WebHooksStringParse.find(".//webhook[@name='production']/updater").text
else:
    UpdaterWebHook=WebHooksStringParse.find(".//webhook[@name='test']/updater").text

print UpdaterWebHook

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    update.message.reply_text('Hi!')


def help(bot, update):
    update.message.reply_text('Help!')

def accompagnatori_ag(bot, update):
    update.message.reply_text('Accompagnatori (elenco parziale):\n' + text_elenco_accompagnatori)

def calendario_ag(bot, update):
    update.message.reply_text(text_calendario)

def prossima_gita_ag(bot, update):
    update.message.reply_text(text_prossima_gita)

def sede(bot, update):
    update.message.reply_text(text_sede_cai)

def ultima_gita_ag(bot, update):
    update.message.reply_text(text_ultima_gita)

def ivan_help(bot, update):
	update.message.reply_text(text_ivan_help)

def escape_markdown(text):
    """Helper function to escape telegram markup symbols"""
    escape_chars = '\*_`\['
    return re.sub(r'([%s])' % escape_chars, r'\\\1', text)

def inlinequery(bot, update):
    query = update.inline_query.query
    results = list()

    results.append(InlineQueryResultArticle(id=uuid4(),
                                            title="Caps",
                                            input_message_content=InputTextMessageContent(
                                                query.upper())))

    results.append(InlineQueryResultArticle(id=uuid4(),
                                            title="Bold",
                                            input_message_content=InputTextMessageContent(
                                                "*%s*" % escape_markdown(query),
                                                parse_mode=ParseMode.MARKDOWN)))

    results.append(InlineQueryResultArticle(id=uuid4(),
                                            title="Italic",
                                            input_message_content=InputTextMessageContent(
                                                "_%s_" % escape_markdown(query),
                                                parse_mode=ParseMode.MARKDOWN)))

    update.inline_query.answer(results)


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    # Create the Updater and pass it your bot's token.
    # main bot
    #updater = Updater("273270658:AAF9aFXNQMJVCIC7zkRz2wTq3Di_pu5K27Q")
    # test bot
##    updater = Updater("271724007:AAER6CE14p9i1ofjHwu2x7BaConwzsITyOI")
    print UpdaterWebHook
    updater = Updater(UpdaterWebHook.replace("\"",""))
    # Get the dispatcher to register handlers
    dp = updater.dispatcher


    #populate the text strings based on data file


    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("sede", sede))
    dp.add_handler(CommandHandler("gita_ag",prossima_gita_ag))
    dp.add_handler(CommandHandler("prossima_gita_ag",prossima_gita_ag))
    dp.add_handler(CommandHandler("ultima_gita_ag",ultima_gita_ag))
    dp.add_handler(CommandHandler("accompagnatori_ag",accompagnatori_ag))
    dp.add_handler(CommandHandler("calendario_ag",calendario_ag))
    dp.add_handler(CommandHandler("per_il_resto_chiedete_a_ivan",ivan_help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(InlineQueryHandler(inlinequery))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
