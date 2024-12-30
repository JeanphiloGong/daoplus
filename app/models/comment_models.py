from datetime import datetime

class Comment:
    def __init__(self, content, user_id, post_id, comment_id=None, created_at=None):
        self.content = content
        self.user_id = user_id
        self.post_id = post_id
        self.comment_id = comment_id
        self.created_at = created_at or datetime.utcnow()

    @staticmethod
    def create_comment(neo4j_service, content, user_id, post_id):
        """Create a new comment in the Neo4j database."""
        query = """
        MATCH (u:User), (p:Post)
        WHERE ID(u) = $user_id AND ID(p) = $post_id
        CREATE (c:Comment {content: $content, created_at: datetime()})-[:COMMENTED_BY]->(u)-[:ON]->(p)
        RETURN ID(c) AS id, c.content AS content, c.created_at AS created_at
        """
        result = neo4j_service.execute_query(query, {
            "content": content,
            "user_id": int(user_id),
            "post_id": int(post_id)
        })
        if result:
            data = result[0]
            return Comment(content=data['content'], user_id=user_id, post_id=post_id, comment_id=data['id'], created_at=data['created_at'])
        return None

    @staticmethod
    def get_comments_by_post_id(neo4j_service, post_id):
        """Retrieve all comments for a specific post."""
        query = """
        MATCH (c:Comment)-[:COMMENTED_BY]->(u:User)-[:ON]->(p:Post)
        WHERE ID(p) = $post_id
        RETURN ID(c) AS id, c.content AS content, c.created_at AS created_at, u.username AS author
        ORDER BY c.created_at ASC
        """
        result = neo4j_service.execute_query(query, {"post_id": int(post_id)})
        comments = []
        for record in result:
            comment = Comment(
                content=record['content'],
                user_id=None,  # Optionally include user_id if needed
                post_id=post_id,
                comment_id=record['id'],
                created_at=record['created_at']
            )
            comment.author = record['author']  # Assign author attribute for templates
            comments.append(comment)
        return comments

    @staticmethod
    def delete_comment(neo4j_service, comment_id):
        """Delete a comment from the Neo4j database."""
        query = """
        MATCH (c:Comment) WHERE ID(c) = $comment_id
        DETACH DELETE c
        """
        neo4j_service.execute_write(query, {"comment_id": int(comment_id)})

    @staticmethod
    def update_comment(neo4j_service, comment_id, content):
        """Update an existing comment in the Neo4j database."""
        query = """
        MATCH (c:Comment) WHERE ID(c) = $comment_id
        SET c.content = $content, c.created_at = datetime()
        RETURN c
        """
        neo4j_service.execute_write(query, {
            "comment_id": int(comment_id),
            "content": content
        })

    def __repr__(self):
        return f"<Comment {self.content[:30]}>"
