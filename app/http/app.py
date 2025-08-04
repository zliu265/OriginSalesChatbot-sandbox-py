# app/http/app.py
from injector import Injector
from internal.router.router import Router
from internal.server.http import Http
from config import Config
import dotenv

injector = Injector()

conf = Config()

dotenv.load_dotenv()

app = Http(__name__,conf=conf, router=injector.get(Router))

if __name__ == "__main__":
    app.run(debug=True)
