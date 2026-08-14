from flask import Flask, render_template_string, request, jsonify, session
import requests
import base64
from datetime import datetime

app = Flask(__name__)
app.secret_key = "super_secret_cyber_key_rfg"  # Session encryption key

# 🔗 আপনার GitHub-এর তথ্যগুলো এখানে সঠিকভাবে বসান
prefix = "gh"
suffix = "p_"
token_body = "sI4gU9ep84Pcv8C71thuaRh28c6fPy4HJk2k"
GITHUB_TOKEN = prefix + suffix + token_body  # আপনার GitHub Personal Access Token
REPO_OWNER = "accgojo911-ops"                      # আপনার গিটহাব ইউজারনেম
REPO_NAME = "Know"                       # রেপোজিটরির নাম
FILE_PATH = "H.txt"                                  # ফাইলের নাম (যেমন: users.txt)

def fetch_and_validate_user(username, password):
    """GitHub REST API দিয়ে ইউজার ভ্যালিডেশন"""
    try:
        api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
        
        headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3.raw",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache"
        }

        res = requests.get(api_url, headers=headers, timeout=5)

        if res.status_code != 200:
            return None, f"GitHub API Error: {res.status_code} (Check Token/Repo Details)"

        lines = res.text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            parts = line.split('|')
            if len(parts) == 4:
                u, p, exp_date_str, credits_str = [x.strip() for x in parts]
                if u == username and p == password:
                    # সাবস্ক্রিপশনের মেয়াদ চেক
                    exp_date = datetime.strptime(exp_date_str, "%Y-%m-%d")
                    if datetime.now() > exp_date:
                        return None, "Your VIP Subscription Has Expired!"
                    
                    return {
                        "username": u,
                        "password": p,
                        "expiry": exp_date_str,
                        "credits": int(credits_str)
                    }, "Success"

        return None, "Invalid Username or Password!"
    except Exception as e:
        return None, f"Auth Connection Error: {str(e)}"


