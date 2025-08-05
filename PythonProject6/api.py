from decouple import config
import requests

BASE_URL = config('BASE_URL')




def create_user(telegram_id, phone, name, lang):
    url = f"{BASE_URL}/api/auth/user-data/"

    if " " in lang:
         lang = lang.split(" ")[1]

    payload = {
        "tg_id": telegram_id,
        "phone_number": phone,
        "name": name,
        "language": lang
    }

    try:
        response = requests.post(url=url, data=payload)

        if response.status_code == 201:
            print("User created successfully.")
            return True

        if response.status_code == 400:
            error_data = response.json()
            if 'telegram_id' in error_data and "already exist" in error_data['telegram_id'][0]:
                return "User already exists."
            else:
                return "Error"

        return f"An error occurred: {response.status_code}"

    except requests.exceptions.RequestException as e:
        print(f"A network error occurred: {e}")
        return (False, "Network error.")




def get_user_info_by_tg_id(telegram_id):
    url = f"{BASE_URL}/api/auth/user-data/one_user_data/?{telegram_id}"

    params = {
        "tg_id": telegram_id
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            print(response.json())
            return response.json()
        else:
            return False, f"Failed to get user info. Status: {response.status_code}, Response: {response.text}"
    except Exception as e:
        return False, f"Request failed with exception: {str(e)}"