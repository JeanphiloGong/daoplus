from app.services.neo4j_service import Neo4jService

def add_reward_points(user, points):
    """Add reward points to a user."""
    # Check if the user already has a reward record
    query = """
    MATCH (u:User {id: $user_id})-[:HAS_REWARD]->(r:Reward)
    RETURN r
    """
    result = user.neo4j_service.execute_query(query, {"user_id": user.id})
    reward = result.single()

    if reward:
        # If reward node exists, increment the points
        query = """
        MATCH (u:User {id: $user_id})-[:HAS_REWARD]->(r:Reward)
        SET r.points = r.points + $points
        RETURN r
        """
        user.neo4j_service.execute_query(query, {"user_id": user.id, "points": points})
    else:
        # If no reward node exists, create a new one
        query = """
        MATCH (u:User {id: $user_id})
        CREATE (u)-[:HAS_REWARD]->(r:Reward {points: $points})
        RETURN r
        """
        user.neo4j_service.execute_query(query, {"user_id": user.id, "points": points})

def deduct_reward_points(user, points):
    """Deduct reward points from a user."""
    # Check if the user has enough reward points
    query = """
    MATCH (u:User {id: $user_id})-[:HAS_REWARD]->(r:Reward)
    RETURN r.points AS points
    """
    result = user.neo4j_service.execute_query(query, {"user_id": user.id})
    reward = result.single()

    if reward and reward["points"] >= points:
        # Deduct points if sufficient points are available
        query = """
        MATCH (u:User {id: $user_id})-[:HAS_REWARD]->(r:Reward)
        SET r.points = r.points - $points
        RETURN r
        """
        user.neo4j_service.execute_query(query, {"user_id": user.id, "points": points})
        return True
    else:
        return False  # Insufficient points

def get_user_rewards(user):
    """Retrieve the user's total reward points."""
    query = """
    MATCH (u:User {id: $user_id})-[:HAS_REWARD]->(r:Reward)
    RETURN r.points AS points
    """
    result = user.neo4j_service.execute_query(query, {"user_id": user.id})
    reward = result.single()
    return reward["points"] if reward else 0
