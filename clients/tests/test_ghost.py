def test_get_ghost_post(ghost):
    post = ghost.get_post("61304d8374047afda1c21b06")
    assert post is not None
    assert post["id"] == "61304d8374047afda1c21b06"
