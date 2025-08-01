# app/http/app.py
from injector import Injector
from internal.router.router import Router
from internal.server.http import Http
import dotenv

injector = Injector()

dotenv.load_dotenv()

app = Http(__name__, router=injector.get(Router))

if __name__ == "__main__":
    app.run(debug=True)
