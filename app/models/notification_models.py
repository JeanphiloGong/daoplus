from datetime import datetime

class Notification:
    def __init__(self, user_id, action, target_id, target_type, notification_id=None, created_at=None):
        self.user_id = user_id
        self.action = action
        self.target_id = target_id
        self.target_type = target_type
        self.notification_id = notification_id
        self.created_at = created_at or datetime.utcnow()

    @staticmethod
    def create_notification(neo4j_service, user_id, action, target_id, target_type):
        """Create a new notification in the Neo4j database."""
        query = """
        MATCH (u:User) WHERE ID(u) = $user_id
        CREATE (n:Notification {action: $action, target_id: $target_id, target_type: $target_type, created_at: datetime()})-[:SENT_TO]->(u)
        RETURN ID(n) AS id, n.action AS action, n.target_id AS target_id, n.target_type AS target_type, n.created_at AS created_at
        """
        result = neo4j_service.execute_query(query, {
            "user_id": int(user_id),
            "action": action,
            "target_id": int(target_id),
            "target_type": target_type
        })
        if result:
            data = result[0]
            return Notification(
                user_id=user_id,
                action=data['action'],
                target_id=data['target_id'],
                target_type=data['target_type'],
                notification_id=data['id'],
                created_at=data['created_at']
            )
        return None

    @staticmethod
    def get_notifications_for_user(neo4j_service, user_id):
        """Retrieve all notifications for a specific user."""
        query = """
        MATCH (n:Notification)-[:SENT_TO]->(u:User)
        WHERE ID(u) = $user_id
        RETURN ID(n) AS id, n.action AS action, n.target_id AS target_id, n.target_type AS target_type, n.created_at AS created_at
        ORDER BY n.created_at DESC
        """
        result = neo4j_service.execute_query(query, {"user_id": int(user_id)})
        notifications = []
        for record in result:
            notification = Notification(
                user_id=user_id,
                action=record['action'],
                target_id=record['target_id'],
                target_type=record['target_type'],
                notification_id=record['id'],
                created_at=record['created_at']
            )
            notifications.append(notification)
        return notifications

    @staticmethod
    def delete_notification(neo4j_service, notification_id):
        """Delete a notification from the Neo4j database."""
        query = """
        MATCH (n:Notification) WHERE ID(n) = $notification_id
        DETACH DELETE n
        """
        neo4j_service.execute_write(query, {"notification_id": int(notification_id)})

    def save(self, neo4j_service):
        """Save (update) the current notification in the Neo4j database."""
        if self.notification_id:
            query = """
            MATCH (n:Notification) WHERE ID(n) = $notification_id
            SET n.action = $action, n.target_id = $target_id, n.target_type = $target_type, n.created_at = datetime()
            RETURN n
            """
            neo4j_service.execute_write(query, {
                "notification_id": int(self.notification_id),
                "action": self.action,
                "target_id": int(self.target_id),
                "target_type": self.target_type
            })
        else:
            # Optionally handle creating a new notification if not already created
            pass

    def __repr__(self):
        return f"<Notification {self.action} on {self.target_type}>"
