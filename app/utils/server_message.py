def server_message(message_type: str, message: str):
    return {
        'type': message_type, 'message': message
    }