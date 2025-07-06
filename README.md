
## 📦 Установка и запуск

### 🔧 1. Установка зависимостей

```bash
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate на Windows
pip install -r requirements.txt

🚀 2. Запуск через Uvicorn
uvicorn app.main:app --reload
Теперь API доступно по адресу:
http://localhost:8000/docs

🐳 Запуск через Docker
🔨 1. Собрать образ

docker build -t docx-translator .

▶️ 2. Запустить контейнер
docker run -p 8080:8000 --name=translator docx-translator
Теперь API доступно по адресу:
http://localhost:8080/docs

## Timeout увеличил, потому что запрос к API1 долго отрабатывается
## Можете через swagger проверить api, потому что там можно сразу скачивать файл(и перевеод только русский -> казахский:) )
