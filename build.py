
import re
import urllib.request
from pathlib import Path

SOURCE_M3U = "https://iptv-org.github.io/iptv/countries/ru.m3u"
EPG_URL = "https://xmltv.live/epg/ru.xml.gz"

OUTPUT = Path("playlist.m3u")

# Дополнительные каналы
CUSTOM_CHANNELS = [
    {
        "name": "ТНТ",
        "id": "TNT.ru",
        "url": "http://stream.mcquack.net/135/index.m3u8",
        "group": "Россия | Развлечения"
    },
    {
        "name": "ТНТ Премьера",
        "id": "TNT-PREMIERA.ru",
        "url": "http://31.148.5.241/kanal_19/index.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/4/43/%D0%A2%D0%9D%D0%A2-Premier.png",
        "group": "Россия | Развлечения"
    },
    {
        "name": "Мосфильм золотая коллекция",
        "id": "MosfilmGoldCollection.ru@SD",
        "url": "http://stream.mcquack.net/369/index.m3u8",
        "logo": "https://i.imgur.com/95Y8jb6.png",
        "group": "Россия | Кино и сериалы"
    }
]

CATEGORIES = {
    "Новости": [
        "news", "новости", "24"
    ],
    "Кино и сериалы": [
        "cinema", "movie", "film", "кино", "сериал"
    ],
    "Спорт": [
        "sport", "спорт", "футбол", "хоккей"
    ],
    "Музыка": [
        "music", "музыка", "муз"
    ],
    "Детские": [
        "kids", "children", "дет", "мульт"
    ],
    "Развлечения": [
        "entertainment", "развлеч", "шоу"
    ],
}


def download(url):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read().decode("utf-8-sig")


def classify(extinf):
    value = extinf.lower()

    for category, words in CATEGORIES.items():
        if any(word in value for word in words):
            return category

    return "Разное"


def set_group(extinf, group):
    pattern = r'group-title="[^"]*"'

    if re.search(pattern, extinf):
        return re.sub(
            pattern,
            f'group-title="{group}"',
            extinf,
            count=1
        )

    if "," in extinf:
        return extinf.replace(
            ",",
            f' group-title="{group}",',
            1
        )

    return extinf


def main():
    source = download(SOURCE_M3U)
    lines = source.splitlines()

    entries = []
    current = []

    for line in lines:
        line = line.strip()

        if not line or line.startswith("#EXTM3U"):
            continue

        if line.startswith("#EXTINF:"):
            if current:
                entries.append(current)
            current = [line]

        elif current:
            current.append(line)

    if current:
        entries.append(current)

    result = []
    seen = set()

    for entry in entries:
        extinf = entry[0]

        # Не дублируем добавленные вручную каналы
        if "tnt.ru" in extinf.lower() or "mosfilmgoldcollection.ru" in extinf.lower():
            continue

        streams = [
            line for line in entry
            if line.startswith(("http://", "https://"))
        ]

        if not streams:
            continue

        stream = streams[-1]

        if stream in seen:
            continue

        seen.add(stream)

        if "ntvseries.ru@sd" in extinf.lower():
            extinf = re.sub(r',.*

        metadata = [
            line for line in entry[1:]
            if line != stream
        ]

        result.append([extinf] + metadata + [stream])

    # Добавляем ТНТ и ТНТ Премьеру
    for channel in CUSTOM_CHANNELS:
        if channel["url"] in seen:
            continue

        extinf = (
            f'#EXTINF:-1 tvg-id="{channel["id"]}" '
            f'tvg-name="{channel["name"]}" '
            + (f'tvg-logo="{channel["logo"]}" ' if channel.get("logo") else "")
            + f'group-title="{channel["group"]}",'
            f'{channel["name"]}'
        )

        result.append([extinf, channel["url"]])
        seen.add(channel["url"])

    if not result:
        raise RuntimeError("Список каналов пуст!")

    output = [
        f'#EXTM3U x-tvg-url="{EPG_URL}"'
    ]

    for entry in result:
        output.extend(entry)

    OUTPUT.write_text(
        "\n".join(output) + "\n",
        encoding="utf-8"
    )

    print("IPTV обновлён!")
    print(f"Всего каналов: {len(result)}")
    print("Добавлены: ТНТ и ТНТ Премьера")


if __name__ == "__main__":
    main()
, ',НТВ сериал', extinf)
            category = "Кино и сериалы"
        else:
            category = classify(extinf)

        extinf = set_group(
            extinf,
            "Россия | " + category
        )

        metadata = [
            line for line in entry[1:]
            if line != stream
        ]

        result.append([extinf] + metadata + [stream])

    # Добавляем ТНТ и ТНТ Премьеру
    for channel in CUSTOM_CHANNELS:
        if channel["url"] in seen:
            continue

        extinf = (
            f'#EXTINF:-1 tvg-id="{channel["id"]}" '
            f'tvg-name="{channel["name"]}" '
            + (f'tvg-logo="{channel["logo"]}" ' if channel.get("logo") else "")
            + f'group-title="{channel["group"]}",'
            f'{channel["name"]}'
        )

        result.append([extinf, channel["url"]])
        seen.add(channel["url"])

    if not result:
        raise RuntimeError("Список каналов пуст!")

    output = [
        f'#EXTM3U x-tvg-url="{EPG_URL}"'
    ]

    for entry in result:
        output.extend(entry)

    OUTPUT.write_text(
        "\n".join(output) + "\n",
        encoding="utf-8"
    )

    print("IPTV обновлён!")
    print(f"Всего каналов: {len(result)}")
    print("Добавлены: ТНТ и ТНТ Премьера")


if __name__ == "__main__":
    main()
