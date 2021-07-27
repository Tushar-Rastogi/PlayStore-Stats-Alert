import os
from google.cloud import bigquery
from matplotlib import pyplot as py


def __plot__(title, x, y):
    # Plot Graph
    py.plot(x, y)
    py.title(title)
    py.legend()
    py.xlabel('Date')
    py.xticks(rotation=60)
    py.ylabel('Count')


# Perform a query.
def perform_query():
    client = bigquery.Client()
    QUERY = (
        'SELECT '
        'COUNT(DISTINCT event_id) AS number_of_crashes, '
        'FORMAT_TIMESTAMP("%F", event_timestamp) AS date_of_crashes '
        'FROM '
        'paytm-app-layer.firebase_crashlytics.net_one97_paytm_ANDROID '
        'GROUP BY '
        'date_of_crashes '
        'ORDER BY '
        'date_of_crashes DESC '
        'LIMIT 30')
    query_job = client.query(QUERY)  # API request
    rows = query_job.result()  # Waits for query to finish
    crashes = []
    dates = []
    for crash, date in rows:
        crashes.append(crash)
        dates.append(date)
    __plot__("Tile", dates, crashes)


if __name__ == '__main__':
    os.environ[
        "GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/tusharrastogi/PycharmProjects/GooglePlayData/key_bqservice.json"
    print('Credendtials from environ: {}'.format(
        os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')))
    perform_query()
    py.show()
