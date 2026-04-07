import requests

GATEWAY_URL = "http://localhost:8000"

def seed_products():
    print("==================================================")
    print("      SEEDING MORE BOOKS AND CLOTHES              ")
    print("==================================================")

    # Need admin token to create products
    # Register/login admin user (staff-service or manager)
    # Actually wait, maybe API Gateway allows creating without auth or we can use admin API
    # Let's check admin login
    resp = requests.post(f"{GATEWAY_URL}/api/staff/auth/login/", json={'email': 'manager@gmail.com', 'password': 'password123'})
    if resp.status_code != 200:
        # try staff
        resp = requests.post(f"{GATEWAY_URL}/api/staff/auth/login/", json={'email': 'staff@gmail.com', 'password': 'password123'})
    
    if resp.status_code != 200:
        print("Could not login as admin/staff!")
        return

    token = resp.json().get('token')
    headers = {'Authorization': f"Token {token}"}
    
    # Categories might be needed. Get a category id.
    cat_resp = requests.get(f"{GATEWAY_URL}/api/categories/")
    category_id = 1
    if cat_resp.status_code == 200:
        cats = cat_resp.json()
        if len(cats) > 0:
            category_id = cats[0]['id']

    # Books
    books = [
        {"title": "Clean Code", "author": "Robert C. Martin", "description": "A Handbook of Agile Software Craftsmanship", "price": "450000", "stock": 100, "category_id": category_id, "cover_url": "https://example.com/clean.jpg"},
        {"title": "Design Patterns", "author": "Erich Gamma", "description": "Elements of Reusable Object-Oriented Software", "price": "500000", "stock": 50, "category_id": category_id, "cover_url": "https://example.com/dp.jpg"},
        {"title": "Pragmatic Programmer", "author": "Andrew Hunt", "description": "From Journeyman to Master", "price": "400000", "stock": 30, "category_id": category_id, "cover_url": "https://example.com/prag.jpg"},
        {"title": "Cracking the Coding Interview", "author": "David Thomas", "description": "A great book for developers.", "price": "350000", "stock": 10, "category_id": category_id, "cover_url": "https://example.com/crack.jpg"}
    ]
    
    for b in books:
        r = requests.post(f"{GATEWAY_URL}/admin-panel/api/books/", json=b, headers=headers)
        if r.status_code in [200, 201]:
            print(f"Added book: {b['title']}")
        elif r.status_code == 404:
            # Maybe the path is wrong. Let's try direct book service if gateway admin route is different.
            print("Admin endpoint not working, trying direct create...")
            break

if __name__ == "__main__":
    seed_products()