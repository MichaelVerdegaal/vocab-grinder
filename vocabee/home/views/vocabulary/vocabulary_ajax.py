import os
from pathlib import Path

from flask import Blueprint, request, Response

from vocabee.util.anki_util import create_deck_by_level
from vocabee.util.queries import get_vocab_by_level, get_vocab_by_id, update_vocab, add_vocab, delete_vocab
from vocabee.util.view_util import create_status
from vocabee.util.vocabulary_util import process_vocabulary

vocabulary_ajax_bp = Blueprint('vocabulary_ajax', __name__, url_prefix='/vocabulary/ajax')


# TODO: this needs caching
@vocabulary_ajax_bp.route('/source/<int:vocab_level>')
def vocabulary_full_get(vocab_level):
    """
    AJAX endpoint to retrieve vocabulary
    :param vocab_level: Valid JLPT vocabulary level (1-5)
    :return: vocabulary in JSON
    """
    if 0 < vocab_level < 6:
        status, vocab = get_vocab_by_level(vocab_level)
        if status['code'] == 200:
            vocab = process_vocabulary(vocab)
            return vocab, 200
        else:
            return status, 500
    else:
        return create_status(400, "Faulty vocabulary level"), 400


@vocabulary_ajax_bp.route('/source/entry/get/<int:vocab_id>')
def vocabulary_entry_get(vocab_id):
    """
    AJAX endpoint to retrieve vocabulary
    :param vocab_id: vocabulary id
    :return: vocabulary entry in JSON
    """
    status, entry = get_vocab_by_id(vocab_id)
    if entry:
        return entry.to_dict(), 200
    else:
        return status, status['code']


@vocabulary_ajax_bp.route('/source/entry/update', methods=['POST'])
def vocabulary_entry_update():
    """
    AJAX endpoint to update a vocabulary entry
    :return: status
    """
    data = request.json
    if not data:
        return create_status(400, "Data received is empty"), 400
    status = update_vocab(data['id'], data['kanji'], data['kana'], data['meaning'], data['jlpt_level'])
    if status['code'] == 200:
        return status, 200
    else:
        return status, 500


@vocabulary_ajax_bp.route('/source/entry/add', methods=['POST'])
def vocabulary_entry_add():
    """
    AJAX endpoint to add a vocabulary entry
    :return: status
    """
    data = request.json
    if not data:
        return create_status(400, "Data received is empty"), 400
    status = add_vocab(data['kanji'], data['kana'], data['meaning'], data['jlpt_level'])
    if status['code'] == 200:
        return status, 200
    else:
        return status, 500


@vocabulary_ajax_bp.route('/source/entry/delete', methods=['POST'])
def vocabulary_entry_delete():
    """
    AJAX endpoint to add a vocabulary entry
    :return: status
    """
    data = request.json
    if not data:
        return create_status(400, "Data received is empty"), 400
    status = delete_vocab(data['id'])
    if status['code'] == 200:
        return status, 200
    else:
        return status, 500


@vocabulary_ajax_bp.route('/source/anki/<int:vocab_level>')
def vocabulary_download_deck(vocab_level):
    """
    Creates download response for generated anki decks
    :param vocab_level: Valid JLPT vocabulary level (1-5)
    :return: downloaded file
    """
    status, vocab = get_vocab_by_level(vocab_level)
    print(status)
    if status['code'] == 200:
        # TODO make a proper constant for the static folder
        project_root = Path(vocabulary_ajax_bp.root_path).parents[3]
        filename = f'vocabee{vocab_level}.apkg'
        path = os.path.join(project_root, filename)
        create_deck_by_level(vocab, vocab_level, filename)

        # Ref: https://stackoverflow.com/a/57998006/7174982
        with open(path, 'rb') as f:
            data = f.readlines()
        os.remove(path)
        return Response(data, headers={'Content-Type': 'application/octet-stream',
                                       'Content-Disposition': f'attachment; filename={filename};'}), 200
    else:
        return status, 500
