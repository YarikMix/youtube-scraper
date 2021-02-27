# -*- coding: utf-8 -*-
import time

import requests
import json
import openpyxl
import yaml
from pytils import numeral
from pathlib import Path
from tqdm import tqdm

from functions import *


BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR.joinpath("config.yaml")
DATA_DIR = BASE_DIR.joinpath("Data")

with open(CONFIG_PATH) as ymlFile:
    config = yaml.load(ymlFile.read(), Loader=yaml.Loader)


class YTParser:
    def __init__(self, api_key, channel_title):
        self.api_key = api_key
        self.domain = "https://www.googleapis.com/youtube/v3"
        self.channel_title = channel_title
        self.channel_id = None
        self.channel_statistics = None
        self.video_data = []

    def extract_all(self):
        self.get_channel_statistics()
        self.get_channel_video_data(50)

    def get_channel_statistics(self):
        """Получаем статистику ютуб канала"""
        url = f"{self.domain}/channels?part=statistics&id={self.channel_id}&key={self.api_key}"
        response = requests.get(url)
        data = json.loads(response.text)
        try:
            raw_data = data["items"][0]["statistics"]
            data = {
                "Количество просмотров": raw_data["viewCount"],
                "Количество подписчиков": raw_data["subscriberCount"],
                "Количество видео": raw_data["videoCount"]
            }

        except:
            data = None

        self.channel_statistics = data

    def get_channel_video_data(self, limit=None):
        """Получаем информацию о видео ютуб канала"""
        self.videos_ids = []  # Список с id видео с канала
        url = f"{self.domain}/search?key={self.api_key}&channelId={self.channel_id}&id&order=date"
        if limit is not None and isinstance(limit, int):
            url += f"&maxResults={limit}"

        next_page_token = self._get_channel_videos_per_page(url)
        total_pages = 0  # Количество запросов, в каждом запросе получаем по 50 видео
        while next_page_token is not None and total_pages < 2:
            next_url = f"{url}&pageToken={next_page_token}"
            next_page_token = self._get_channel_videos_per_page(next_url)
            total_pages += 1

        # Обрабатываем каждое видео из списка
        for video_id in tqdm(self.videos_ids):
            self._get_single_video_data(video_id)

    def _get_channel_videos_per_page(self, url):
        response = requests.get(url)
        data = json.loads(response.text)

        items = data["items"]
        nextPageToken = data.get("nextPageToken", None)
        for item in items:
            kind = item["id"]["kind"]
            if kind == "youtube#video":
                video_id = item["id"]["videoId"]
                self.videos_ids.append(video_id)

        return nextPageToken

    def _get_single_video_data(self, video_id):
        """Получаем информацию о видео по его id"""
        url = f"{self.domain}/videos?part=snippet,statistics,contentDetails&id={video_id}&key={self.api_key}"
        response = requests.get(url)
        data = json.loads(response.text)

        raw_data = data["items"][0]

        self.video_data.append(
            {
                "ID": raw_data["id"],
                "Название": raw_data["snippet"]["title"],
                "Длительность": get_video_duration(raw_data["contentDetails"]["duration"]),
                "Опубликовано": get_video_release_date(raw_data["snippet"]["publishedAt"]),
                "Статистика": {
                    "Количество просмотров": raw_data["statistics"]["viewCount"],
                    "Количество лайков": raw_data["statistics"]["likeCount"],
                    "Количество дизлайков": raw_data["statistics"]["dislikeCount"],
                    "Количество комментариев": raw_data["statistics"]["commentCount"]
                },
                "Описание": raw_data["snippet"]["description"],
                "Превью": get_last_value(raw_data["snippet"]["thumbnails"])["url"]
            }
        )

    def _get_channel_info(self, title):
        """Возвращает id и название ютуб канала"""
        query = title.lower().replace(" ", "+")
        url = f"{self.domain}/search?part=snippet&key={self.api_key}&q={query}"
        response = requests.get(url)
        data = json.loads(response.text)

        try:
            items = data["items"]
            for item in items:
                kind = item["id"]["kind"]
                if kind == "youtube#channel":
                    id = item["id"]["channelId"]
                    title = item["snippet"]["title"]
                    return id, title
            # Если не нашлось канала с таким названием
            print("Канал с таким названием не найден")
        except:
            if data["error"]["code"] == 403:
                print("Квота превышена :(")
        return None

    def write_excel(self, file_name):
        """Создаём xlsx файл и заполняем его данными из json файла"""
        with open(f"{file_name}.json", encoding="utf-8") as f:
            data = json.load(f)

        book = openpyxl.Workbook()
        sheet = book.active

        sheet["A1"] = "ID"
        sheet["B1"] = "Название"
        sheet["C1"] = "Длительность"
        sheet["D1"] = "Опубликовано"
        sheet["E1"] = "Просмотров"
        sheet["F1"] = "Лайков"
        sheet["G1"] = "Дизлайков"
        sheet["H1"] = "Комментариев"

        for row, video in enumerate(data.popitem()[1]["Видео"], start=2):
            id = video["ID"]
            title = video["Название"]
            duration = video["Длительность"]
            published = video["Опубликовано"]
            views_count = video["Статистика"]["Количество просмотров"]
            likes_count = video["Статистика"]["Количество лайков"]
            dislikes_count = video["Статистика"]["Количество дизлайков"]
            comments_count = video["Статистика"]["Количество комментариев"]

            sheet[row][0].value = id
            sheet[row][1].value = title
            sheet[row][2].value = duration
            sheet[row][3].value = published
            sheet[row][4].value = views_count
            sheet[row][5].value = likes_count
            sheet[row][6].value = dislikes_count
            sheet[row][7].value = comments_count

        book.save(f"{file_name}.xlsx")
        book.close()

    def dump(self):
        fused_data = {
            self.channel_title: {
                "Статистика": self.channel_statistics,
                "Видео": self.video_data
            }
        }
        file_name = self.channel_title.replace(" ", "_").lower()
        file_path = self.CHANNEL_DATA_DIR.joinpath(file_name)
        # Печатаем json файл
        write_json(
            file_name=file_path,
            data=fused_data
        )
        # Печатаем excel файл
        self.write_excel(file_path)

    def main(self):
        # Создаём папку Data, если её нет
        if not DATA_DIR.exists():
            DATA_DIR.mkdir()

        # Получаем id и название канала
        channel_info = self._get_channel_info(title=self.channel_title)
        if channel_info != None:
            time_start = time.time()
            print("Собираем данные")

            self.channel_id, self.channel_title = channel_info

            self.CHANNEL_DATA_DIR = DATA_DIR.joinpath(self.channel_title)
            # Создаём папку с данными о канале, если её нет
            if not self.CHANNEL_DATA_DIR.exists():
                self.CHANNEL_DATA_DIR.mkdir()

            # Собираем данные
            self.extract_all()

            # Печатаем данные
            self.dump()

            time_finish = time.time()

            print("Данные о канале '{}' собраны за {}".format(
                self.channel_title,
                numeral.get_plural(
                    round(time_finish - time_start),
                    "секунду, секунды, секунд"
                )
            ))


if __name__ == "__main__":
    channel_title = input("Введите название канала\n> ")
    parser = YTParser(
        api_key=config["api_key"],
        channel_title=channel_title
    )

    parser.main()