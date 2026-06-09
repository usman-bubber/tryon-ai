from flask import Flask, request, jsonify, send_from_directory
import os
import uuid
from model import try_on   # <-- import our AI function

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/tryon', methods=['POST'])
def tryon():
    try:
        if 'user_image' not in request.files:
            return jsonify({"error": "user_image missing"})
        if 'cloth_image' not in request.files:
            return jsonify({"error": "cloth_image missing"})

        user_image  = request.files['user_image']
        cloth_image = request.files['cloth_image']
        product_id  = request.form.get('product_id', 'unknown')

        # Save uploaded files with unique names
        unique_id       = str(uuid.uuid4())[:8]
        user_path       = os.path.join(UPLOAD_FOLDER, f"user_{unique_id}.jpg")
        cloth_path      = os.path.join(UPLOAD_FOLDER, f"cloth_{unique_id}.jpg")
        output_filename = f"result_{unique_id}.jpg"
        output_path     = os.path.join(OUTPUT_FOLDER, output_filename)

        user_image.save(user_path)
        cloth_image.save(cloth_path)

        # ── Run AI model ──
        success, message = try_on(user_path, cloth_path, output_path)

        if success:
            return jsonify({
                "output": f"http://127.0.0.1:5000/outputs/{output_filename}",
                "message": message
            })
        else:
            return jsonify({"error": message})

    except Exception as e:
        return jsonify({"error": str(e)})


# Serve output images to CI4/browser
@app.route('/outputs/<filename>')
def get_output(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

if __name__ == "__main__":
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port, debug=False)