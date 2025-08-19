import json

from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Подключаемся к уведомлениям для пользователя
        if self.scope["user"].is_anonymous:
            await self.close()
        else:
            await self.channel_layer.group_add( # type: ignore
                f"user_{self.scope['user'].id}",
                self.channel_name
            )

        # Подключаемся к общему каналу списка задач
        await self.channel_layer.group_add("tasks_list", self.channel_name) # type: ignore

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("tasks_list", self.channel_name) # type: ignore
        if not self.scope["user"].is_anonymous:
            await self.channel_layer.group_discard( # type: ignore
                f"user_{self.scope['user'].id}",
                self.channel_name
            )

    # Для уведомлений пользователю
    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            "type": "notification",
            "message": event["message"]
        }))

    # Для обновления списка задач
    async def task_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "task_update",
            "action": event["action"],
            "task": event["task"]
        }))