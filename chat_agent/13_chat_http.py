import requests  # Import requests library

# Base URL of the API (example)
BASE_URL = "https://jsonplaceholder.typicode.com/posts"

# Custom headers (you can add authentication or any other header here)
headers = {
    "Authorization": "Bearer YOUR_TOKEN_HERE",  # Example custom token
    "Content-Type": "application/json",          # Tell server we send JSON
    "X-Custom-Header": "MyCustomValue"           # Add your own variables
}

# Custom query parameters (appended to URL as ?key=value)
params = {
    "userId": 1,
    "sort": "desc"
}

# Custom JSON payload for POST/PUT/PATCH
payload = {
    "title": "My New Post",
    "body": "This is the content of my post.",
    "userId": 1
}

# -------------------
# 1. GET Request
# -------------------
# Fetch data from API with headers + query parameters
response_get = requests.get(BASE_URL, headers=headers, params=params)
print("GET Response:", response_get.json())

# -------------------
# 2. POST Request
# -------------------
# Create a new resource by sending a payload
response_post = requests.post(BASE_URL, headers=headers, json=payload)
print("POST Response:", response_post.json())

# -------------------
# 3. PUT Request
# -------------------
# Replace an existing resource (e.g., post with ID 1)
response_put = requests.put(f"{BASE_URL}/1", headers=headers, json=payload)
print("PUT Response:", response_put.json())

# -------------------
# 4. PATCH Request
# -------------------
# Partially update an existing resource
patch_payload = {"title": "Updated Title Only"}
response_patch = requests.patch(f"{BASE_URL}/1", headers=headers, json=patch_payload)
print("PATCH Response:", response_patch.json())

# -------------------
# 5. DELETE Request
# -------------------
# Delete a resource (e.g., post with ID 1)
response_delete = requests.delete(f"{BASE_URL}/1", headers=headers)
print("DELETE Response:", response_delete.status_code)  # Usually 200 or 204
