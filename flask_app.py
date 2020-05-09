from flask import Flask, request
import logging
import os
import json

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {}
animal = 'слона'
shop = 'слон'
end = False


@app.route('/post', methods=['POST'])
def main():
    global end
    end = False
    logging.info(f'Request: {request.json!r}')

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(request.json, response)
    logging.info(f'Response:  {response!r}')

    return json.dumps(response)


def handle_dialog(req, res):
    global animal, shop, end
    user_id = req['session']['user_id']
    if req['session']['new']:
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.
        # Запишем подсказки, которые мы ему покажем в первый раз
        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ]
        }
        # Заполняем текст ответа
        res['response']['text'] = f'Привет! Купи {animal}!'
        # Получим подсказки
        res['response']['buttons'] = get_suggests(user_id)
        return
    # Сюда дойдем только, если пользователь не новый,
    # и разговор с Алисой уже был начат
    # Обрабатываем ответ пользователя.
    # В req['request']['original_utterance'] лежит весь текст,
    # что нам прислал пользователь
    # Если он написал 'ладно', 'куплю', 'покупаю', 'хорошо',
    # то мы считаем, что пользователь согласился.
    # Подумайте, всё ли в этом фрагменте написано "красиво"?
    if 'ладно' in req['request']['original_utterance'].lower() or 'куплю' in req['request'][
        'original_utterance'].lower() or 'покупаю' in req['request'][
        'original_utterance'].lower() or 'хорошо' in req['request']['original_utterance'].lower():
        # Пользователь согласился, прощаемся.
        res['response']['text'] = f'{animal} можно найти на Яндекс.Маркете!'
        # res['response']['end_session'] = True
        if shop != 'кролик':
            user_id = req['session']['user_id']
            sessionStorage[user_id] = {
                'suggests': [
                    "Не хочу.",
                    "Не буду.",
                    "Отстань!",
                ]
            }
            # Заполняем текст ответа
            res['response']['text'] = 'А теперь купи Кролика'
            res['response']['buttons'] = get_suggests(user_id)
            # Получим подсказки
            animal = 'кролика'
            shop = 'кролик'
            return
        else:
            get_suggests(user_id)
    # Если нет, то убеждаем его купить слона!
    if end:
        res['response']['text'] = 'Покупка совершена. Деньги списаны с вашего счета!'
        res['response']['end_session'] = True
    else:
        res['response']['text'] = \
            f"Все говорят '{req['request']['original_utterance']}', а ты купи {animal}!"
        res['response']['buttons'] = get_suggests(user_id)


# Функция возвращает две подсказки для ответа.
def get_suggests(user_id):
    global shop, end
    session = sessionStorage[user_id]
    # Выбираем две первые подсказки из массива.
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]
    # Убираем первую подсказку, чтобы подсказки менялись каждый раз.
    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session
    # Если осталась только одна подсказка, предлагаем подсказку
    # со ссылкой на Яндекс.Маркет.
    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": f"https://market.yandex.ru/search?text={shop}",
            "hide": True
        })
    end = True
    return suggests


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
