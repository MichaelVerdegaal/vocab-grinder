from flask import current_app as app
from vocabee import cache
from vocabee.home.models import Vocabulary


@cache.memoize(60)
def get_vocab_by_level(jlpt_level):
    """
    Fetches vocabulary entries by JLPT level
    :param jlpt_level: Vocabulary level
    :return: Queryset
    """
    vocabulary = app.session.query(Vocabulary).filter_by(jlpt_level=f"N{jlpt_level}").all()
    app.session.remove()
    return vocabulary
