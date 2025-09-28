from flask import Flask, request, render_template, redirect, url_for
import cv2, requests, numpy as np
import os

app = Flask(__name__)
UPLOAD_FOLDER = "static"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    # Redirect all users to the input page
    return redirect(url_for("input_page"))

@app.route("/input")
def input_page():
    cartoon_url = request.args.get("cartoon_url")
    return render_template("index.html", cartoon_url=cartoon_url)

@app.route("/cartoonify", methods=["POST"])
def cartoonify():
    url = request.form.get("url")
    if not url:
        return redirect(url_for("input_page"))

    try:
        response = requests.get(url)
        if response.status_code != 200:
            return redirect(url_for("input_page"))

        img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        if img is None:
            return redirect(url_for("input_page"))

        # Cartoonify process
        g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        g = cv2.medianBlur(g, 5)
        e = cv2.adaptiveThreshold(g, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
        c = cv2.bilateralFilter(img, 9, 250, 250)
        cartoon = cv2.bitwise_and(c, c, mask=e)

        filename = os.path.join(UPLOAD_FOLDER, "cartoon.jpg")
        cv2.imwrite(filename, cartoon)
        return redirect(url_for("input_page", cartoon_url=filename))

    except Exception:
        return redirect(url_for("input_page"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
