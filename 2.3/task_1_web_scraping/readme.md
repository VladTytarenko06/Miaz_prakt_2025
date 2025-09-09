Ось готовий приклад **README.md** для вашого скрипта:

````markdown
# Ukrinform News Scraper

Цей скрипт призначений для збору заголовків останніх новин з сайту [Укрінформ](https://www.ukrinform.ua/) за допомогою бібліотек **requests** та **BeautifulSoup**.

## Можливості
- Отримання заголовків новин зі сторінки "Останні новини".
- Збереження результатів у файл `news_titles.csv` (колонки: заголовок, посилання).
- Можливість вказати кількість сторінок для збору новин.

## Вимоги
Перед запуском встановіть необхідні бібліотеки:
```bash
pip install requests beautifulsoup4
````

## Використання

### У Jupyter Notebook

1. Імпортуйте функцію `get_latest_headlines` із скрипта.
2. Виконайте код:

   ```python
   headlines = get_latest_headlines(n_pages=1)

   import csv
   with open("news_titles.csv", "w", newline="", encoding="utf-8") as f:
       writer = csv.DictWriter(f, fieldnames=["title", "url"])
       writer.writeheader()
       writer.writerows(headlines)
   ```
3. У результаті буде створено файл `news_titles.csv` з останніми заголовками.

### У вигляді окремого скрипта

Запустіть:

```bash
python scraper.py
```

## Приклад результату (CSV)

```csv
title,url
"Президент України провів зустріч з прем'єр-міністром ...","https://www.ukrinform.ua/rubric-politycs/1234567-prezident.html"
"В Україні оновлено дані щодо безпекової ситуації","https://www.ukrinform.ua/rubric-ato/7654321-v-ukraini.html"
```

---

✍️ Автор: *ваше ім’я або нік*

```

---

Хочете, я одразу згенерую цей файл `README.md` і віддам вам готовим завантаженням, щоб додати у ваш проект поряд із `scraper.ipynb`?
```
