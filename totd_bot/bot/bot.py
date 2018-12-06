import datetime
import logging

import telegram

from environs import Env
from sqlalchemy import create_engine, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from telegram.ext import CommandHandler, Filters, Updater
from telegram.ext.jobqueue import Days

from bot.models import Base, Chat, Wisdom

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

env = Env()
try:
    env.read_env()
except FileNotFoundError:
    pass

db_url = env.str('DB_URL', '')
engine = create_engine(db_url)
create_session = sessionmaker()
Base.metadata.create_all(engine)


def start_bot():
    admin_user_ids = env.list('ADMIN_USER_IDS', '41669938', subcast=int)
    token = env.str('TG_API_TOKEN', '')
    hour_to_post = env.int('POST_HOUR', 12)
    minute_to_post = env.int('POST_MINUTE', 0)

    updater = Updater(token=token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('chat_id', show_chat_id))
    dispatcher.add_handler(CommandHandler('allow_chat', allow_chat, pass_args=True,
                                          filters=Filters.user(user_id=admin_user_ids)))
    dispatcher.add_handler(CommandHandler('list_chats', show_allowed_chats,
                                          filters=Filters.user(user_id=admin_user_ids)))
    dispatcher.add_handler(CommandHandler('add_wisdom', add_wisdom, pass_args=True,
                                          filters=Filters.user(user_id=admin_user_ids)))
    dispatcher.add_handler(CommandHandler('list_wisdoms', show_wisdoms,
                                          filters=Filters.user(user_id=admin_user_ids)))

    job_queue = updater.job_queue
    weekdays = (Days.MON, Days.TUE, Days.WED, Days.THU, Days.FRI)
    time_to_run = datetime.time(hour=hour_to_post, minute=minute_to_post)
    logger.info('Post time {}, Current datetime {}'.format(time_to_run, datetime.datetime.now()))
    job_queue.run_daily(post_wisdom, time=time_to_run, days=weekdays)
    # job_minute = job_queue.run_repeating(post_wisdom, interval=30)
    updater.start_polling()


def show_chat_id(bot, update):
    update.message.reply_text('Current chat id is "{}"'.format(update.message.chat_id))


def allow_chat(bot, update, args):
    if args:
        chat_id = args[0]
        chat = bot.get_chat(chat_id)
        session = create_session(bind=engine)
        session.add(Chat(id=chat_id, title=chat.title))
        session.commit()
        session.close()
        msg = 'Allowed wisdom posting at chat with id "{}"'.format(chat_id)
    else:
        msg = 'Empty chat_id, please place chat_id after command'
    update.message.reply_text(msg)


def show_allowed_chats(bot, update):
    session = create_session(bind=engine)
    try:
        text = '\n'.join(['{}.{} ({})'.format(n, s.title, s.id) for n, s in enumerate(session.query(Chat))])
    except SQLAlchemyError:
        raise
    finally:
        session.close()
    update.message.reply_text('Allowed chats:\n{}'.format(text))


def add_wisdom(bot, update, args):
    wisdom_text = ' '.join(args)
    if wisdom_text:
        session = create_session(bind=engine)
        wisdom = Wisdom(text=wisdom_text)
        session.add(wisdom)
        session.commit()
        session.close()
        msg = 'Your wisdom was added'
    else:
        msg = 'Empty wisdom, please place your thought after command'
    update.message.reply_text(msg)


def show_wisdoms(bot, update):
    session = create_session(bind=engine)
    try:
        text = '\n'.join(['{}.{}'.format(n, s.text) for n, s in enumerate(session.query(Wisdom)[:30])])
    except SQLAlchemyError:
        raise
    finally:
        session.close()
    update.message.reply_text('First 30 wisdoms I have:\n{}'.format(text))


def post_wisdom(bot, job):
    session = create_session(bind=engine)
    try:
        for chat in session.query(Chat):
            wisdom = session.query(Wisdom).order_by(func.random()).first()
            if wisdom:
                try:
                    bot.send_message(chat_id=chat.id, text=wisdom.text)
                except telegram.TelegramError as e:
                    logger.error('Failed to post wisdom at chat {}: {}'.format(chat.id, e))
    except SQLAlchemyError:
        raise
    finally:
        session.close()
