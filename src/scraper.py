import os
import json
import logging
from datetime import datetime
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from dotenv import load_dotenv

# Load environment variables
load_dotenv(r"C:\Users\hp\Desktop\medical-telegram-warehouse\medical-telegram-warehouse\.env")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(r'logs/scraper.log'),
        logging.StreamHandler()
    ]
)

# Telegram API credentials from .env
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
phone = os.getenv('PHONE')

# List of channels to scrape (usernames without @)
channels = ['chemed123', 'lobelia4cosmetics', 'tikvahpharma', 'ethiopharmaceutical', 'healthisssue', 'DoctorsEthiopia', 'HakimEthio', 'EMSA_ETHIOPIA']

async def main():
    # Create Telegram client (session file will be created automatically, ignored in .gitignore)
    client = TelegramClient('scraper_session', api_id, api_hash)
    
    try:
        await client.start(phone=phone)
        if not await client.is_user_authorized():
            await client.send_code_request(phone)
            try:
                await client.sign_in(phone, input('Enter the code: '))
            except SessionPasswordNeededError:
                await client.sign_in(password=input('Enter password: '))
        
        logging.info("Client authorized successfully.")
        
        for channel in channels:
            try:
                entity = await client.get_entity(channel)
                channel_name = entity.username or entity.title
                
                # Create directories
                date_str = datetime.now().strftime('%Y-%m-%d')
                json_dir = f'data/raw/telegram_messages/{date_str}'
                os.makedirs(json_dir, exist_ok=True)
                image_dir = f'data/raw/images/{channel_name}'
                os.makedirs(image_dir, exist_ok=True)
                
                messages = []
                async for message in client.iter_messages(entity, limit=100):  # Adjust limit as needed
                    data = {
                        'message_id': message.id,
                        'channel_name': channel_name,
                        'message_date': message.date.isoformat(),
                        'message_text': message.text,
                        'has_media': message.media is not None,
                        'views': message.views,
                        'forwards': message.forwards,
                        'image_path': None
                    }
                    
                    if message.photo:
                        image_path = f'{image_dir}/{message.id}.jpg'
                        await message.download_media(file=image_path)
                        data['image_path'] = image_path
                        logging.info(f"Downloaded image for message {message.id} in {channel}")
                    
                    messages.append(data)
                
                # Save as JSON
                json_path = f'{json_dir}/{channel_name}.json'
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(messages, f, ensure_ascii=False, indent=4)
                logging.info(f"Saved {len(messages)} messages for {channel_name}")
            
            except Exception as e:
                logging.error(f"Error scraping {channel}: {str(e)}")
    
    except Exception as e:
        logging.error(f"Client error: {str(e)}")

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())