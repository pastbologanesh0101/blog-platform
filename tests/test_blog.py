def create_post(client, title="Hello World", body="This is **bold** text.", published=True):
    data = {"title": title, "body_markdown": body}
    if published:
        data["published"] = "on"
    return client.post("/new", data=data, follow_redirects=True)


def test_create_post(client):
    response = create_post(client, title="My First Post", body="Some content here.")
    assert response.status_code == 200
    assert b"My First Post" in response.data
    assert b"Some content here." in response.data


def test_slug_generation_and_uniqueness(client, app):
    create_post(client, title="Hello World!")
    create_post(client, title="Hello World!")

    with app.app_context():
        from blog_platform.db import get_db

        db = get_db()
        slugs = [
            row["slug"]
            for row in db.execute(
                "SELECT slug FROM post ORDER BY id"
            ).fetchall()
        ]

    assert slugs[0] == "hello-world"
    assert slugs[1] == "hello-world-2"
    assert slugs[0] != slugs[1]


def test_view_post_by_slug(client):
    create_post(client, title="A Unique Title", body="Body text for this post.")
    response = client.get("/post/a-unique-title")
    assert response.status_code == 200
    assert b"A Unique Title" in response.data
    assert b"Body text for this post." in response.data


def test_unpublished_post_hidden_from_list(client):
    create_post(client, title="Draft Post", body="Secret draft content.", published=False)
    create_post(client, title="Published Post", body="Visible content.", published=True)

    index_response = client.get("/")
    assert b"Published Post" in index_response.data
    assert b"Draft Post" not in index_response.data

    # But the draft is still reachable by direct slug link.
    direct_response = client.get("/post/draft-post")
    assert direct_response.status_code == 200
    assert b"Draft Post" in direct_response.data


def test_markdown_rendered_to_html(client):
    create_post(
        client,
        title="Markdown Post",
        body="This is **bold** and this is *italic*.",
    )
    response = client.get("/post/markdown-post")
    assert response.status_code == 200
    assert b"<strong>bold</strong>" in response.data
    assert b"<em>italic</em>" in response.data
    # Raw markdown syntax should not leak through unrendered.
    assert b"**bold**" not in response.data


def test_edit_post_updates_title_and_body(client):
    create_post(client, title="Original Title", body="Original body.")
    response = client.post(
        "/post/original-title/edit",
        data={
            "title": "Original Title",
            "body_markdown": "Updated body.",
            "published": "on",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Updated body." in response.data


def test_unpublish_route_removes_post_from_index(client):
    create_post(client, title="Temporary Post", body="Will be unpublished.")
    client.post("/post/temporary-post/unpublish", follow_redirects=True)

    index_response = client.get("/")
    assert b"Temporary Post" not in index_response.data
