from urllib.parse import quote_plus

from bson.objectid import ObjectId
from configuration import conf
from motor import motor_asyncio


class MongoDB:
    def __init__(self):
        if conf.bot.debug:
            self.client = motor_asyncio.AsyncIOMotorClient(host="localhost", port=27017)
        else:
            self.client = motor_asyncio.AsyncIOMotorClient(
                host=conf.db.host,
                port=conf.db.port,
                username=quote_plus(conf.db.username),
                password=quote_plus(conf.db.password),
            )
        self.db = self.client[conf.db.database]

    async def user_update(self, user_id, data=None):
        user_info = await self.db.users.find_one({"user_id": user_id})

        if user_info is None:
            await self.db.users.insert_one({"user_id": user_id})
            return await self.user_update(user_id, data)

        if data:
            await self.db.users.update_one(
                {"user_id": user_id}, {"$set": data}, upsert=True
            )
            return await self.user_update(user_id)

        return user_info
    
    async def guest_update(self, badge_number, data=None):
        guest_info = await self.db.guests.find_one({"badge_number": badge_number})

        if guest_info is None:
            await self.db.guests.insert_one({"badge_number": badge_number})
            return await self.guest_update(badge_number, data)

        if data:
            await self.db.guests.update_one(
                {"badge_number": badge_number}, {"$set": data}, upsert=True
            )
            return await self.guest_update(badge_number)

        return guest_info

    async def users_list(self):
        return await self.db.users.find().to_list(length=None)

    async def get_user_by_badge(self, badge_number: str, badge_tariff: str):
        """Get user by badge_number."""
        query = {
            "badge_number": badge_number,
            "badge_tariff": badge_tariff,
        }
        return await self.db.guests.find_one(query)

db = MongoDB()
