from datetime import datetime, timezone

import markdown as markdown_lib
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from .db import get_db
from .slugify import unique_slug

bp = Blueprint("blog", __name__)


def render_markdown(text):
    """Render a Markdown string to HTML."""
    return markdown_lib.markdown(text or "", extensions=["fenced_code", "tables"])


@bp.route("/")
def index():
    db = get_db()
    posts = db.execute(
        "SELECT id, title, slug, created_at FROM post "
        "WHERE published = 1 ORDER BY created_at DESC"
    ).fetchall()
    return render_template("index.html", posts=posts)


@bp.route("/new", methods=["GET", "POST"])
def new_post():
    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        body_markdown = request.form.get("body_markdown") or ""
        published = 1 if request.form.get("published") else 0

        error = None
        if not title:
            error = "Title is required."
        elif not body_markdown.strip():
            error = "Post body is required."

        if error is not None:
            flash(error)
            return render_template(
                "new.html", title=title, body_markdown=body_markdown
            )

        db = get_db()
        slug = unique_slug(db, title)
        created_at = datetime.now(timezone.utc).isoformat()
        db.execute(
            "INSERT INTO post (title, slug, body_markdown, created_at, published) "
            "VALUES (?, ?, ?, ?, ?)",
            (title, slug, body_markdown, created_at, published),
        )
        db.commit()
        return redirect(url_for("blog.view_post", slug=slug))

    return render_template("new.html", title="", body_markdown="")


def _get_post_or_404(slug):
    db = get_db()
    post = db.execute("SELECT * FROM post WHERE slug = ?", (slug,)).fetchone()
    if post is None:
        abort(404)
    return post


@bp.route("/post/<slug>")
def view_post(slug):
    post = _get_post_or_404(slug)
    body_html = render_markdown(post["body_markdown"])
    return render_template("post.html", post=post, body_html=body_html)


@bp.route("/post/<slug>/edit", methods=["GET", "POST"])
def edit_post(slug):
    post = _get_post_or_404(slug)
    db = get_db()

    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        body_markdown = request.form.get("body_markdown") or ""
        published = 1 if request.form.get("published") else 0

        error = None
        if not title:
            error = "Title is required."
        elif not body_markdown.strip():
            error = "Post body is required."

        if error is not None:
            flash(error)
            return render_template("edit.html", post=post)

        db.execute(
            "UPDATE post SET title = ?, body_markdown = ?, published = ? "
            "WHERE id = ?",
            (title, body_markdown, published, post["id"]),
        )
        db.commit()
        return redirect(url_for("blog.view_post", slug=slug))

    return render_template("edit.html", post=post)


@bp.route("/post/<slug>/unpublish", methods=["POST"])
def unpublish_post(slug):
    post = _get_post_or_404(slug)
    db = get_db()
    db.execute("UPDATE post SET published = 0 WHERE id = ?", (post["id"],))
    db.commit()
    return redirect(url_for("blog.view_post", slug=slug))
