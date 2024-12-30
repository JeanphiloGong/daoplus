from app import neo4j_driver
from datetime import datetime

class Post:
    def __init__(self, title, content, user_id, post_id=None, is_flagged=False, created_at=None):
        self.title = title
        self.content = content
        self.user_id = user_id
        self.post_id = post_id
        self.is_flagged = is_flagged
        self.created_at = created_at or datetime.utcnow()

    @staticmethod
    def create_post(neo4j_service, title, content, user_id):
        """Create a new post in the Neo4j database."""
        query = """
        MATCH (u:User) WHERE ID(u) = $user_id
        CREATE (p:Post {title: $title, content: $content, is_flagged: $is_flagged, created_at: datetime()})-[:CREATED_BY]->(u)
        RETURN ID(p) AS id, p.title AS title, p.content AS content, p.is_flagged AS is_flagged, p.created_at AS created_at
        """
        result = neo4j_service.execute_query(query, {
            "title": title,
            "content": content,
            "is_flagged": False,
            "user_id": int(user_id)
        })
        if result:
            data = result[0]
            return Post(title=data['title'], content=data['content'], user_id=user_id, post_id=data['id'], is_flagged=data['is_flagged'], created_at=data['created_at'])
        return None

    @staticmethod
    def get_all_posts(neo4j_service):
        """Retrieve all posts from the Neo4j database."""
        query = """
        MATCH (p:Post)-[:CREATED_BY]->(u:User)
        RETURN ID(p) AS id, p.title AS title, p.content AS content, p.is_flagged AS is_flagged, p.created_at AS created_at, u.username AS author
        ORDER BY p.created_at DESC
        """
        result = neo4j_service.execute_query(query)
        posts = []
        for record in result:
            post = Post(
                title=record['title'],
                content=record['content'],
                user_id=None,  # Optionally include user_id if needed
                post_id=record['id'],
                is_flagged=record['is_flagged'],
                created_at=record['created_at']
            )
            post.author = record['author']  # Assign author attribute for templates
            posts.append(post)
        return posts

    @staticmethod
    def get_post_by_id(neo4j_service, post_id):
        """Retrieve a single post by ID from the Neo4j database."""
        query = """
        MATCH (p:Post)-[:CREATED_BY]->(u:User)
        WHERE ID(p) = $post_id
        RETURN ID(p) AS id, p.title AS title, p.content AS content, p.is_flagged AS is_flagged, p.created_at AS created_at, u.username AS author
        """
        result = neo4j_service.execute_query(query, {"post_id": int(post_id)})
        if result:
            data = result[0]
            post = Post(
                title=data['title'],
                content=data['content'],
                user_id=None,  # Optionally include user_id if needed
                post_id=data['id'],
                is_flagged=data['is_flagged'],
                created_at=data['created_at']
            )
            post.author = data['author']
            return post
        return None

    @staticmethod
    def update_post(neo4j_service, post_id, title, content):
        """Update an existing post in the Neo4j database."""
        query = """
        MATCH (p:Post) WHERE ID(p) = $post_id
        SET p.title = $title, p.content = $content
        RETURN p
        """
        neo4j_service.execute_write(query, {
            "post_id": int(post_id),
            "title": title,
            "content": content
        })

    @staticmethod
    def delete_post(neo4j_service, post_id):
        """Delete a post from the Neo4j database."""
        query = """
        MATCH (p:Post) WHERE ID(p) = $post_id
        DETACH DELETE p
        """
        neo4j_service.execute_write(query, {"post_id": int(post_id)})

    @staticmethod
    def flag_post(neo4j_service, post_id):
        """Flag a post for moderation."""
        query = """
        MATCH (p:Post) WHERE ID(p) = $post_id
        SET p.is_flagged = true
        """
        neo4j_service.execute_write(query, {"post_id": int(post_id)})

    @staticmethod
    def unflag_post(neo4j_service, post_id):
        """Unflag a previously flagged post."""
        query = """
        MATCH (p:Post) WHERE ID(p) = $post_id
        SET p.is_flagged = false
        """
        neo4j_service.execute_write(query, {"post_id": int(post_id)})

    @staticmethod
    def get_flagged_posts(neo4j_service):
        """Retrieve all flagged posts for admin review."""
        query = """
        MATCH (p:Post)-[:CREATED_BY]->(u:User)
        WHERE p.is_flagged = true
        RETURN ID(p) AS id, p.title AS title, p.content AS content, p.created_at AS created_at, u.username AS author
        ORDER BY p.created_at DESC
        """
        result = neo4j_service.execute_query(query)
        flagged_posts = []
        for record in result:
            post = Post(
                title=record['title'],
                content=record['content'],
                user_id=None,
                post_id=record['id'],
                is_flagged=True,
                created_at=record['created_at']
            )
            post.author = record['author']
            flagged_posts.append(post)
        return flagged_posts

    @staticmethod
    def search_posts(neo4j_service, query_text):
        """Search posts by title or content."""
        query = """
        MATCH (p:Post)-[:CREATED_BY]->(u:User)
        WHERE toLower(p.title) CONTAINS toLower($query) OR toLower(p.content) CONTAINS toLower($query)
        RETURN ID(p) AS id, p.title AS title, p.content AS content, p.is_flagged AS is_flagged, p.created_at AS created_at, u.username AS author
        ORDER BY p.created_at DESC
        """
        result = neo4j_service.execute_query(query, {"query": query_text})
        posts = []
        for record in result:
            post = Post(
                title=record['title'],
                content=record['content'],
                user_id=None,
                post_id=record['id'],
                is_flagged=record['is_flagged'],
                created_at=record['created_at']
            )
            post.author = record['author']
            posts.append(post)
        return posts

    def __repr__(self):
        return f"<Post {self.title}>"

