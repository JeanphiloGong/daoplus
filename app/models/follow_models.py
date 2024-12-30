class Follow:
    def __init__(self, follower_id, followed_id, follow_id=None, created_at=None):
        self.follower_id = follower_id
        self.followed_id = followed_id
        self.follow_id = follow_id
        self.created_at = created_at or datetime.utcnow()

    @staticmethod
    def follow_user(neo4j_service, follower_id, followed_id):
        """Create a FOLLOWS relationship between two users."""
        query = """
        MATCH (f:User), (t:User)
        WHERE ID(f) = $follower_id AND ID(t) = $followed_id
        CREATE (f)-[:FOLLOWS]->(t)
        RETURN ID(f) AS follower_id, ID(t) AS followed_id
        """
        neo4j_service.execute_write(query, {
            "follower_id": int(follower_id),
            "followed_id": int(followed_id)
        })

    @staticmethod
    def unfollow_user(neo4j_service, follower_id, followed_id):
        """Remove a FOLLOWS relationship between two users."""
        query = """
        MATCH (f:User)-[r:FOLLOWS]->(t:User)
        WHERE ID(f) = $follower_id AND ID(t) = $followed_id
        DELETE r
        """
        neo4j_service.execute_write(query, {
            "follower_id": int(follower_id),
            "followed_id": int(followed_id)
        })

    @staticmethod
    def is_following(neo4j_service, follower_id, followed_id):
        """Check if a user is following another user."""
        query = """
        MATCH (f:User)-[r:FOLLOWS]->(t:User)
        WHERE ID(f) = $follower_id AND ID(t) = $followed_id
        RETURN COUNT(r) AS follow_count
        """
        result = neo4j_service.execute_query(query, {
            "follower_id": int(follower_id),
            "followed_id": int(followed_id)
        })
        if result and result[0]['follow_count'] > 0:
            return True
        return False
