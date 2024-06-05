import logging
import requests
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Replace with your Telegram bot token
TOKEN = "6636798850:AAHN2eSP_BXwZHBvr8myjdPh2zSroo9rFDc"

# OpenWeatherMap API details (replace with your API key)
API_KEY = "ada4dee7e059ed5a98038882d3756d6b"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# Language code (optional, default is 'en')
LANGUAGE_CODE = "en"

# Units (optional, default is 'metric')
UNITS = "metric"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Responds to the '/start' command with instructions."""
    instructions = (
        "Hi! I'm your weather bot.\n"
        "To get the weather for a location, you can either:\n"
        "  * Type the city name (e.g., London, Tokyo).\n"
        "  * Send me your location using the Google Maps pin button."
    )
    await update.message.reply_text(instructions)


def get_weather_by_city(city_name: str) -> dict:
    """Fetches weather data from OpenWeatherMap API using city name."""
    url = f"{BASE_URL}?q={city_name}&appid={API_KEY}&lang={LANGUAGE_CODE}&units={UNITS}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f"Error fetching weather data for {city_name}: {response.text}")
        return None


def get_weather_by_location(latitude: float, longitude: float) -> dict:
    """Fetches weather data from OpenWeatherMap API using coordinates."""
    url = f"{BASE_URL}?lat={latitude}&lon={longitude}&appid={API_KEY}&lang={LANGUAGE_CODE}&units={UNITS}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f"Error fetching weather data for coordinates: {response.text}")
        return None


def format_weather_data(data: dict) -> str:
    """Formats weather data into a human-readable message."""
    city = data["name"]
    weather_description = data["weather"][0]["description"]
    temperature = data["main"]["temp"]
    feels_like = data["main"]["feels_like"]
    humidity = data["main"]["humidity"]

    return (
        f"**Weather in {city}**\n"
        f"Description: {weather_description}\n"
        f"Temperature: {temperature:.1f}°C (Feels like: {feels_like:.1f}°C)\n"
        f"Humidity: {humidity}%"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles user messages, including text and location data."""
    if update.message.text == "/start":
        await start(update, context)
        return

    text = update.message.text

    # Check if user sends location data
    if update.message.location:
        latitude = update.message.location.latitude
        longitude = update.message.location.longitude
        weather_data = get_weather_by_location(latitude, longitude)
    else:
        weather_data = get_weather_by_city(text)

    if weather_data:
        weather_message = format_weather_data(weather_data)
        await update.message.reply_text(weather_message)
    else:
        await update.message.reply_text("Sorry, I couldn't find the weather for that location.")


def main() -> None:
    """Initializes and starts the Telegram bot."""
    logging.basicConfig(level=logging.INFO)

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT | filters.LOCATION, handle_message))

    application.run_polling()


if __name__ == "__main__":
    main()
