# leave-vk: Уходите из Vk

Сейчас в VK лучше не находиться. Слишком много ненужных людей могут читать вашу переписку и обижать вас за ваш контент. А у нас в ВК паблики!

Этот скрипт сделает полный бекап вашего паблика, сохранит все данные в .json, скачает картинки, и отрендерит все посты в Markdown.

Альфа-версия. Я думаю сделать маленький сервис, который будет помогать людям скачивать паблики и выкладывать их онлайн. (Например, прямо в эту репу – и потом на GitHub Pages) А пока вот, скрипт.

Автор: @valyagolev, http://t.me/roguelike_theory

Получите токен VK: https://vk.com/apps?act=manage. Поставьте `pipenv`. Потом:

    $ git clone https://github.com/valyagolev/leave-vk
    $ cd leave-vk
    $ pipenv install
    $ pipenv shell
    $ TOKEN=(ваш сервис токен) python leave_vk.py https://vk.com/roguelike_theory

Не стесняйтесь помочь с функционалом ;-)

Лицензия: GNU GPL v3.0

Pull Requests: Принимаются!
