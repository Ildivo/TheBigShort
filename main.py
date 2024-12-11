# main.py
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import random
import string

from database import SessionLocal, init_db
from models import URLMapping

# Инициализация FastAPI приложения
app = FastAPI()

# Инициализация базы данных
init_db()

# Настроим Jinja2 шаблоны
templates = Jinja2Templates(directory="templates")

# Отдаем статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def generate_short_url(length=6):
    """Функция для генерации короткой ссылки из случайных символов"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def validate_and_format_url(url: str) -> str:
    """Функция для проверки и добавления префикса http://"""
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url
    return url


@app.get("/")
def home(request: Request):
    """Главная страница с формой для сокращения ссылки"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/shorten/")
async def shorten_url(request: Request, db: Session = Depends(get_db)):
    """Маршрут для создания короткой ссылки"""
    form_data = await request.form()  # Используем await внутри асинхронной функции
    original_url = form_data.get('url')

    # Преобразуем URL, если не указан префикс
    original_url = validate_and_format_url(original_url)

    # Проверяем, не существует ли уже такая короткая ссылка
    existing_mapping = db.query(URLMapping).filter(URLMapping.original_url == original_url).first()
    if existing_mapping:
        return templates.TemplateResponse("result.html", {
            "request": request,
            "short_url": existing_mapping.short_url,
            "original_url": original_url
        })

    # Генерируем уникальную короткую ссылку
    short_url = generate_short_url()

    # Сохраняем в базе данных
    db.add(URLMapping(original_url=original_url, short_url=short_url))
    db.commit()

    return templates.TemplateResponse("result.html", {
        "request": request,
        "short_url": short_url,
        "original_url": original_url
    })


@app.get("/{short_url}")
def redirect_url(short_url: str, db: Session = Depends(get_db)):
    """Маршрут для перенаправления на оригинальную ссылку"""
    # Ищем оригинальную ссылку по короткой
    mapping = db.query(URLMapping).filter(URLMapping.short_url == short_url).first()

    if mapping is None:
        raise HTTPException(status_code=404, detail="Short URL not found")

    # Перенаправляем на оригинальный URL
    return RedirectResponse(mapping.original_url)
