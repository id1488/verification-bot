# Discord Verification Bot

Этот Discord бот предназначен для верификации пользователей через систему форм. Бот использует команду `me.start` для установки канала, в котором пользователи будут отправлять свои заявки.

## Особенности

- **Команда `me.start`**: Устанавливает канал, в котором была прописана команда, как канал для отправки заявок.
- **Система форм**: Пользователи могут отправлять свои заявки через формы для верификации.

## Установка

1. **Клонируйте репозиторий и установите discord.py 2.0**:
   ```bash
   git clone https://github.com/sjskUw/verification-bot.git
   cd discord-verification-bot
   pip install -U discord.py
   ```
 2. **Поменяйте содержимое на свое в setup.txt**
      ```
      TOKEN=YOUR TOKEN
      role_id=YOUR ROLE ID
      logs_id=YOUR LOGS CHANNEL ID
      ```
3. **Запустите бота**
   ```
   python bot.py
   ```
