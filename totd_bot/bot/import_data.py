import csv
import logging

from sqlalchemy.exc import SQLAlchemyError

from bot.models import Wisdom
from bot.bot import create_session, engine

logger = logging.getLogger(__name__)


def import_tips(csv_path):
    logger.info('Import tips from file'.format(csv_path))
    with open(csv_path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        session = create_session(bind=engine)
        try:
            for i, row in enumerate(reader):
                logger.info('{}. {}'.format(i, row))
                session.add(Wisdom(text=row[0].strip()))
                session.commit()
        except SQLAlchemyError:
            raise
        finally:
            session.close()
