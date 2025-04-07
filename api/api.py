from flask import Flask, request, jsonify
import requests, time, base64, json

app = Flask(__name__)

def generate_token():
    payload = {
        "timestamp": int(time.time()),
        "referer": "",
        "location": "https://linkvertise.com/"
    }
    encoded = base64.b64encode(json.dumps(payload).encode()).decode()
    return encoded

@app.route("/bypass", methods=["GET"])
def bypass():
    link = request.args.get("url")
    if not link:
        return jsonify({"error": "Parameter url kosong!"}), 400

    try:
        # Extract link ID
        link_id = link.split("/")[-1]

        # Step 1 - static data
        static_url = f"https://publisher.linkvertise.com/api/v1/redirect/link/static/{link_id}"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(static_url, headers=headers)
        if res.status_code != 200:
            return jsonify({"error": "Gagal ambil static data!"}), 500

        # Step 2 - generate token & get target
        token = generate_token()
        target_url = f"https://publisher.linkvertise.com/api/v1/redirect/link/target/{link_id}?X-Linkvertise-UT={token}"
        res2 = requests.get(target_url, headers=headers)
        if res2.status_code != 200:
            return jsonify({"error": "Gagal ambil link target, kemungkinan ada proteksi lanjut!"}), 500

        real_link = res2.json()["data"]["target"]
        return jsonify({"success": True, "link": real_link})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
