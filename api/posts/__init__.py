"""Routes to transform post data."""
from flask import current_app as api
from flask import jsonify, make_response, request
from api import ghost, db, image
from api.log import LOGGER
from api.moment import get_current_time
from .read import get_queries
from .lynx.cards import generate_link_previews


@LOGGER.catch
@api.route('/post/update', methods=['POST'])
def update_post():
    """Update post metadata & render Lynx previews."""
    post = request.get_json()['post']['current']
    post_id = post.get('id')
    slug = post.get('slug')
    title = post.get('title')
    feature_image = post.get('feature_image')
    custom_excerpt = post.get('custom_excerpt')
    primary_tag = post.get('primary_tag')
    mobiledoc = post.get('mobiledoc')
    time = get_current_time()
    body = {
        "posts": [{
            "meta_title": title,
            "og_title": title,
            "twitter_title": title,
            "meta_description": custom_excerpt,
            "twitter_description": custom_excerpt,
            "og_description": custom_excerpt,
            "updated_at": time
            }
        ]
    }
    if primary_tag.get('slug') == 'roundup':
        # Assign random image to Lynx post
        if feature_image is None:
            feature_image = image.fetch_random_lynx_image()
            body['posts'][0].update({
                "feature_image": feature_image,
                "og_image": feature_image,
                "twitter_image": feature_image
            })
        # Parse link previews
        if 'kg-card' not in mobiledoc:
            doc = generate_link_previews(post)
            LOGGER.info(f'Lynx mobile doc: {doc}')
            # db.execute_query(f"UPDATE posts SET mobiledoc = '{doc}' WHERE id = '{post_id}';")
    # Update image meta tags
    if feature_image is not None:
        body['posts'][0].update({
            "og_image": feature_image,
            "twitter_image": feature_image
        })
    response, code = ghost.update_post(post_id, body, slug)
    LOGGER.info(f'Post Updated with code {code}: {body}')
    return make_response(jsonify(response), code)


@LOGGER.catch
@api.route('/post/metadata', methods=['GET'])
def post_metadata_sanitize():
    """Mass update post metadata."""
    queries = get_queries()
    results = db.execute_queries(queries)
    headers = {'Content-Type': 'application/json'}
    LOGGER.info(f'Successfully ran queries: {queries}')
    return make_response(jsonify(results), 200, headers)


@LOGGER.catch
@api.route('/post/backup', methods=['GET'])
def backup_database():
    """Save JSON backup of database."""
    json = ghost.get_json_backup()
    return json
