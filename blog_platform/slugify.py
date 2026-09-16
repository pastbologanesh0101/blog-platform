import re


def slugify(title):
    """Turn a post title into a URL-friendly slug.

    Lowercases, replaces runs of non-alphanumeric characters with a single
    hyphen, and strips leading/trailing hyphens. Falls back to "post" if
    the title has no alphanumeric characters at all.
    """
    slug = title.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug or "post"


def unique_slug(db, title):
    """Generate a slug for ``title`` that does not collide with any
    existing post's slug. Collisions are resolved by appending -2, -3, ...
    """
    base = slugify(title)
    slug = base
    suffix = 2
    while db.execute("SELECT 1 FROM post WHERE slug = ?", (slug,)).fetchone():
        slug = f"{base}-{suffix}"
        suffix += 1
    return slug
