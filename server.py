# server.py (Version 10.1 - FINAL)
import http.server, socketserver, json, mysql.connector, hashlib, time, os, sys
from urllib.parse import urlparse, parse_qs
import os

db_config = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "bitechain_db")
}

DIFFICULTY = 2

def calculate_hash(index, timestamp, review_id, previous_hash, nonce):
    return hashlib.sha256(f"{index}{timestamp}{review_id}{previous_hash}{nonce}".encode()).hexdigest()
def proof_of_work(index, timestamp, review_id, previous_hash):
    nonce = 0
    while True:
        new_hash = calculate_hash(index, timestamp, review_id, previous_hash, nonce)
        if new_hash.startswith('0' * DIFFICULTY): return nonce, new_hash
        nonce += 1

# In a PyInstaller build, bundled HTML/CSS/JS files are extracted to sys._MEIPASS.
# When running normally, serve files from the folder containing server.py.
BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

class BiteChainAPIHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)
    def do_POST(self):
        content_length = int(self.headers['Content-Length']); post_data = self.rfile.read(content_length); data = json.loads(post_data)
        if self.path == '/api/submit-review':
            try:
                conn = mysql.connector.connect(**db_config); cursor = conn.cursor()
                username = data.get('username', 'anonymous')
                cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                user_result = cursor.fetchone()
                if user_result: user_id = user_result[0]
                else: cursor.execute("INSERT INTO users (username) VALUES (%s)", (username,)); user_id = cursor.lastrowid
                cursor.execute("INSERT INTO reviews (restaurant_id, user_id, rating, feedback_text) VALUES (%s, %s, %s, %s)", (data['restaurant_id'], user_id, data['rating'], data['feedback']))
                new_review_id = cursor.lastrowid
                cursor.execute("SELECT id, hash FROM blockchain ORDER BY id DESC LIMIT 1"); last_block_id, previous_hash = cursor.fetchone()
                new_block_index, timestamp = last_block_id + 1, int(time.time())
                print(f"Mining block {new_block_index} for review {new_review_id}..."); nonce, new_hash = proof_of_work(new_block_index, timestamp, new_review_id, previous_hash); print(f"Block mined! Hash: {new_hash}")
                cursor.execute("INSERT INTO blockchain VALUES (%s, %s, %s, %s, %s, %s)", (new_block_index, timestamp, new_review_id, previous_hash, nonce, new_hash))
                conn.commit(); cursor.close(); conn.close()
                self.send_json_response(201, {'message': 'Review submitted and secured on the BiteChain!'})
            except Exception as e: self.send_json_response(500, {'error': str(e)})
        elif self.path == '/api/verify-review':
            try:
                conn = mysql.connector.connect(**db_config); cursor = conn.cursor()
                cursor.execute("UPDATE reviews SET verifications = verifications + 1 WHERE id = %s", (data['review_id'],)); conn.commit()
                cursor.execute("SELECT verifications FROM reviews WHERE id = %s", (data['review_id'],)); new_count = cursor.fetchone()[0]
                cursor.close(); conn.close(); self.send_json_response(200, {'message': 'Verification successful!', 'new_count': new_count})
            except Exception as e: self.send_json_response(500, {'error': str(e)})
        elif self.path == '/api/vote-tag':
            try:
                conn = mysql.connector.connect(**db_config); cursor = conn.cursor()
                cursor.execute("UPDATE restaurant_tags SET votes = votes + 1 WHERE id = %s", (data['tag_id'],)); conn.commit()
                cursor.execute("SELECT votes FROM restaurant_tags WHERE id = %s", (data['tag_id'],)); new_count = cursor.fetchone()[0]
                cursor.close(); conn.close(); self.send_json_response(200, {'message': 'Vote counted!', 'new_count': new_count})
            except Exception as e: self.send_json_response(500, {'error': str(e)})
        else: self.send_error(404, "Not Found")

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path.startswith('/api/'):
            params = parse_qs(parsed_path.query)
            if parsed_path.path == '/api/restaurants':
                try: self.send_json_response(200, self.get_filtered_restaurants(params))
                except Exception as e: self.send_error(500, f"Server Error: {e}")
            elif parsed_path.path == '/api/restaurant-details':
                try: self.send_json_response(200, self.get_single_restaurant_details(int(params['id'][0])))
                except Exception as e: self.send_error(500, f"Server Error: {e}")
            return
        if self.path == '/': self.path = '/login.html'
        return super().do_GET()

    def send_json_response(self, code, data):
        self.send_response(code); self.send_header('Content-type', 'application/json'); self.end_headers(); self.wfile.write(json.dumps(data).encode())
    def get_single_restaurant_details(self, restaurant_id):
        conn = mysql.connector.connect(**db_config); cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM restaurants WHERE id = %s", (restaurant_id,)); restaurant_info = cursor.fetchone()
        cursor.execute("SELECT r.id, r.rating, r.feedback_text, u.username, r.verifications FROM reviews r JOIN users u ON r.user_id = u.id WHERE r.restaurant_id = %s ORDER BY r.creation_date DESC", (restaurant_id,)); reviews_info = cursor.fetchall()
        cursor.execute("SELECT id, tag_name, votes FROM restaurant_tags WHERE restaurant_id = %s ORDER BY votes DESC", (restaurant_id,)); tags_info = cursor.fetchall()
        cursor.close(); conn.close()
        return {'restaurant': restaurant_info, 'reviews': reviews_info, 'tags': tags_info}
    def get_filtered_restaurants(self, params):
        conn = mysql.connector.connect(**db_config); cursor = conn.cursor(dictionary=True); query, query_params = "SELECT * FROM restaurants WHERE 1=1", []
        if params.get('near_me') == ['true'] and params.get('location'): query += " AND location LIKE %s"; query_params.append(f"%{params['location'][0]}%")
        if 'dietary' in params: query += " AND dietary_info LIKE %s"; query_params.append(f"%{params['dietary'][0]}%")
        if 'search' in params and params['search'][0]:
            search_term = params['search'][0].lower()
            search_pattern = f"%{search_term}%"
            query += " AND (LOWER(name) LIKE %s OR LOWER(cuisine) LIKE %s OR LOWER(tags) LIKE %s)"
            query_params.extend([search_pattern, search_pattern, search_pattern])
        if params.get('adventure') == ['true']: query += " ORDER BY RAND() LIMIT 1"
        cursor.execute(query, tuple(query_params)); result = cursor.fetchall(); cursor.close(); conn.close(); return result

PORT = 8000
with socketserver.TCPServer(("", PORT), BiteChainAPIHandler) as httpd:
    print(f"✅ BiteChain 10.1 FINAL LIVE at http://localhost:{PORT}")
    httpd.serve_forever()
