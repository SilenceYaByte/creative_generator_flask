# -*- coding: utf-8 -*-
# app.py
from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from utils.generator import generate_creative_files
from utils.image_generator import generate_image
import os
import zipfile
import sqlite3
from io import BytesIO

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'formats.db')
GENERATED_DIR = os.path.join(BASE_DIR, 'generated')


# --- Инициализация базы ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS formats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        format_name TEXT NOT NULL,
        width TEXT NOT NULL,
        height TEXT NOT NULL,
        template_type TEXT DEFAULT 'HTML',
        platform TEXT NOT NULL,
        only_image INTEGER DEFAULT 0,
        description TEXT,
        link TEXT
    )''')
    conn.commit()
    conn.close()


# --- Главная страница ---
@app.route('/')
def index():
    query = request.args.get('query', '').strip()
    formats = []

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if query:
        cursor.execute("""
            SELECT * FROM formats
            WHERE format_name LIKE ? OR description LIKE ? OR platform LIKE ?
        """, (f'%{query}%', f'%{query}%', f'%{query}%'))
    else:
        cursor.execute("SELECT * FROM formats")

    formats = cursor.fetchall()
    conn.close()

    if not formats and query:
        flash('Форматы по запросу не найдены.', 'warning')

    return render_template('index.html', formats=formats, query=query)


# --- Добавление нового формата ---
@app.route('/add', methods=['POST'])
def add_format():
    format_name = request.form.get('format_name')
    width = request.form.get('width')
    height = request.form.get('height')
    template_type = request.form.get('template_type', 'HTML')
    platform = request.form.get('platform')
    only_image = 1 if request.form.get('only_image') == 'on' else 0
    description = request.form.get('description', '')
    link = request.form.get('link', '')

    if not format_name or not width or not height:
        flash('Пожалуйста, заполните все обязательные поля.', 'danger')
        return redirect(url_for('index'))

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM formats WHERE format_name=? AND width=? AND height=? AND platform=?
    """, (format_name, width, height, platform))
    if cursor.fetchone():
        conn.close()
        flash('Формат с такими параметрами уже существует!', 'warning')
        return redirect(url_for('index'))

    cursor.execute("""
        INSERT INTO formats (format_name, width, height, template_type, platform, only_image, description, link)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (format_name, width, height, template_type, platform, only_image, description, link))
    conn.commit()
    conn.close()

    flash('Формат успешно добавлен.', 'success')
    return redirect(url_for('index'))


# --- Скачивание одного формата ---
@app.route('/download/<int:format_id>')
def download(format_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM formats WHERE id=?", (format_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        flash('Формат не найден.', 'danger')
        return redirect(url_for('index'))

    format_name, width, height, template_type, platform, only_image, description, link = (
        row[1], row[2], row[3], row[4], row[5], bool(row[6]), row[7], row[8]
    )

    output_dir = GENERATED_DIR
    os.makedirs(output_dir, exist_ok=True)

    files = generate_creative_files(
        format_name, width, height, template_type,
        platform, only_image, description, link, output_dir
    )

    # создаём ZIP архив
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zipf:
        for file_path in files:
            arcname = os.path.basename(file_path)
            zipf.write(file_path, arcname)

    zip_buffer.seek(0)
    return send_file(
        zip_buffer, mimetype='application/zip',
        as_attachment=True, download_name=f'{format_name}.zip'
    )


# --- Удаление формата ---
@app.route('/delete/<int:format_id>', methods=['POST'])
def delete_format(format_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM formats WHERE id=?", (format_id,))
    conn.commit()
    conn.close()
    flash('Формат удалён.', 'info')
    return redirect(url_for('index'))


# --- Скачивание всех форматов ---
@app.route('/download_all')
def download_all():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM formats")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        flash('Нет форматов для выгрузки.', 'warning')
        return redirect(url_for('index'))

    output_dir = GENERATED_DIR
    os.makedirs(output_dir, exist_ok=True)
    all_files = []

    for row in rows:
        format_name, width, height, template_type, platform, only_image, description, link = (
            row[1], row[2], row[3], row[4], row[5], bool(row[6]), row[7], row[8]
        )
        files = generate_creative_files(
            format_name, width, height, template_type,
            platform, only_image, description, link, output_dir
        )
        all_files.extend(files)

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zipf:
        for file_path in all_files:
            arcname = os.path.basename(file_path)
            zipf.write(file_path, arcname)

    zip_buffer.seek(0)
    return send_file(
        zip_buffer, mimetype='application/zip',
        as_attachment=True, download_name='all_creatives.zip'
    )


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5050)
