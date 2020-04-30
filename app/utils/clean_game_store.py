from datetime import datetime


def clean_game_store(store: dict):
    copy = store.copy()
    for key, item in copy.items():
        if (datetime.now() - item.last_updated).total_seconds() > 600:
            try:
                del store[key]
            except:
                print('Failed to delete id')
        