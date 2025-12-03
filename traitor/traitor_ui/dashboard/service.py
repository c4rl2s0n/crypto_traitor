import threading
import time
import random
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def start_random_service():
    def loop():
        layer = get_channel_layer()
        while True:
            value = random.randint(0, 100)
            async_to_sync(layer.group_send)(
                "live",
                {"type": "push_update", "value": value},
            )
            time.sleep(0.3)
    t = threading.Thread(target=loop, daemon=True)
    t.start()
