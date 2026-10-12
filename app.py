# -*- coding: utf-8 -*-
"""Сайт «Третий возраст».

Запуск:
    python app.py

После запуска откройте в браузере адрес http://127.0.0.1:5000
"""

from datetime import datetime
from threading import Lock

from flask import (Flask, abort, flash, redirect, render_template, request,
                   url_for)

import content

app = Flask(__name__)
app.config["SECRET_KEY"] = "tretiy-vozrast-2026"

# ---------------------------------------------------------------------------
# Форум. Данные хранятся в памяти: они живут, пока работает сервер.
# ---------------------------------------------------------------------------
forum_lock = Lock()
forum_topics = []
topic_counter = 0


def _seed_forum():
    """Стартовые темы, чтобы форум не выглядел пустым."""
    global topic_counter
    seeds = [
        {
            "title": "Как вы начинаете утро?",
            "category": "health",
            "author": "Валентина",
            "message": "Делюсь своей привычкой: стакан воды, десять минут "
                       "растяжки и прогулка. А что помогает проснуться вам?",
            "replies": [
                {"author": "Николай", "message": "Я делаю зарядку под радио "
                                                 "и очень доволен!", "time": "2 ч назад"},
            ],
            "time": "3 ч назад",
        },
        {
            "title": "Куда поехать на выходные осенью?",
            "category": "travel",
            "author": "Людмила",
            "message": "Ищу спокойный маршрут на один день, желательно "
                       "с красивой природой и кафе рядом.",
            "replies": [
                {"author": "Сергей", "message": "Советую старую усадьбу в "
                                                "сорока минутах — тихо и красиво.",
                 "time": "1 ч назад"},
                {"author": "Людмила", "message": "Спасибо, посмотрю!", "time": "40 мин назад"},
            ],
            "time": "5 ч назад",
        },
        {
            "title": "Помогите выбрать первую книгу про инвестиции",
            "category": "finance",
            "author": "Анатолий",
            "message": "Хочу разобраться в базовых принципах. Что почитать "
                       "для начала — простым языком?",
            "replies": [],
            "time": "1 ч назад",
        },
    ]
    for seed in seeds:
        topic_counter += 1
        forum_topics.append({
            "id": topic_counter,
            "title": seed["title"],
            "category": seed["category"],
            "author": seed["author"],
            "message": seed["message"],
            "time": seed["time"],
            "replies": seed["replies"],
            "views": 12 + topic_counter * 7,
        })


_seed_forum()


@app.context_processor
def inject_globals():
    """Общие данные, доступные во всех шаблонах."""
    return {
        "categories": content.category_list(),
        "CATEGORIES": content.CATEGORIES,
        "site_name": "Третий возраст",
        "year": datetime.now().year,
    }


@app.route("/")
def index():
    materials = content.MATERIALS
    # Считаем число материалов в каждой категории для фильтров.
    counts = {c["key"]: 0 for c in content.category_list()}
    for m in materials:
        counts[m["category"]] += 1
    return render_template("index.html", materials=materials, counts=counts)


@app.route("/material/<slug>")
def material(slug):
    item = content.get_material(slug)
    if item is None:
        abort(404)
    return render_template(
        "material.html",
        item=item,
        related=content.related_materials(slug),
    )


@app.route("/forum")
def forum():
    counts = {c["key"]: 0 for c in content.category_list()}
    for t in forum_topics:
        if t["category"] in counts:
            counts[t["category"]] += 1
    total_replies = sum(len(t["replies"]) for t in forum_topics)
    # Сначала темы с недавней активностью — просто по номеру, новые сверху.
    topics = sorted(forum_topics, key=lambda t: t["id"], reverse=True)
    return render_template(
        "forum.html",
        topics=topics,
        counts=counts,
        total_replies=total_replies,
    )


@app.route("/forum/new", methods=["POST"])
def forum_new():
    global topic_counter
    title = (request.form.get("title") or "").strip()
    message = (request.form.get("message") or "").strip()
    author = (request.form.get("author") or "").strip() or "Гость"
    category = request.form.get("category") or "health"

    if not title or not message:
        flash("Заполните заголовок и текст сообщения.", "error")
        return redirect(url_for("forum"))

    with forum_lock:
        topic_counter += 1
        forum_topics.append({
            "id": topic_counter,
            "title": title,
            "category": category,
            "author": author,
            "message": message,
            "time": "только что",
            "replies": [],
            "views": 0,
        })
        new_id = topic_counter

    flash("Тема создана. Добро пожаловать в обсуждение!", "success")
    return redirect(url_for("forum_topic", topic_id=new_id))


@app.route("/forum/topic/<int:topic_id>")
def forum_topic(topic_id):
    topic = next((t for t in forum_topics if t["id"] == topic_id), None)
    if topic is None:
        abort(404)
    topic["views"] += 1
    return render_template("topic.html", topic=topic)


@app.route("/forum/topic/<int:topic_id>/reply", methods=["POST"])
def forum_reply(topic_id):
    topic = next((t for t in forum_topics if t["id"] == topic_id), None)
    if topic is None:
        abort(404)

    message = (request.form.get("message") or "").strip()
    author = (request.form.get("author") or "").strip() or "Гость"
    if not message:
        flash("Введите текст ответа.", "error")
        return redirect(url_for("forum_topic", topic_id=topic_id))

    with forum_lock:
        topic["replies"].append({
            "author": author,
            "message": message,
            "time": "только что",
        })
    flash("Ответ добавлен.", "success")
    return redirect(url_for("forum_topic", topic_id=topic_id))


@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
