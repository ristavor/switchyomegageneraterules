import requests

# Функция для загрузки данных из raw ссылок
def fetch_file_content(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text.splitlines()

# Рекурсивная функция для обработки файлов с директивами include
def process_file(url, processed_urls=set()):
    if url in processed_urls:  # Проверяем, чтобы файл не обрабатывался повторно
        return set()

    processed_urls.add(url)
    domains = set()

    lines = fetch_file_content(url)
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):  # Пропускаем пустые строки и комментарии
            continue

        # Убираем комментарии из строки
        if "#" in line:
            line = line.split("#", 1)[0].strip()

        # Если директива include, обрабатываем связанный файл
        if line.startswith("include:"):
            include_file = line.split(":", 1)[1]
            include_url = f"https://raw.githubusercontent.com/v2fly/domain-list-community/refs/heads/master/data/{include_file}"
            domains.update(process_file(include_url, processed_urls))
        else:
            domains.add(line)  # Обычные доменные строки добавляем

    return domains

# Функция для удаления избыточных доменов (убирает поддомены)
def optimize_domains(domains):
    # Сортируем домены в порядке увеличения длины (от самых коротких к самым длинным)
    sorted_domains = sorted(domains, key=lambda x: x.count("."))

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
    # Исходная ссылка на файл
    base_url = "https://raw.githubusercontent.com/v2fly/domain-list-community/refs/heads/master/data/category-ru"

    # Рекурсивная обработка доменов из файла и всех директив include
    all_domains = process_file(base_url)

    # Оптимизация доменов
    optimized_domains = optimize_domains(all_domains)

    # Преобразование доменов в формат SwitchyOmega
    switchyomega_format = "#BEGIN\n\n[Wildcard]\n"
    switchyomega_format += "\n".join(f"*://*.{domain}/*" for domain in sorted(optimized_domains))
    switchyomega_format += "\n#END"

    # Вывод результата
    # print(switchyomega_format)

    # Сохранение в файл
    with open("except-ru.txt", "w") as file:
        file.write(switchyomega_format)

# Запуск скрипта
if __name__ == "__main__":
    main()
