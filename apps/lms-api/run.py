from __future__ import annotations

from lms.app import create_app
from lms.infrastructure.database.db import init_db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        init_db(app)
    app.run(host='0.0.0.0', port=5000, debug=True)
