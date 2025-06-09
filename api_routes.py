import time
from flask import jsonify, request
from flask_restful import Resource, Api
import userManagement as dbHandler
import logging

api = Api()
logger = logging.getLogger(__name__)

class ServerStatus(Resource):
    def __init__(self):
        self.start_time = time.time()

    def get(self):
        logger.debug("ServerStatus endpoint called")

        uptime_seconds = time.time() - self.start_time
        uptime = self.format_uptime(uptime_seconds)

        status = {
            "server": "online",
            "message": "GameStudy server is running.",
            "uptime": uptime,
        }

        logger.debug("Returning server status: %s", status)
        return jsonify(status)

    def format_uptime(self, seconds):
        days = seconds // (24 * 3600)
        seconds %= (24 * 3600)
        hours = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        return f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"

class UserGameStats(Resource):
    def get(self):
        logger.debug("UserGameStats endpoint called")
        
        username = request.args.get('username')
        if not username:
            logger.debug("Username is required")
            return jsonify({"message": "Username is required"}), 400
        
        logger.debug("Username from query parameters: %s", username)
        user = dbHandler.get_user(username)
        if user:
            logger.debug("User found: %s", user)
            stats = dbHandler.get_user_game_stats(user['username'])
            logger.debug("User game stats: %s", stats)
            data = {
                "total_sessions": stats.get('total_sessions', 0),
                "average_xp": stats.get('average_xp', 0),
                "recent_sessions": stats.get('recent_sessions', []),
                "xp_over_time": stats.get('xp_over_time', {})
            }
            logger.debug("Returning user study stats: %s", data)
            return jsonify(data)
        else:
            logger.debug("User not found: %s", username)
            return jsonify({"message": "User not found"}), 404

api.add_resource(UserGameStats, '/api/user_game_stats')
api.add_resource(ServerStatus, '/api/server_status')
