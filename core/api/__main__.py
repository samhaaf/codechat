import uvicorn

from .config import Config

if Config.ENVIRONMENT == 'local':
    uvicorn.run('api.app:app', host="127.0.0.1", port=2345, reload=True)
else:
    print('env', Config.ENVIRONMENT)
    uvicorn.run('api.app:app', host="0.0.0.0", port=2345)
