import os

dbconfig = {
    "host": os.environ.get('NEON_HOST'),
    "username": os.environ.get('NEON_USERNAME'),
    "password": os.environ.get('NEON_PASSWORD'),
    "database": os.environ.get('NEON_DATABASE'),
    "port": os.environ.get('NEON_PORT')
}