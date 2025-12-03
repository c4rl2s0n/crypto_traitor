import threading

import traitor



# --- Start threads ---
threads = [
    # webserver
    threading.Thread(target=traitor.app.run_webserver),
    # trading bot lifecycle
    #threading.Thread(target=traitor.app.run)
]

for thread in threads:
    thread.run()

# for thread in threads:
#     thread.join()
