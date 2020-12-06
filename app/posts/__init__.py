"""Routes to transform post data."""
from datetime import datetime, timedelta
from time import sleep

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.moment import get_current_datetime, get_current_time
from app.posts.lynx.parse import batch_lynx_embeds, generate_link_previews
from clients import gcs, ghost
from clients.log import LOGGER
from database import rdbms
from database.read_sql import collect_sql_queries, fetch_raw_lynx_posts
from database.schemas import PostUpdate

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post(
    "/",
    summary="Optimize a single post image.",
    description="Generates retina and mobile varieties of post feature_images. \
        Defaults to images uploaded within the current month; \
        accepts a `?directory=` parameter which accepts a path to recursively optimize images on the given CDN.",
)
def update_post(post_update: PostUpdate):
    """Enrich post metadata upon update."""
    previous_update = post_update.post.previous
    if previous_update:
        current_time = get_current_datetime()
        previous_update_date = datetime.strptime(
            previous_update["updated_at"], "%Y-%m-%dT%H:%M:%S.000Z"
        )
        if previous_update_date and current_time - previous_update_date < timedelta(
            seconds=5
        ):
            LOGGER.warning("Post update ignored as post was just updated.")
            return "Post update ignored as post was just updated."
    post = post_update.post.current
    post_id = post.id
    slug = post.slug
    title = post.title
    feature_image = post.feature_image
    custom_excerpt = post.custom_excerpt
    primary_tag = post.primary_tag
    html = post.html
    time = get_current_time()
    body = {
        "posts": [
            {
                "meta_title": title,
                "og_title": title,
                "twitter_title": title,
                "meta_description": custom_excerpt,
                "twitter_description": custom_excerpt,
                "og_description": custom_excerpt,
                "updated_at": time,
            }
        ]
    }
    if primary_tag.slug == "roundup" and feature_image is None:
        feature_image = gcs.fetch_random_lynx_image()
        body["posts"][0].update(
            {
                "feature_image": feature_image,
                "og_image": feature_image,
                "twitter_image": feature_image,
            }
        )
    if html and "http://" in html:
        html = html.replace("http://", "https://")
        body["posts"][0].update({"html": html})
        LOGGER.info(f"Resolved unsecure links in post `{slug}`")
    # Update image meta tags
    if feature_image is not None:
        body["posts"][0].update(
            {"og_image": feature_image, "twitter_image": feature_image}
        )
    if body["posts"][0]["mobiledoc"]:
        sleep(1)
        time = get_current_time()
        body["posts"][0]["updated_at"] = time
    response, code = ghost.update_post(post_id, body, slug)
    return {str(code): response}


@router.get(
    "/",
    summary="Sanitize metadata for all posts.",
    description="Run a sequence of queries to ensure all posts have proper metadata.",
)
def batch_post_metadata():
    """Mass update post metadata."""
    queries = collect_sql_queries(subdirectory="/posts/updates")
    results, total_rows = rdbms.execute_queries(queries, "hackers_prod")
    LOGGER.success(f"Successfully ran {len(queries)} post queries")
    return {
        "db": {
            "type": "posts",
            "num_queries": len(queries),
            "db_name": "hackers_prod",
            "rows_affected": total_rows,
            "queries": results,
        }
    }


@router.get(
    "/embed",
    summary="Batch create Lynx embeds.",
    description="Fetch raw Lynx post and generate embedded link previews.",
)
def batch_lynx_previews():
    posts = fetch_raw_lynx_posts()
    result = batch_lynx_embeds(posts)
    return result


@router.post(
    "/embed",
    summary="Embed Lynx links.",
    description="Generate embedded link previews for a single Lynx post.",
)
def post_link_previews(post_update: PostUpdate):
    """Render anchor tag link previews."""
    post = post_update.post.current
    post_id = post.id
    slug = post.slug
    html = post.html
    previous = post_update.post.previous
    primary_tag = post.primary_tag
    if primary_tag.slug == "roundup":
        if html is not None and "kg-card" not in html:
            if previous.get("slug", None) is None:
                num_embeds, doc = generate_link_previews(post.__dict__)
                result = rdbms.execute_query(
                    f"UPDATE posts SET mobiledoc = '{doc}' WHERE id = '{post_id}';",
                    "hackers_prod",
                )
                LOGGER.info(f"Generated Previews for Lynx post {slug}: {doc}")
                return result
        LOGGER.warning(f"Lynx post {slug} already contains previews.")
        return JSONResponse(
            {f"Lynx post {slug} already contains previews."},
            status_code=202,
            headers={"content-type": "text/plain"},
        )


@router.get("/backup")
def backup_database():
    """Export JSON backup of database."""
    json = ghost.get_json_backup()
    return json