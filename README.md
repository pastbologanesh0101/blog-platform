# Blogging Platform

A small, self-contained blogging platform built with Flask and SQLite. Write
posts in Markdown, publish or unpublish them, and view them on clean,
server-rendered pages — no JavaScript framework, no external database.

## Features

- **Posts** with a title, Markdown body, auto-generated unique slug,
  creation timestamp, and a published/draft flag.
- **Create** posts through a simple form; Markdown is rendered to HTML with
  the [`markdown`](https://python-markdown.github.io/) package (fenced code
  blocks and tables supported).
- **Automatic slugs**: generated from the title (e.g. "Hello World!" ->
  `hello-world`). Colliding titles get `-2`, `-3`, etc. appended.
- **List** view shows only published posts, newest first.
- **View by slug**: `/post/<slug>` — works for both published and
  unpublished posts (direct links still work for drafts/previews).
- **Edit** a post's title, body, and published state; **unpublish** with one
  click.
- App factory pattern (`create_app`) so tests run against an isolated
  in-memory SQLite database.

## Requirements

- Python 3.11+

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running the app

```bash
export FLASK_APP=app.py
flask init-db     # creates instance/blog.sqlite with the post table
flask run
```

Then open http://127.0.0.1:5000 in your browser.

## Example usage

1. Visit `/new` and create a post:
   - Title: `Hello World`
   - Body (Markdown):
     ```
     This is my **first** post with some *emphasis* and a list:

     - one
     - two
     ```
   - Check "Publish immediately" and click **Save Post**.
2. You're redirected to `/post/hello-world`, where the Markdown body has
   been rendered to HTML (`<strong>first</strong>`, `<em>emphasis</em>`,
   a `<ul>` list, etc).
3. The post now appears on the home page (`/`).
4. Create a second post titled `Hello World` — it automatically gets the
   slug `hello-world-2` to avoid colliding with the first.
5. Visit `/post/hello-world/edit` to change the title/body or uncheck
   "Published" to turn it back into a draft. A quick **Unpublish** button is
   also available on the post page.
6. Unpublished posts disappear from the home page listing but remain
   reachable at their direct `/post/<slug>` URL.

## Running the tests

```bash
pip install -r requirements-dev.txt
pytest -v
```

Tests use Flask's test client against an in-memory SQLite database (via
`create_app(testing=True)`), so they don't touch the filesystem and run
quickly. Tests cover: post creation, slug generation/uniqueness, viewing a
post by slug, unpublished posts being hidden from the list (but still
reachable directly), Markdown-to-HTML rendering, editing a post, and the
unpublish route.

## Project layout

```
blog-platform/
├── app.py                       # entry point (flask run / flask init-db)
├── blog_platform/
│   ├── __init__.py               # create_app() app factory
│   ├── db.py                     # SQLite connection handling
│   ├── schema.sql                # post table definition
│   ├── slugify.py                # slug generation + uniqueness
│   ├── routes.py                 # all view routes
│   ├── templates/                # Jinja2 templates
│   └── static/style.css          # plain CSS
├── tests/
│   ├── conftest.py
│   └── test_blog.py
├── requirements.txt
├── requirements-dev.txt
└── .github/workflows/tests.yml   # CI: pytest on Python 3.11 and 3.12
```

## License

MIT — see [LICENSE](LICENSE).
