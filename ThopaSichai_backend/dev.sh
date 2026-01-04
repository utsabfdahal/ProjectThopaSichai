#!/bin/bash
# Run Django development server using uv
exec uv run python manage.py runserver 0.0.0.0:8000 "$@"
