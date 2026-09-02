# -*- coding: utf-8 -*-
"""
utils/generator.py
Основная логика генерации креативов (HTML, PNG, TXT, ZIP)
"""

import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from utils.image_generator import generate_image

# --- Каталог с HTML-шаблонами ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates', 'html_templates')

_jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(['html', 'htm', 'xml'])
)

# Маппинг template_type -> имя файла шаблона
TEMPLATE_MAP = {
    'default': 'default.html',
    'html': 'default.html',
    'billboard': 'billboard.html',
    'fullscreen': 'fullscreen.html',
    'popup': 'popup.html',
    'popup_desktop': 'popup.html',
    'popup_mobile': 'popup.html',
    'popupcontent': 'popup_content.html',
    'popup_content': 'popup_content.html',
    'floatingbillboard': 'floating_billboard.html',
    'floating_billboard': 'floating_billboard.html',
    'showup': 'show_up.html',
    'show-up': 'show_up.html',
    'show_up': 'show_up.html',
    'interscroller': 'interscroller.html',
    'virtualletter': 'virtual_letter.html',
    'virtual_letter': 'virtual_letter.html',
    'виртуальное письмо': 'virtual_letter.html',
    'виртуальноеписьмо': 'virtual_letter.html',
    'письмо': 'virtual_letter.html',
    'servicewidget': 'service_widget.html',
    'service_widget': 'service_widget.html',
    'сервисный виджет': 'service_widget.html',
    'сервисныйвиджет': 'service_widget.html',
    'native': 'default.html',
    'video': 'default.html',
    'carousel': 'carousel.html',
    'stickline': 'sticky_line.html',
    'stickylin': 'sticky_line.html',
    'stickyline': 'sticky_line.html',
    'sticky_line': 'sticky_line.html',
    'superfooter': 'superfooter.html',
    'super_footer': 'superfooter.html',
    'topbanner': 'top_banner.html',
    'top_banner': 'top_banner.html',
}


def resolve_template_file(template_type):
    """Возвращает имя файла шаблона для переданного template_type."""
    if not template_type:
        return 'default.html'
    key = template_type.strip().lower().replace(' ', '')
    key = key.replace('_desktop', '').replace('_mobile', '')
    return TEMPLATE_MAP.get(key, 'default.html')


def render_html(template_type, format_name, width, height, description, link, base_file='base.html'):
    """Рендерит HTML-креатив из шаблона по выбранному типу.
    В HTML всегда остаётся макрос [clickurl_1] (переданная ссылка в HTML не пишется).
    base_file='base.html' — DSP-вариант (фон и размеры на body);
    base_file='base_shot.html' — скриншотный (внутренний контейнер для Selenium)."""
    template_file = resolve_template_file(template_type)
    template = _jinja_env.get_template(template_file)
    return template.render(
        format_name=format_name,
        width=width,
        height=height,
        description=description or f'Размер: {width}×{height}',
        link='[clickurl_1]',
        base_file=base_file,
    )


