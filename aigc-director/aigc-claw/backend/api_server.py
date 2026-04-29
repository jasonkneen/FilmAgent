# -*- coding: utf-8 -*-
"""Compatibility entrypoint for the AIGC-Claw FastAPI server.

The application is organized under the ``api`` package following the
Pixelle-Video router/schema layout, while this file keeps the historical
``python api_server.py`` startup command working.
"""

import os
import sys

_backend_dir = os.path.dirname(os.path.abspath(__file__))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

import uvicorn

from api.app import app
from config import settings


def main():
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)


if __name__ == "__main__":
    main()
