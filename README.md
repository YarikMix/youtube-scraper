## Скрипт, собирающий информацию о ютуб канале

### Как использовать

Скачиваем зависимости
```bash
pip3 install -r requirements.txt
```

В файл config.yaml вписываем ключ для работы с YouTube API
```bash
domain: "https://www.googleapis.com/youtube/v3"
api_key: ""  # Ваш ключ для доступа к YouTube API
```
Гайд, [как получить ключ](https://www.youtube.com/watch?v=th5_9woFJmk&t=1090s&ab_channel=CoreySchafer)

Запускаем скрипт:
```bash
python YouTube-Scraper/main.py
```

Вводим название ютуб канала
```bash
Введите название канала
> Папич
```

Скрипт начнёт собирать данные о канале. Это займёт не более минуты
```bash
Собираем данные
100%|██████████| 149/149 [00:21<00:00,  6.87it/s]
Данные о канале 'Лучшее с Папичем' собраны за 23 секунды
```

По окончанию работы скрипта, в папка Data будет лежать папка с собранной информацией
<br>
![](https://github.com/YarikMix/YouTube-Scraper/raw/main/images/1.png)