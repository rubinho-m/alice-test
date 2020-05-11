import logging
import json
import os

from flask import Flask, request
from data import db_session
from data.users import User
from images import get_size, upload_image, get_images
from geocoder import get_city_map_url

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

# создаем словарь, в котором ключ — название города,
# а значение — массив, где перечислены id картинок,
# которые мы записали в прошлом пункте.

cities = {
    'москва',
    'нью-йорк',
    'париж'
}

# создаем словарь, где для каждого пользователя
# мы будем хранить его имя
sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    logging.info(f'Response: {response!r}')
    return json.dumps(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']

    # если пользователь новый, то просим его представиться.
    if req['session']['new']:
        session = db_session.create_session()
        res['response']['text'] = '''Привет! Назови свое имя!
Вот кого я уже знаю: ''' + ', '.join(user.name for user in session.query(User).all())
        # создаем словарь в который в будущем положим имя пользователя
        sessionStorage[user_id] = {
            'first_name': None
        }
        session.close()
        return

    # если пользователь не новый, то попадаем сюда.
    # если поле имени пустое, то это говорит о том,
    # что пользователь еще не представился.
    if sessionStorage[user_id]['first_name'] is None:
        # в последнем его сообщение ищем имя.
        first_name = get_first_name(req)
        # если не нашли, то сообщаем пользователю что не расслышали.
        if first_name is None:
            res['response']['text'] = \
                'Не расслышала имя. Повтори, пожалуйста!'
        # если нашли, то приветствуем пользователя.
        # И спрашиваем какой город он хочет увидеть.
        else:
            user = User()
            user.name = first_name
            session = db_session.create_session()
            session.add(user)
            session.commit()
            session.close()
            sessionStorage[user_id]['first_name'] = first_name
            res['response'][
                'text'] = 'Приятно познакомиться, ' \
                          + first_name.title() \
                          + '. Я - Алиса. Какой город хочешь увидеть?'
            # получаем варианты buttons из ключей нашего словаря cities

    # если мы знакомы с пользователем и он нам что-то написал,
    # то это говорит о том, что он уже говорит о городе,
    # что хочет увидеть.
    else:
        # ищем город в сообщении от пользователя
        city = get_city(req)
        try:
            assert city is not None
            if city in cities:  # удаляем город из кнопок-подсказок
                cities.remove(city)
            city_url = get_city_map_url(city)
            result = upload_image(city_url)
            im_id = result['image']['id']
            res['response']['card'] = {}
            res['response']['card']['type'] = 'BigImage'
            res['response']['card']['title'] = f'Это {city}'
            res['response']['card']['image_id'] = im_id
            res['response']['text'] = f'Это {city}'
        except Exception as e:
            res['response']['text'] = 'Первый раз слышу об этом городе. Попробуй еще разок!'
    res['response']['buttons'] = [
        {
            'title': city.title(),
            'hide': True
        } for city in cities
    ]


def get_city(req):
    # перебираем именованные сущности
    for entity in req['request']['nlu']['entities']:
        # если тип YANDEX.GEO то пытаемся получить город(city),
        # если нет, то возвращаем None
        if entity['type'] == 'YANDEX.GEO':
            # возвращаем None, если не нашли сущности с типом YANDEX.GEO
            return entity['value'].get('city', None)


def get_first_name(req):
    # перебираем сущности
    for entity in req['request']['nlu']['entities']:
        # находим сущность с типом 'YANDEX.FIO'
        if entity['type'] == 'YANDEX.FIO':
            # Если есть сущность с ключом 'first_name',
            # то возвращаем ее значение.
            # Во всех остальных случаях возвращаем None.
            return entity['value'].get('first_name', None)


@app.route('/')
def test():
    # return str(get_size())
    # return str(upload_image('https://c7.hotpng.com/preview/53/309/191/pikachu-pixel-art-pikachu.jpg'))
    # return upload_image('http://static-maps.yandex.ru/1.x/?ll=46.034158,51.533103&spn=0.005,0.005&l=map')['image']['id']
    # return str(get_images())
    session = db_session.create_session()
    return ', '.join(user.name for user in session.query(User).all())


if __name__ == '__main__':
    db_session.global_init()
    if "PORT" in os.environ:
        app.run(host='0.0.0.0', port=os.environ["PORT"])
    else:
        app.run(host='127.0.0.1', port=5000)
