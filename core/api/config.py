import os

class Config:
    ENVIRONMENT=os.environ['ENVIRONMENT']
    JWT_SECRET=os.environ['JWT_SECRET']
    DATABASE_HOST=os.environ['DATABASE_HOST']
    DATABASE_PORT=os.environ['DATABASE_PORT']
    DATABASE_USER=os.environ['DATABASE_USER']
    DATABASE_PASS=os.environ['DATABASE_PASS']
    DATABASE_NAME=os.environ['DATABASE_NAME']
