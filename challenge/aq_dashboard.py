'''OpenAQ Air Quality Dashboard with Flask'''
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import openaq  # why does this import have an error message?

# set up API object - is this correct?
api = openaq.OpenAQ()

# create flask application
app = Flask(__name__)

# database stuff - does ordering matter?
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
DB = SQLAlchemy(app)


def get_results():
    # retrieve data from API
    _, body = api.measurements(city='Los Angeles', parameter='pm25')
    results = []
    for item in body['results']:
        utc_datetime = item['date']['utc']
        value = item['value']
        results.append((utc_datetime, value))
    return results


@app.route('/')
def root():
    # body = str(get_results())
    return str(Record.query.filter(Record.value >= 18).all())


class Record(DB.Model):
    # id (integer, primary key)
    id = DB.Column(DB.Integer, primary_key=True, autoincrement=True)
    # datetime (string)
    datetime = DB.Column(DB.String)
    # value (float, cannot be null)
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        # write a nice representation of a record
        return (
            f'Record(id={self.id}, '
            f'datetime={self.datetime}, '
            f'value={self.value})'
        )


@app.route('/refresh')
def refresh():
    """Pull fresh data from Open AQ and replace existing data."""
    DB.drop_all()
    DB.create_all()
    # get data from OpenAQ
    db_access = get_results()
    # make Record objects with it
    db_entry = [Record(
        datetime=item[0],
        value=item[1])
        for item in db_access
    ]
    # and add to db
    DB.session.add_all(db_entry)

    DB.session.commit()

    return 'Data refreshed!'