def resolve_custom_txt_params(template_type, platform, width=None, link=None):
    """
    Возвращает индивидуальные TXT-параметры для спец-шаблонов,
    либо None, если шаблон обычный HTML (нужны стандартные параметры).
    """
    custom_txt_params = {
        "FloatingBillboard": """click_url_mode=true
height=250px
width=100%
content_type=html
show_time=2000
top_offset=0
scroll_element=body
normalize_html=false
button_background_color=#4c4b4e
button_color=white
minimize_banner=false
button_close_mode=true""",
        "Fullscreen": """click_url_mode=true
width=100%
height=100%
header_phrase=До закрытия рекламы осталось
panel_text_color=#FFFFFF
panel_text_family=Roboto
panel_text_family_link=https://fonts.googleapis.com/css?family=Roboto:300,500&subset=cyrillic
timer_banner_show=0
timer_close_show=1000
timer_banner_close=10000
mobile_mode=false
ad_label_content=Реклама""",
        "Interscroller": """click_url_mode=true
width=300px
height=600px
mobile_mode=false
content_1_parallaxScrollRate=10
content_1_parallaxMouseRate=0
content_1_parallaxGyroscopeRate=0
content_1_freeze=both
content_1_normalize_html=false
content_2_parallaxScrollRate=5
content_2_parallaxMouseRate=0
content_2_parallaxGyroscopeRate=0
content_2_freeze=true
content_2_normalize_html=false
content_3_parallaxScrollRate=0
content_3_parallaxMouseRate=0
content_3_parallaxGyroscopeRate=0
content_3_freeze=false
content_3_normalize_html=false
content_4_parallaxScrollRate=0
content_4_parallaxMouseRate=0
content_4_parallaxGyroscopeRate=0
content_4_freeze=false
content_4_normalize_html=false
content_5_parallaxScrollRate=0
content_5_parallaxMouseRate=0
content_5_parallaxGyroscopeRate=0
content_5_freeze=false
content_5_normalize_html=false
ad_label_content=Реклама""",
        "PopUp_Desktop": """click_url_mode=true
width=232px
height=174px
content_cta_color=#FF4800
content_cta_font_color=#FFFFFF
content_title_font_color=#181B22
content_price_font_color=#181B22
timer_banner_close=10000
timer_banner_show=21600
show_in_view_num=2
z_index=9999
background_color=#FFF
normalize_html=false
ad_label_content=Реклама""",
        "PopUp_Mobile": """click_url_mode=true
width=220px
height=162px
content_cta_color=#FF4800
content_cta_font_color=#FFFFFF
content_title_font_color=#181B22
content_price_font_color=#181B22
timer_banner_close=10000
timer_banner_show=21600
show_in_view_num=2
z_index=9999
background_color=#fff
normalize_html=false
ad_label_content=Реклама""",
        "PopUpContent": """click_url_mode=true
width=1032px
height=96px
normalize_html=true
ad_label_content=Реклама
timer_banner_close=100000
show_in_view_num=1
timer_banner_show=10000""",
        "Show-up": """click_url_mode=true
width=232px
height=174px
timer__banner_close=10000
show_in_view_num=2
ad_label_content=Реклама
timer__banner_show=30000""",
        "Виртуальное письмо": """deferred_render=false
normalize_html=false
click_url_mode=true
width=100%
height=100%
virtual_letter__mode=false
allow_access_interface=false
ad_label_content=Реклама""",
    }

    if not template_type:
        return None

    t = template_type.strip().lower()

    if t == "popup":
        return custom_txt_params["PopUp_Mobile" if platform.lower() == "mobile" else "PopUp_Desktop"]

    if t in ("popup_desktop", "popup-desktop", "popupdesktop"):
        return custom_txt_params["PopUp_Desktop"]
    if t in ("popup_mobile", "popup-mobile", "popupmobile"):
        return custom_txt_params["PopUp_Mobile"]

    if t in ("show-up", "showup", "show_up", "show-up"):
        return custom_txt_params["Show-up"]

    if t in ("virtualletter", "virtual_letter", "virtual letter"):
        return custom_txt_params["Виртуальное письмо"]

    if t in ("branding", "branding_desktop", "branding-desktop", "brandingdesktop"):
        click_url = link if link and link.strip() and '[clickurl_1]' not in link else 'https://example.com/branding/'
        return f"""ad_label_content=Реклама
ad_label=true
adv_info=Тестовый баннер РТ
clickurl_1={click_url}
markup_type=default
plane_name=gazeta
click_url_mode=true
center_area_type=html_url
banner_position=absolute
center_area=index.html
normalize_html=true
horizontal_align_by_view=false
fixed_banner_width={width}"""

    # Прямое совпадение с ключами словаря
    for key in custom_txt_params:
        if t == key.lower() or t == key.lower().replace("_", "").replace("-", ""):
            return custom_txt_params[key]

    return None


def generate_creative_files(format_name, width, height, template_type, platform,
                            only_image, description, link, output_dir):
    """
    Создаёт HTML, PNG и TXT-файлы для выбранного формата.

    Аргументы:
        format_name (str): Название формата (например "Billboard 100x250")
        width (str): Ширина (например "100%")
        height (str): Высота (например "250")
        template_type (str): Тип шаблона (billboard, native и т.д.)
        platform (str): Платформа (Desktop, Mobile)
        only_image (bool): Только изображение без HTML
        description (str): Текстовое описание формата
        link (str): Кастомная ссылка для макроса [clickurl_1]
        output_dir (str): Папка для сохранения результата
    """

    # --- Параметры по версии (is_mobile / is_desktop) ---
    is_mobile = "true" if platform.lower() == "mobile" else "false"
    is_desktop = "true" if platform.lower() != "mobile" else "false"
    version_params = f"is_mobile={is_mobile}\nis_desktop={is_desktop}"

    # --- Индивидуальные параметры для спец-шаблонов ---
    custom_params = resolve_custom_txt_params(template_type, platform, width, link)

    # --- Стандартные параметры для обычных HTML ---
    if custom_params is None:
        click_url = link if link and link.strip() and '[clickurl_1]' not in link else 'https://example.com/'
        custom_params = f"""width={width}
height={height}
ad_label_content=Реклама
ad_label=true
adv_info=Тестовый баннер РТ
clickurl_1={click_url}"""

    txt_params = f"{version_params}\n{custom_params}"

    # --- Подготовка путей ---
    safe_name = format_name.replace(" ", "_").replace("/", "_")
    html_path = os.path.join(output_dir, f"{safe_name}.html")
    txt_path = os.path.join(output_dir, f"{safe_name}.txt")

    # --- Всегда создаём HTML (по ТЗ PNG рендерится только из HTML) ---
    html_content = render_html(template_type, format_name, width, height, description, link, base_file='base.html')
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # --- Генерация PNG из скриншотного HTML (отдельная база с контейнером) ---
    shot_html_content = render_html(template_type, format_name, width, height, description, link, base_file='base_shot.html')
    shot_html_path = os.path.join(output_dir, f"{safe_name}.shot.html")
    with open(shot_html_path, "w", encoding="utf-8") as f:
        f.write(shot_html_content)

    try:
        image_path = generate_image(format_name, description, width, height, output_dir, shot_html_path)
    finally:
        # Скриншотный HTML — временный, для выгрузки не нужен
        if os.path.exists(shot_html_path):
            os.remove(shot_html_path)

    # --- Создание TXT с параметрами ---
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(txt_params)

    # --- Возврат списка файлов для упаковки ---
    files = [txt_path, image_path]
    if not only_image:
        files.insert(0, html_path)
    else:
        # Только PNG: HTML создавался временно — убираем из выгрузки
        if os.path.exists(html_path):
            os.remove(html_path)

    return files
