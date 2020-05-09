from flask import Flask, request
import logging
import json
import os

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {}

who = 'слон'
obj = 'слона'
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
    global obj, who
    user_id = req['session']['user_id']

    if req['session']['new']:
        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ]
        }
        res['response']['text'] = 'Привет! Купи слона!'
        res['response']['buttons'] = get_suggests(user_id)
        return

    if 'ладно' in req['request']['original_utterance'].lower() or 'куплю' in req['request'][
        'original_utterance'].lower() or 'покупаю' in req['request'][
        'original_utterance'].lower() or 'хорошо' in req['request']['original_utterance'].lower():
        res['response']['text'] = f'{obj} можно найти на Яндекс.Маркете!'

        if who != 'кролик':
            user_id = req['session']['user_id']
            sessionStorage[user_id] = {
                'suggests': [
                    "Не хочу.",
                    "Не буду.",
                    "Отстань!",
                ]
            }
            res['response']['text'] = 'А теперь купи Кролика'
            res['response']['buttons'] = get_suggests(user_id)
            obj = 'кролика'
            who = 'кролик'
            return
        else:
            get_suggests(user_id)
    if end:
        res['response']['text'] = 'Покупка совершена. Деньги списаны с вашего счета'
        res['response']['end_session'] = True
    else:
        res['response']['text'] = \
            f"Все говорят '{req['request']['original_utterance']}', а ты купи {obj}!"
        res['response']['buttons'] = get_suggests(user_id)

    res['response']['text'] = \
        f"Все говорят '{req['request']['original_utterance']}', а ты купи слона!"
    res['response']['buttons'] = get_suggests(user_id)


def get_suggests(user_id):
    global end, who
    session = sessionStorage[user_id]

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
            "url": f"https://market.yandex.ru/search?text={who}",
            "hide": True
        })

    end = True

    return suggests


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
