class Like:
    def __init__(self, user_id, post_id, like_id=None, created_at=None):
        self.user_id = user_id
        self.post_id = post_id
        self.like_id = like_id
        self.created_at = created_at or datetime.utcnow()

    @staticmethod
    def like_post(neo4j_service, user_id, post_id):
        """Create a LIKE relationship between a user and a post."""
        query = """
        MATCH (u:User), (p:Post)
        WHERE ID(u) = $user_id AND ID(p) = $post_id
        CREATE (u)-[:LIKES]->(p)
        RETURN ID(u) AS user_id, ID(p) AS post_id
        """
        neo4j_service.execute_write(query, {
            "user_id": int(user_id),
            "post_id": int(post_id)
        })

    @staticmethod
    def unlike_post(neo4j_service, user_id, post_id):
        """Remove a LIKE relationship between a user and a post."""
        query = """
        MATCH (u:User)-[r:LIKES]->(p:Post)
        WHERE ID(u) = $user_id AND ID(p) = $post_id
        DELETE r
        """
        neo4j_service.execute_write(query, {
            "user_id": int(user_id),
            "post_id": int(post_id)
        })

    @staticmethod
    def is_liked(neo4j_service, user_id, post_id):
        """Check if a user has already liked a post."""
        query = """
        MATCH (u:User)-[:LIKES]->(p:Post)
        WHERE ID(u) = $user_id AND ID(p) = $post_id
        RETURN COUNT(r) AS like_count
        """
        result = neo4j_service.execute_query(query, {
            "user_id": int(user_id),
            "post_id": int(post_id)
        })
        if result and result[0]['like_count'] > 0:
            return True
        return False