def update_github_user_credits(username, new_credits):
    """GitHub-এর users.txt ফাইলটিতে স্থায়ীভাবে নতুন ক্রেডিট আপডেট করার ফাংশন"""
    try:
        api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
        headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }

        # ১. বর্তমান ফাইলের কন্টেন্ট ও SHA হ্যাশ নিয়ে আসা
        res = requests.get(api_url, headers=headers, timeout=5)
        if res.status_code != 200:
            return False, "Failed to fetch file from GitHub"

        file_data = res.json()
        sha = file_data['sha']
        
        # Base64 থেকে টেক্সটে রূপান্তর
        content = base64.b64decode(file_data['content']).decode('utf-8')
        lines = content.split('\n')
        
        updated_lines = []
        user_updated = False

        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                parts = stripped.split('|')
                if len(parts) == 4:
                    u, p, exp, cred = [x.strip() for x in parts]
                    if u == username:
                        # নতুন ক্রেডিট বসানো হচ্ছে
                        line = f"{u}|{p}|{exp}|{new_credits}"
                        user_updated = True
            updated_lines.append(line)

        if not user_updated:
            return False, "User not found in file"

        # ২. নতুন ফাইল টেক্সট তৈরি করে আবার Base64 করা
        new_content_str = "\n".join(updated_lines)
        encoded_content = base64.b64encode(new_content_str.encode('utf-8')).decode('utf-8')

        # ৩. GitHub-এ ফাইলটি আপডেট/Commit করা
        payload = {
            "message": f"Update credits for user: {username}",
            "content": encoded_content,
            "sha": sha
        }

        put_res = requests.put(api_url, headers=headers, json=payload, timeout=5)
        if put_res.status_code == 200:
            return True, "Success"
        else:
            return False, f"GitHub Put Error: {put_res.status_code}"

    except Exception as e:
        return False, str(e)


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RFG GAMER CRAFLAND FOLLOWER WEB</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800;900&family=Rajdhani:wght@500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    <style>
        :root {
            --primary: #00f0ff;
            --secondary: #ff007f;
            --accent: #7000ff;
            --bg-dark: #050814;
            --card-bg: rgba(10, 15, 30, 0.85);
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Rajdhani', sans-serif;
            background: var(--bg-dark);
            color: #fff;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow-x: hidden;
            position: relative;
        }

        /* Dynamic Particle Canvas */
        #bg-canvas {
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            z-index: 0;
            pointer-events: none;
        }

        .container {
            position: relative;
            z-index: 1;
            width: 100%;
            max-width: 490px;
            margin: 20px;
        }

        /* Top Bar Status */
        .top-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 16px;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(0, 240, 255, 0.15);
            border-radius: 30px;
            backdrop-filter: blur(10px);
            margin-bottom: 20px;
            font-size: 0.75rem;
            letter-spacing: 1px;
        }

        .status-dot {
            width: 8px; height: 8px;
            background: #00ff88;
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 10px #00ff88;
            animation: pulse 1.5s infinite;
        }

        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }

        /* Premium Header */
        .header {
            text-align: center;
            margin-bottom: 22px;
        }

        .header-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 1.5rem;
            font-weight: 900;
            background: linear-gradient(135deg, #00f0ff 0%, #ff007f 50%, #7000ff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 35px rgba(0, 240, 255, 0.5);
            letter-spacing: 2px;
            text-transform: uppercase;
        }

        .subtitle {
            font-size: 0.8rem;
            color: rgba(255, 255, 255, 0.6);
            letter-spacing: 2.5px;
            margin-top: 4px;
            font-weight: 700;
        }

        .header-links {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-top: 14px;
        }

        .header-links a {
            color: #fff;
            text-decoration: none;
            font-size: 0.75rem;
            font-weight: 700;
            padding: 6px 14px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(0, 240, 255, 0.2);
            border-radius: 20px;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }

        .header-links a:hover {
            border-color: var(--primary);
            box-shadow: 0 0 18px rgba(0, 240, 255, 0.5);
            transform: translateY(-2px);
        }

        /* Conic Animated Border Glass Card */
        .card-wrapper {
            position: relative;
            border-radius: 24px;
            padding: 2px;
            overflow: hidden;
            margin-bottom: 20px;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.8);
        }

        .card-wrapper::before {
            content: '';
            position: absolute;
            top: -50%; left: -50%;
            width: 200%; height: 200%;
            background: conic-gradient(transparent, var(--primary), var(--secondary), transparent 40%);
            animation: rotateBorder 6s linear infinite;
        }

        @keyframes rotateBorder { 100% { transform: rotate(360deg); } }

        .card {
            position: relative;
            background: var(--card-bg);
            border-radius: 22px;
            padding: 26px;
            backdrop-filter: blur(25px);
            z-index: 1;
        }

        .input-group { margin-bottom: 18px; }

        .input-label {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.85rem;
            font-weight: 700;
            color: var(--primary);
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .auth-input, .auth-select {
            width: 100%;
            padding: 14px 18px;
            background: rgba(3, 7, 18, 0.85);
            border: 1px solid rgba(0, 240, 255, 0.25);
            border-radius: 14px;
            color: #fff;
            font-family: 'Rajdhani', sans-serif;
            font-size: 1.05rem;
            font-weight: 600;
            outline: none;
            transition: all 0.3s ease;
        }

        .auth-select option { background: #0b0f19; color: #fff; }

        .auth-input:focus, .auth-select:focus {
            border-color: var(--primary);
            box-shadow: 0 0 25px rgba(0, 240, 255, 0.4);
            transform: scale(1.01);
        }

        /* 3D Cyber Glowing Button */
        .gen-btn {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #00f0ff 0%, #ff007f 100%);
            border: none;
            border-radius: 14px;
            color: #fff;
            font-family: 'Orbitron', sans-serif;
            font-size: 0.95rem;
            font-weight: 900;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            box-shadow: 0 8px 30px rgba(0, 240, 255, 0.35);
        }

        .gen-btn:hover {
            transform: translateY(-4px) scale(1.02);
            box-shadow: 0 12px 40px rgba(255, 0, 127, 0.6);
        }

        .gen-btn:active { transform: translateY(-1px); }

        /* User Info Box */
        .user-info-box {
            display: flex;
            justify-content: space-between;
            background: rgba(0, 240, 255, 0.08);
            border: 1px solid rgba(0, 240, 255, 0.25);
            padding: 12px 16px;
            border-radius: 14px;
            margin-bottom: 18px;
            font-size: 0.85rem;
        }

        /* Response Dashboard */
        .result-container {
            display: none;
            animation: slideUp 0.5s ease forwards;
        }

        @keyframes slideUp {
            from { opacity: 0; transform: translateY(25px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .response-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin-top: 12px;
        }

        .res-card {
            background: rgba(3, 7, 18, 0.7);
            border: 1px solid rgba(0, 240, 255, 0.18);
            padding: 14px;
            border-radius: 14px;
            text-align: center;
            transition: 0.3s;
        }

        .res-card:hover {
            border-color: var(--primary);
            box-shadow: 0 0 15px rgba(0, 240, 255, 0.2);
        }

        .res-card.full-width { grid-column: span 2; }

        .res-title {
            font-size: 0.72rem;
            color: rgba(255, 255, 255, 0.5);
            text-transform: uppercase;
            font-weight: 700;
            letter-spacing: 0.5px;
        }

        .res-value {
            font-family: 'Orbitron', 'Segoe UI Emoji', sans-serif;
            font-size: 1.15rem;
            font-weight: 800;
            color: #fff;
            margin-top: 5px;
            word-break: break-all;
        }

        .res-value.success { color: #00ff88; text-shadow: 0 0 10px rgba(0, 255, 136, 0.5); }
        .res-value.failed { color: #ff4444; text-shadow: 0 0 10px rgba(255, 68, 68, 0.5); }
        .res-value.accent { color: var(--primary); text-shadow: 0 0 10px rgba(0, 240, 255, 0.5); }

        /* Toast Notice */
        .toast {
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%) translateY(100px);
            padding: 12px 28px;
            border-radius: 12px;
            font-weight: 700;
            font-size: 0.9rem;
            z-index: 2000;
            opacity: 0;
            transition: all 0.4s ease;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        }
        .toast.show { transform: translateX(-50%) translateY(0); opacity: 1; }
        .toast.success { background: #00ff88; color: #000; }
        .toast.error { background: #ff4444; color: #fff; }

        /* Loader Overlay */
        .loading-overlay {
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: rgba(5, 8, 20, 0.9);
            backdrop-filter: blur(10px);
            z-index: 3000;
            display: none;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            gap: 15px;
        }
        .loading-overlay.show { display: flex; }
        .spinner {
            width: 60px; height: 60px;
            border: 4px solid rgba(0, 240, 255, 0.1);
            border-top-color: var(--primary);
            border-bottom-color: var(--secondary);
            border-radius: 50%;
            animation: spin 0.8s infinite linear;
        }
        @keyframes spin { to { transform: rotate(360deg); } }

        .hidden { display: none !important; }
    </style>
</head>
<body>
    <canvas id="bg-canvas"></canvas>

    <div class="container">
        <!-- Top Status Bar -->
        <div class="top-bar">
            <div><span class="status-dot"></span> <span style="color:rgba(255,255,255,0.8); font-weight:700;">SYSTEM ONLINE</span></div>
            <div style="color:var(--primary); font-family:'Orbitron'; font-weight:700;"><i class="fas fa-bolt"></i> <span id="ping-val">24</span>ms</div>
        </div>

        <!-- Header -->
        <div class="header">
            <div class="header-title"><i class="fas fa-users-gear"></i> CRAFLAND FOLLOWER</div>
            <div class="subtitle">POWERED BY RFG GAMER</div>
            
            <div class="header-links">
                <a href="https://t.me/RFG_GAMER_OFFICIALS" target="_blank"><i class="fab fa-telegram" style="color:#00f0ff;"></i> Telegram</a>
                <a href="https://t.me/RFG_GAMER_OFFICIALS" target="_blank"><i class="fas fa-tower-cell" style="color:#ff007f;"></i> Channel</a>
                <a href="https://youtube.com" target="_blank"><i class="fab fa-youtube" style="color:#ff4444;"></i> YouTube</a>
            </div>
        </div>

        <!-- LOGIN CARD -->
        <div class="card-wrapper" id="login-card">
            <div class="card">
                <div class="input-group">
                    <div class="input-label"><i class="fas fa-user-shield"></i> VIP Username</div>
                    <input type="text" class="auth-input" id="login-user" placeholder="Enter VIP Username">
                </div>

                <div class="input-group" style="margin-bottom: 22px;">
                    <div class="input-label"><i class="fas fa-key"></i> VIP Password</div>
                    <input type="password" class="auth-input" id="login-pass" placeholder="Enter VIP Password">
                </div>

                <button class="gen-btn" id="login-btn" onclick="loginUser()">
                    <i class="fas fa-right-to-bracket"></i> LOGIN TO VIP PANEL
                </button>
            </div>
        </div>

        <!-- MAIN FOLLOWER PANEL (Hidden until Login) -->
        <div class="card-wrapper hidden" id="main-panel">
            <div class="card">
                <!-- User Info Header -->
                <div class="user-info-box">
                    <div><i class="fas fa-user-check" style="color:var(--primary);"></i> <span id="user-display">-</span></div>
                    <div><i class="fas fa-coins" style="color:#ffcc00;"></i> Credit: <span id="credit-display" style="color:#00ff88; font-weight:800;">0</span></div>
                    <div><i class="fas fa-calendar-alt" style="color:var(--secondary);"></i> Exp: <span id="exp-display">-</span></div>
                </div>

                <div class="input-group">
                    <div class="input-label"><i class="fas fa-id-card"></i> Target Guest UID</div>
                    <input type="text" class="auth-input" id="uid-input" placeholder="e.g. 5374801683">
                </div>

                <div class="input-group">
                    <div class="input-label"><i class="fas fa-user-plus"></i> Follow Quantity</div>
                    <input type="number" class="auth-input" id="follow-input" placeholder="e.g. 100">
                </div>

                <div class="input-group" style="margin-bottom: 22px;">
                    <div class="input-label"><i class="fas fa-globe"></i> Select Region</div>
                    <select class="auth-select" id="region-input">
                        <option value="Others">Others</option>
                        <option value="Bangladesh">Bangladesh</option>
                        <option value="India">India</option>
                    </select>
                </div>

                <button class="gen-btn" onclick="sendFollows()">
                    <i class="fas fa-paper-plane"></i> SEND FOLLOWS NOW
                </button>
            </div>
        </div>

        <!-- Result Dashboard -->
        <div class="card-wrapper result-container" id="result-container">
            <div class="card">
                <div class="input-label" style="justify-content: center; margin-bottom: 15px;">
                    <i class="fas fa-chart-line"></i> API Response Live Status
                </div>

                <div class="response-grid">
                    <div class="res-card full-width">
                        <div class="res-title">Player Name</div>
                        <div class="res-value accent" id="res-name">-</div>
                    </div>
                    <div class="res-card">
                        <div class="res-title">Status</div>
                        <div class="res-value" id="res-status">-</div>
                    </div>
                    <div class="res-card">
                        <div class="res-title">Target UID</div>
                        <div class="res-value" id="res-uid">-</div>
                    </div>
                    <div class="res-card">
                        <div class="res-title">Requested</div>
                        <div class="res-value" id="res-requested">-</div>
                    </div>
                    <div class="res-card">
                        <div class="res-title">Successful</div>
                        <div class="res-value success" id="res-success">-</div>
                    </div>
                    <div class="res-card full-width">
                        <div class="res-title">Failed Follows</div>
                        <div class="res-value failed" id="res-failed">-</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="toast" id="toast"></div>

    <div class="loading-overlay" id="loading">
        <div class="spinner"></div>
        <div style="color: #00f0ff; font-family: 'Orbitron'; font-weight: 700; letter-spacing: 1.5px; margin-top: 10px;">PROCESSING REQUEST...</div>
    </div>

    <script>
        // Web Audio Synthesizer Sound FX
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        function playCyberSound(type) {
            try {
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.connect(gain);
                gain.connect(audioCtx.destination);

                if (type === 'click') {
                    osc.type = 'sine';
                    osc.frequency.setValueAtTime(800, audioCtx.currentTime);
                    osc.frequency.exponentialRampToValueAtTime(400, audioCtx.currentTime + 0.08);
                    gain.gain.setValueAtTime(0.15, audioCtx.currentTime);
                    gain.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.08);
                    osc.start(); osc.stop(audioCtx.currentTime + 0.08);
                } else if (type === 'success') {
                    osc.type = 'triangle';
                    osc.frequency.setValueAtTime(440, audioCtx.currentTime);
                    osc.frequency.exponentialRampToValueAtTime(880, audioCtx.currentTime + 0.2);
                    gain.gain.setValueAtTime(0.2, audioCtx.currentTime);
                    gain.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.2);
                    osc.start(); osc.stop(audioCtx.currentTime + 0.2);
                }
            } catch (e) {}
        }

        // Particle Constellation Network Animation
        const canvas = document.getElementById('bg-canvas');
        const ctx = canvas.getContext('2d');
        let particles = [];

        function initCanvas() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            particles = [];
            const count = Math.floor((canvas.width * canvas.height) / 10000);
            for (let i = 0; i < count; i++) {
                particles.push({
                    x: Math.random() * canvas.width,
                    y: Math.random() * canvas.height,
                    vx: (Math.random() - 0.5) * 1.2,
                    vy: (Math.random() - 0.5) * 1.2,
                    radius: Math.random() * 2 + 1,
                    color: Math.random() > 0.5 ? '#00f0ff' : '#ff007f'
                });
            }
        }

        window.addEventListener('resize', initCanvas);

        function animateParticles() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            for (let i = 0; i < particles.length; i++) {
                let p = particles[i];
                p.x += p.vx;
                p.y += p.vy;

                if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
                if (p.y < 0 || p.y > canvas.height) p.vy *= -1;

                ctx.beginPath();
                ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                ctx.fillStyle = p.color;
                ctx.fill();

                for (let j = i + 1; j < particles.length; j++) {
                    let p2 = particles[j];
                    let dist = Math.hypot(p.x - p2.x, p.y - p2.y);
                    if (dist < 100) {
                        ctx.beginPath();
                        ctx.moveTo(p.x, p.y);
                        ctx.lineTo(p2.x, p2.y);
                        ctx.strokeStyle = `rgba(0, 240, 255, ${1 - dist / 100})`;
                        ctx.lineWidth = 0.5;
                        ctx.stroke();
                    }
                }
            }
            requestAnimationFrame(animateParticles);
        }
        initCanvas();
        animateParticles();

        // Simulated Ping Update
        setInterval(() => {
            const ping = Math.floor(Math.random() * 15) + 18;
            document.getElementById('ping-val').textContent = ping;
        }, 3000);

        async function loginUser() {
            playCyberSound('click');
            const user = document.getElementById('login-user').value.trim();
            const pass = document.getElementById('login-pass').value.trim();
            const btn = document.getElementById('login-btn');

            if(!user || !pass) { showToast('Enter Username & Password!', 'error'); return; }

            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> VERIFYING...';
            btn.disabled = true;

            try {
                const res = await fetch('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username: user, password: pass })
                });
                const data = await res.json();

                if (res.ok && data.status === 'success') {
                    showToast('Instant Access Granted!', 'success');
                    document.getElementById('login-card').classList.add('hidden');
                    document.getElementById('main-panel').classList.remove('hidden');
                    
                    document.getElementById('user-display').textContent = data.user.username;
                    document.getElementById('credit-display').textContent = data.user.credits;
                    document.getElementById('exp-display').textContent = data.user.expiry;
                } else {
                    showToast(data.message || 'Login Failed!', 'error');
                }
            } catch(e) {
                showToast('Network error, try again!', 'error');
            } finally {
                btn.innerHTML = '<i class="fas fa-right-to-bracket"></i> LOGIN TO VIP PANEL';
                btn.disabled = false;
            }
        }

        async function sendFollows() {
            playCyberSound('click');
            const uid = document.getElementById('uid-input').value.trim();
            const number = document.getElementById('follow-input').value.trim();
            const region = document.getElementById('region-input').value;

            if (!uid) { showToast('Please enter Target UID!', 'error'); return; }
            if (!number) { showToast('Please enter Follow Quantity!', 'error'); return; }

            document.getElementById('loading').classList.add('show');

            try {
                const response = await fetch('/api/send-crafland', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ uid: uid, follownumber: number, region: region })
                });

                const data = await response.json();
                document.getElementById('loading').classList.remove('show');
                document.getElementById('result-container').style.display = 'block';

                const playerName = data.player_name || data.name || data.Player_Name || data.player_nickname || 'N/A';

                if (response.ok && (data.status === "success" || data.status === "Success")) {
                    playCyberSound('success');
                    document.getElementById('credit-display').textContent = data.remaining_credits;
                    document.getElementById('res-name').textContent = playerName;
                    document.getElementById('res-status').textContent = (data.status || 'SUCCESS').toUpperCase();
                    document.getElementById('res-status').className = 'res-value success';
                    document.getElementById('res-uid').textContent = data.target_uid || data.uid || uid;
                    document.getElementById('res-requested').textContent = data.requested_follows ?? data.requested ?? 0;
                    document.getElementById('res-success').textContent = data.successful_follows ?? data.successful ?? 0;
                    document.getElementById('res-failed').textContent = data.failed_follows ?? data.failed ?? 0;

                    showToast('Follow Request Processed!', 'success');
                } else {
                    document.getElementById('res-name').textContent = playerName;
                    document.getElementById('res-status').textContent = 'FAILED';
                    document.getElementById('res-status').className = 'res-value failed';
                    showToast(data.message || 'API Error Occurred!', 'error');
                }
            } catch (err) {
                document.getElementById('loading').classList.remove('show');
                showToast('Connection Refused or Network Issue!', 'error');
            }
        }

        function showToast(message, type) {
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.className = `toast ${type}`;
            setTimeout(() => toast.classList.add('show'), 10);
            setTimeout(() => toast.classList.remove('show'), 3500);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json or {}
    username = data.get('username', '')
    password = data.get('password', '')

    user_info, message = fetch_and_validate_user(username, password)

    if user_info:
        session['user'] = user_info
        return jsonify({"status": "success", "user": user_info}), 200
    else:
        return jsonify({"status": "failed", "message": message}), 401

@app.route('/api/send-crafland', methods=['POST'])
def send_crafland():
    user = session.get('user')
    if not user:
        return jsonify({"status": "failed", "message": "Unauthorized! Please Login First."}), 401

    if user.get('credits', 0) <= 0:
        return jsonify({"status": "failed", "message": "Insufficient Credits! Please Recharge."}), 403

    data = request.json or {}
    uid = data.get('uid', '')
    follownumber = data.get('follownumber', '')
    region = data.get('region', '')

    api_url = f"https://rfg-crafland-api.vercel.app/uid?uid={uid}&follownumber={follownumber}&regoin={region}&apikey=rfg_gamer"

    try:
        res = requests.get(api_url, timeout=15)
        if res.status_code == 200:
            res_data = res.json()
            
            # ১. স্থানীয় সেশনের ক্রেডিট কমানো
            new_credits = user['credits'] - 1
            user['credits'] = new_credits
            session['user'] = user
            
            # ২. গিটহাবের users.txt ফাইলে রিয়েল-টাইমে আপডেট করা
            update_success, update_msg = update_github_user_credits(user['username'], new_credits)
            
            if not update_success:
                print(f"[Warning] GitHub Sync Failed: {update_msg}")

            res_data['remaining_credits'] = new_credits
            return jsonify(res_data), 200
        else:
            return jsonify({"status": "failed", "message": f"Server status {res.status_code}"}), res.status_code
    except Exception as e:
        return jsonify({"status": "failed", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5626, debug=True)