from flask import Flask, request, jsonify

app = Flask(__name__)

# Mock database (สมมุติ user id mapping กับ session)
user_sessions = {
    "user1_token": 1,
    "user2_token": 2,
    "user3_token": 3,
}

# Mock user profile data
profiles = {
    1: {"name": "User One", "email": "user1@example.com"},
    2: {"name": "User Two", "email": "user2@example.com"},
    3: {"name": "User Three", "email": "user3@example.com"},
}

@app.route('/profile', methods=['GET'])
def profile():
    # ตัวอย่าง token จำลองว่า user ล็อกอินส่ง token มาด้วย
    token = request.headers.get('Authorization')
    if not token or token not in user_sessions:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = user_sessions[token]  # id ของผู้ใช้ที่ล็อกอิน
    requested_id = int(request.args.get('id', 0))  # id ที่ user พยายามขอ

    if requested_id != user_id:
        return jsonify({"error": "Forbidden: Access Denied"}), 403

    # ถ้า id ตรงกัน = ตอบข้อมูลกลับ
    profile_data = profiles.get(user_id)
    if not profile_data:
        return jsonify({"error": "Profile not found"}), 404

    return jsonify(profile_data), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7000, debug=True)