from __future__ import annotations

import logging

formatter = logging.Formatter('[%(name)s][%(asctime)s] %(levelname)s in %(module)s: %(message)s')
default_handler = logging.StreamHandler()
default_handler.setFormatter(formatter)

logger = logging.getLogger('lms')
logger.setLevel(logging.DEBUG)
logger.addHandler(default_handler)
