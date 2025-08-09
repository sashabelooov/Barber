from decouple import config
import aiohttp

BASE_URL = config('BASE_URL')


# ✅ create_user() funksiyasi
async def create_user(telegram_id, phone, first_name, language):
    url = f"{BASE_URL}/api/auth/register/"
    language = language.split(' ')[1]  # Masalan: "🇺🇿 Uzbek" => "Uzbek"
    payload = {
        "telegram_id": telegram_id,
        "phone_number": phone,
        "first_name": first_name,
        "language": language
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload) as response:

                if response.status in [200, 201]:
                    print("User created successfully.")
                    return True

                elif response.status == 400:
                    error_data = await response.json()
                    if 'telegram_id' in error_data and "already exist" in error_data['telegram_id'][0]:
                        return None
                    else:
                        return False

                return f"An error occurred: {response.status}"

    except aiohttp.ClientError as e:
        print(f"A network error occurred: {e}")
        return "Network error."


# ✅ is_user_exists() funksiyasi
async def is_user_exists(telegram_id):
    url = f"{BASE_URL}/api/auth/users/if_exists/{telegram_id}/"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:

                if response.status == 200:
                    return await response.json()

                elif response.status == 404:
                    print("User does not exist.")
                    return False

                else:
                    print(f"Unexpected error: {response.status}")
                    return f"An error occurred: {response.status}"

    except aiohttp.ClientError as e:
        print(f"A network error occurred: {e}")
        return "Network error."





async def all_barbers_name():
    url = f"{BASE_URL}/api/auth/users/"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:

                if response.status == 200:
                    data = await response.json()
                    return data

                elif response.status == 404:
                    print("User does not exist.")
                    return False

                else:
                    print(f"Unexpected error: {response.status}")
                    return f"An error occurred: {response.status}"

    except aiohttp.ClientError as e:
        print(f"A network error occurred: {e}")
        return "Network error."