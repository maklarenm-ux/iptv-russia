
import re
import urllib.request
from pathlib import Path

SOURCE_M3U = "https://free-epg.de/api/playlists/ru.m3u"
EPG_URL = "https://xmltv.live/epg/ru.xml.gz"

OUTPUT = Path("playlist.m3u")

CATEGORIES = {
    "Новости": [
        "news", "новости", "24", "россия 1", "мир 24"
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
        headers={"User-Agent": "Mozilla/5.0 IPTV-Playlist-Builder"}
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

        if not line:
            continue

        if line.startswith("#EXTM3U"):
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

        # Находим URL потока
        stream_urls = [
            line for line in entry
            if line.startswith(("http://", "https://", "rtmp://"))
        ]

        if not stream_urls:
            continue

        stream = stream_urls[-1]

        if stream in seen:
            continue

        seen.add(stream)

        category = classify(extinf)
        extinf = set_group(extinf, category)

        # Сохраняем дополнительные параметры источника
        metadata = [
            line for line in entry[1:]
            if line != stream
        ]

        result.append([extinf] + metadata + [stream])

    if not result:
        raise RuntimeError("Источник не вернул ни одного канала")

    output = [
        "#EXTM3U",
        f'#EXTM3U x-tvg-url="{EPG_URL}"'
    ]

    # Оставляем одну корректную заглавную строку
    output = [
        f'#EXTM3U x-tvg-url="{EPG_URL}"'
    ]

    for entry in result:
        output.extend(entry)

    OUTPUT.write_text(
        "\n".join(output) + "\n",
        encoding="utf-8"
    )

    print(f"Готово! Каналов: {len(result)}")

if __name__ == "__main__":
    main()
