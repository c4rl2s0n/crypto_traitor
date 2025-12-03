from channels.generic.websocket import AsyncJsonWebsocketConsumer

class LiveConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        print("WS Connected")
        await self.channel_layer.group_add("live", self.channel_name)
        await self.accept()
        # send initial state
        await self.send_json({
            "type": "update",
            "values": [1, 2, 3, 4]
        })


    async def disconnect(self, code):
        print("WS Disconnected")
        await self.channel_layer.group_discard("live", self.channel_name)

    async def push_update(self, event):
        await self.send_json({
            "type": "update",
            "value": event["value"]
        })
