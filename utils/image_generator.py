# -*- coding: utf-8 -*-
"""
utils/image_generator.py
Создание PNG изображения из HTML (скриншот контейнера точного размера).
"""

import os
import time
import numpy as np
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Путь к Chrome (если Selenium не находит автоматически)
CHROME_BINARY = r"C:\Program Files\Google\Chrome\Application\chrome.exe"


def _parse_dimension(value, default):
    """Преобразует '100%', '250px', '300' в пиксели; для % берём default."""
    try:
        if isinstance(value, str) and "%" in value:
            return default
        return int(str(value).replace("px", "").strip())
    except Exception:
        return default


def _get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--hide-scrollbars")
    if os.path.exists(CHROME_BINARY):
        options.binary_location = CHROME_BINARY

    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )


def generate_image(format_name, description, width, height, output_dir, html_path=None):
    """
    Делает PNG-скриншот контейнера .background-container из HTML.
    Размер PNG ровно width x height (в пикселях, из базы).

    Если PNG уже существует и новее HTML — пропускаем рендер (оптимизация).
    """
    width_px = _parse_dimension(width, 600)
    height_px = _parse_dimension(height, 400)

    safe_name = format_name.replace(" ", "_").replace("/", "_")
    image_path = os.path.join(output_dir, f"{safe_name}.png")

    # Оптимизация: не пересоздаём PNG, если он уже существует и не устарел
    if html_path and os.path.exists(html_path) and os.path.exists(image_path):
        if os.path.getmtime(image_path) >= os.path.getmtime(html_path):
            return image_path

    # PNG создаётся только из HTML (по ТЗ)
    if not html_path or not os.path.exists(html_path):
        img = _generate_gradient(width_px, height_px, format_name, description)
        img.save(image_path)
        return image_path

    driver = _get_driver()

    try:
        # Открываем окно с запасом, чтобы контейнер не обрезался
        driver.set_window_size(width_px + 200, height_px + 200)
        driver.get(f"file:///{os.path.abspath(html_path)}")

        # Жёстко задаём контейнеру точный размер (ширина может быть % в шаблоне)
        driver.execute_script(
            "var c = document.querySelector('.background-container');"
            "if (c) { c.style.width = arguments[0] + 'px'; c.style.height = arguments[1] + 'px'; }",
            width_px, height_px
        )
        # Пересчитываем автоподгонку текста под новый размер
        driver.execute_script("if (window.__fitText) window.__fitText();")

        # Ждём, пока JS автоподгонки текста пометит контейнер как готовый
        try:
            WebDriverWait(driver, 15).until(
                lambda d: d.execute_script(
                    "return document.body.getAttribute('data-rendered') === '1';"
                )
            )
        except Exception:
            time.sleep(1.0)

        try:
            container = driver.find_element(By.CSS_SELECTOR, ".background-container")
            png_data = container.screenshot_as_png
        except Exception:
            png_data = driver.get_screenshot_as_png()

        with open(image_path, "wb") as f:
            f.write(png_data)

    finally:
        driver.quit()

    return image_path


def _generate_gradient(width, height, format_name, description):
    """Фолбэк — если HTML отсутствует, создаём градиент вручную."""
    from PIL import ImageDraw, ImageFont

    gradient = np.zeros((height, width, 3), dtype=np.uint8)
    for y in range(height):
        ratio = y / height
        r = int(9 + (29 - 9) * ratio)
        g = int(35 + (135 - 35) * ratio)
        b = int(48 + (106 - 48) * ratio)
        gradient[y, :, :] = (r, g, b)

    img = Image.fromarray(gradient)
    draw = ImageDraw.Draw(img)

    try:
        font_big = ImageFont.truetype("arial.ttf", 28)
        font_small = ImageFont.truetype("arial.ttf", 18)
    except IOError:
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()

    text_lines = [format_name, description or f"{width}x{height}"]
    y_text = height // 2 - 20
    for line in text_lines:
        text_width, text_height = draw.textbbox((0, 0), line, font=font_big)[2:]
        x_text = (width - text_width) / 2
        draw.text((x_text, y_text), line, font=font_big, fill=(255, 255, 255))
        y_text += text_height + 8

    return img
