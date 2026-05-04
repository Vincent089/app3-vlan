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
from flask import Flask, jsonify
from app.api import vlans_bp, cores_bp, vlan_ranges_bp
from app.db import SessionLocal, init_db
from common.execptions import DomainError

init_db()
app = Flask(__name__)


@app.teardown_appcontext
def shutdown_session(exception=None):
    SessionLocal.remove()


@app.errorhandler(DomainError)
def handle_domain_error(e):
    return jsonify({ "error": str(e) }), e.status_code


app.register_blueprint(vlans_bp, url_prefix="/vlans")
app.register_blueprint(cores_bp, url_prefix="/cores")
app.register_blueprint(vlan_ranges_bp, url_prefix="/vlanranges")

if __name__ == "__main__":
    app.run(debug=True)
