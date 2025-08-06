from flask import Flask, request, redirect, session, jsonify
import requests, base64, os

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default_secret")

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = "https://spotify-backend-apam.onrender.com/callback"
SCOPE = "user-read-private user-top-read user-read-recently-played playlist-read-private playlist-modify-private playlist-modify-public"

@app.route("/")
def index():
    return '<h2>Spotify Backend is running. <a href="/login">Login with Spotify</a></h2>'

@app.route("/login")
def login():
    auth_url = (
        f"https://accounts.spotify.com/authorize?client_id={CLIENT_ID}"
        f"&response_type=code&redirect_uri={REDIRECT_URI}"
        f"&scope={SCOPE}&show_dialog=true"
    )
    return redirect(auth_url)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    token_url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode(),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }

    r = requests.post(token_url, headers=headers, data=data)
    if r.status_code != 200:
        return "Token exchange failed", 400

    token_info = r.json()
    session["access_token"] = token_info["access_token"]
    session["refresh_token"] = token_info["refresh_token"]
    return "Login successful. You may close this tab."

@app.route("/refresh", methods=["GET"])
def refresh():
    refresh_token = session.get("refresh_token")
    if not refresh_token:
        return "No refresh token found", 401

    token_url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode(),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    r = requests.post(token_url, headers=headers, data=data)
    if r.status_code != 200:
        return "Token refresh failed", 400

    token_info = r.json()
    session["access_token"] = token_info["access_token"]
    return jsonify({"access_token": token_info["access_token"]})

@app.route("/get-top-tracks", methods=["GET"])
def get_top_tracks():
    access_token = session.get("access_token")
    if not access_token:
        return jsonify({"error": "Not authenticated"}), 401

    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    url = "https://api.spotify.com/v1/me/top/tracks?limit=20&time_range=medium_term"
    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        return jsonify({"error": "Failed to fetch top tracks"}), r.status_code

    data = r.json()
    return jsonify(data)

# Update redirect URI for Render deployment
# Fix syntax error on redirect update
# Actually removed broken line
# Final cleanup — no more bad lines
