from __future__ import annotations

from flask import Blueprint

bp = Blueprint('monitoring', __name__)


@bp.route('/health', methods=['GET'])
def health_check() -> dict[str, str]:
    return {'status': 'OK'}
