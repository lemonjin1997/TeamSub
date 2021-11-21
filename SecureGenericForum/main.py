from re import L
import time

from app.api import api_blueprint
from app.app import app, db
from app.setup import setup, init_db, setup_dummy_data, setup_default_user

app.register_blueprint(api_blueprint)


def main():
    print("Setting up.")
    init_db(db)
    setup(db.session)
    setup_default_user(db.session)
    if app.config['TESTING'] == True:
        setup_dummy_data(db.session)

    print("Done.")
    print("Starting server.")
    print(app.url_map)


if __name__ == '__main__':  # running without wsgi
    main()
    app.run(host='0.0.0.0', port='5000')
else:  # running with wsgi/gunicorn
    main()
