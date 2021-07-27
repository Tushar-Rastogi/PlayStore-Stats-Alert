import requests


def serve_request(apis):
    response = requests.get(apis)
    print(response.status_code)
    data = response.json()
    for lst in data['data']:
        if 3 < float(lst[1]) < 4:
            print(lst)


if __name__ == '__main__':
    api = "https://ssd-api.jpl.nasa.gov/fireball.api"
    serve_request(api)

