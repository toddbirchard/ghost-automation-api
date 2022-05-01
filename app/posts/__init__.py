"""Ghost post enrichment of data."""
from datetime import datetime, timedelta
from time import sleep

from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from app.moment import get_current_datetime, get_current_time
from app.posts.metadata import assign_img_alt, batch_assign_img_alt
from app.posts.update import (
    update_html_ssl_links,
    update_metadata,
    update_metadata_images,
)
from clients import ghost
from config import BASE_DIR
from database import rdbms
from database.read_sql import collect_sql_queries
from database.schemas import PostBulkUpdate, PostUpdate
from log import LOGGER

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post(
    "/",
    summary="Optimize post metadata.",
    description="Performs multiple actions to optimize post SEO. \
                Generates meta tags, ensures SSL hyperlinks, and populates missing <img /> `alt` attributes.",
    response_model=PostUpdate,
)
async def update_post(post_update: PostUpdate):
    """
    Enrich post metadata upon update.

    :param PostUpdate post_update: Request to update Ghost post.

    """
    previous_update = post_update.post.previous
    if previous_update:
        current_time = get_current_datetime()
        previous_update_date = datetime.strptime(
            str(previous_update.updated_at), "%Y-%m-%dT%H:%M:%S.000Z"
        )
        LOGGER.debug(
            f"current_time=`{current_time}` previous_update_date=`{previous_update_date}`"
        )
        if previous_update_date and current_time - previous_update_date < timedelta(
            seconds=5
        ):
            LOGGER.warning("Post update ignored as post was just updated.")
            raise HTTPException(
                status_code=422, detail="Post update ignored as post was just updated."
            )
    post = post_update.post.current
    slug = post.slug
    feature_image = post.feature_image
    html = post.html
    body = {
        "posts": [
            {
                "meta_title": post.title,
                "og_title": post.title,
                "twitter_title": post.title,
                "meta_description": post.custom_excerpt,
                "twitter_description": post.custom_excerpt,
                "og_description": post.custom_excerpt,
                "updated_at": get_current_time(),
            }
        ]
    }
    if html and "http://" in html:
        body = update_html_ssl_links(html, body, slug)
    if feature_image is not None:
        body = update_metadata_images(feature_image, body, slug)
    if body["posts"][0].get("mobiledoc") is not None:
        mobiledoc = assign_img_alt(body["posts"][0]["mobiledoc"])
        body["posts"][0].update({"mobiledoc": mobiledoc})
    sleep(1)
    time = get_current_time()
    body["posts"][0]["updated_at"] = time
    response, code = ghost.update_post(post.id, body, post.slug)
    LOGGER.success(f"Successfully updated post `{slug}`: {body}")
    return {str(code): response}


@router.get(
    "/",
    summary="Sanitize metadata for all posts.",
    description="Ensure all posts have properly optimized metadata.",
    response_model=PostBulkUpdate,
)
async def batch_update_metadata():
    """Run SQL queries to sanitize metadata for all posts."""
    update_queries = collect_sql_queries("posts/updates")
    update_results = rdbms.execute_queries(update_queries, "hackers_dev")
    insert_posts = rdbms.execute_query_from_file(
        f"{BASE_DIR}/database/queries/posts/selects/missing_all_metadata.sql",
        "hackers_dev",
    )
    insert_results = update_metadata(insert_posts)
    LOGGER.success(
        f"Inserted metadata for {len(insert_results)} posts, updated {len(update_results.keys())}."
    )
    return {
        "inserted": {"count": len(insert_results), "posts": insert_results},
        "updated": {"count": len(update_results.keys()), "posts": update_results},
    }


@router.get(
    "/alt",
    summary="Populate missing alt text for images.",
    description="Assign missing alt text to embedded images.",
)
async def assign_img_alt_attr():
    """Find <img>s missing alt text and assign `alt`, `title` attributes."""
    return batch_assign_img_alt()


@router.get("/backup")
async def backup_database():
    """Export JSON backup of database."""
    json = ghost.get_json_backup()
    return json


@router.get(
    "/post",
    summary="Get a post.",
)
async def get_single_post(post_id: str):
    """
    Request to get Ghost post.

    :param str post_id: Post to fetch
    """
    if post_id is None:
        raise HTTPException(
            status_code=422, detail="Post ID required to test endpoint."
        )
    return ghost.get_post(post_id)


@router.get(
    "/all",
    summary="Get all post URLs.",
)
async def get_all_posts():
    """List all published Ghost posts."""
    posts = ghost.get_all_posts()
    LOGGER.success(f"Fetched all {len(posts)} Ghost posts: {posts}")
    return JSONResponse(
        posts,
        status_code=200,
        headers={"content-type": "application/json"},
    )
