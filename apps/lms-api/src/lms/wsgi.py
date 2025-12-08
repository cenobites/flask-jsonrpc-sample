from __future__ import annotations

from werkzeug.middleware.proxy_fix import ProxyFix

from lms.app import create_app

app = create_app()
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)  # type: ignore[method-assign]
