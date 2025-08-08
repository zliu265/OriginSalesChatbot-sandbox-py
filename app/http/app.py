# app/http/app.py
from pkg.sqlalchemy import SQLAlchemy
from injector import Injector
from internal.router.router import Router
from internal.server.http import Http
from .module import ExtensionModule
from config import Config
import dotenv
from flask_migrate import Migrate

injector = Injector([ExtensionModule])

conf = Config()

dotenv.load_dotenv()

app = Http(
    __name__,
    conf=conf,
    db=injector.get(SQLAlchemy),
    migrate=injector.get(Migrate),
    router=injector.get(Router)
)

if __name__ == "__main__":
    app.run(debug=True)

#python -m app.http.app