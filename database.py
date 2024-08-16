import datetime

def log_verification_request(user_id, channel_id, server_id):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] User ID: {user_id}, Channel ID: {channel_id}, Server ID: {server_id}\n"
    
    with open("verification_logs.txt", "a") as log_file:
        log_file.write(log_message)

# Пример использования:
# log_verification_request(123456789, 987654321, 555555555)
