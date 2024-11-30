import requests

# Функция для загрузки данных из raw ссылок
def fetch_domains(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text.splitlines()

# Функция для удаления дубликатов и оптимизации доменов
def optimize_domains(domains):
    # Убираем пустые строки и комментарии
    cleaned_domains = set(
        domain.strip().split("#", 1)[0].strip()
        for domain in domains
        if domain.strip() and not domain.startswith("#")
    )

    # Сортируем домены в порядке увеличения длины (от самых коротких к самым длинным)
    sorted_domains = sorted(cleaned_domains, key=lambda x: x.count("."))

    # Убираем поддомены, которые покрываются более общими доменами
    optimized_domains = set()
    for domain in sorted_domains:
        if not any(
            domain.endswith(f".{existing}") or domain == existing
            for existing in optimized_domains
        ):
            optimized_domains.add(domain)

    return optimized_domains

# Основной процесс
def main():
    # Список ссылок на файлы
    file_urls = [
        "https://community.antifilter.download/list/domains.lst",
        "https://raw.githubusercontent.com/1andrevich/Re-filter-lists/refs/heads/main/community.lst",
        "https://raw.githubusercontent.com/v2fly/domain-list-community/refs/heads/master/data/youtube"
        # Добавляйте сюда новые URL по необходимости
        # "https://example.com/new_file.lst",
    ]

    # Сбор всех доменов из файлов
    all_domains = []
    for url in file_urls:
        all_domains.extend(fetch_domains(url))

    # Оптимизация доменов
    optimized_domains = optimize_domains(all_domains)

    # Преобразование доменов в формат SwitchyOmega
    switchyomega_format = "#BEGIN\n\n[Wildcard]\n"
    switchyomega_format += "\n".join(f"*://*.{domain}/*" for domain in sorted(optimized_domains))
    switchyomega_format += "\n#END"

    # Вывод результата
    # print(switchyomega_format)

    # Сохранение в файл
    with open("ru-blocked.txt", "w") as file:
        file.write(switchyomega_format)

# Запуск скрипта
if __name__ == "__main__":
    main()
