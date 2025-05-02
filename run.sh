#!/bin/bash
gunicorn -b 127.0.0.1:6000 --timeout 120 "app:create_app()"