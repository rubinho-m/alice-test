import requests


def get_city_map_url(city):
    geocoder_uri = "http://geocode-maps.yandex.ru/1.x/"
    response = requests.get(geocoder_uri, params={
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "format": "json",
        "geocode": city
    })

    toponym = response.json()["response"]["GeoObjectCollection"][
        "featureMember"][0]["GeoObject"]
    ll = ','.join(toponym["Point"]["pos"].split(" "))

    return f"http://static-maps.yandex.ru/1.x/?ll={ll}&spn=0.005,0.005&l=map"


if __name__ == '__main__':
    print(get_city_map_url('Саратов'))