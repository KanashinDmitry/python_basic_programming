import json
import sqlite3
import requests

from flask import Flask, g
from flask_cors import CORS
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError

app = Flask(__name__)
CORS(app)

DATABASE = 'my_database.sqlite'


def get_db():
    db_conn = getattr(g, '_database', None)
    if db_conn is None:
        db_conn = g._database = sqlite3.connect(DATABASE)
    return db_conn


def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.executescript(
            """CREATE TABLE IF NOT EXISTS Rankings
               (position integer primary key
               , team text not null
               , logo text not null
               , players text not null
               , diff text not null
               , points text not null)"""
        )

        db.commit()


def add_data_db():
    with app.app_context():
        db = get_db()
        parse_html("https://www.hltv.org/ranking/teams")
        db.commit()


def request_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
    else:
        return response.content


def parse_html(url):
    page_cont = request_url(url)
    soup = BeautifulSoup(page_cont, 'html.parser')
    for team in soup.find_all('div', class_="ranked-team"):
        team_name = team.find('span', class_="name").text
        logo = team.find('img')['src']
        position = team.find('span', class_="position").text
        players = ', '\
                  .join([player.text for player
                         in team.find_all('div', class_="rankingNicknames")])
        points = team.find('span', class_="points").text
        diff = team.find('div', {"class": ["change positive", "change negative"]})
        diff = "no difference" if diff is None else diff.text
        cursor = get_db().cursor()
        cursor.execute('''  INSERT OR REPLACE INTO
                            Rankings(position, team, logo, players, diff, points)
                            VALUES(?, ?, ?, ?, ?, ?)''',
                       (int(position[1:]), team_name, logo, players, diff, points[1:-1]))
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/get_all')
def get_all():
    db_cursor = get_db().cursor()
    db_cursor.row_factory = sqlite3.Row
    db_cursor.execute("SELECT * From Rankings")
    result = db_cursor.fetchall()
    json_result = json.dumps([dict(row) for row in result])
    return json_result


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


if __name__ == '__main__':
    init_db()
    add_data_db()
    app.run()
