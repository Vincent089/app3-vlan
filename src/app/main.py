#   -----------------------------------------------------------------------------
#  Copyright (c) 2026. Vincent Corriveau (vincent.corriveau89@gmail.com)
#
#  Licensed under the MIT License. You may obtain a copy of the License at
#  https://opensource.org/licenses/MIT
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  -----------------------------------------------------------------------------
from flask import Flask
from app.api import vlans_bp, cores_bp
from app.db import SessionLocal, init_db

init_db()
app = Flask(__name__)


@app.teardown_appcontext
def shutdown_session(exception=None):
    SessionLocal.remove()


app.register_blueprint(vlans_bp, url_prefix="/vlans")
app.register_blueprint(cores_bp, url_prefix="/cores")

if __name__ == "__main__":
    app.run(debug=True)
