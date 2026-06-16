from flask import Flask, request, jsonify, send_from_directory
import os
import uuid
import base64
from model import try_on

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

        unique_id       = str(uuid.uuid4())[:8]
        user_path       = os.path.join(UPLOAD_FOLDER, f"user_{unique_id}.jpg")
        cloth_path      = os.path.join(UPLOAD_FOLDER, f"cloth_{unique_id}.jpg")
        output_filename = f"result_{unique_id}.jpg"
        output_path     = os.path.join(OUTPUT_FOLDER, output_filename)

        user_image.save(user_path)
        cloth_image.save(cloth_path)

        success, message = try_on(user_path, cloth_path, output_path)

        # Cleanup uploads
        try:
            os.remove(user_path)
            os.remove(cloth_path)
        except:
            pass

    if success:
        # Return as base64 — Railway deletes files on restart
        with open(output_path, "rb") as f:
            import base64
            img_b64 = base64.b64encode(f.read()).decode('utf-8')
        try:
            os.remove(output_path)
        except:
            pass
        return jsonify({
            "output_base64": img_b64,
            "message": message
        })
        else:
            return jsonify({"error": message})

    except Exception as e:
        return jsonify({"error": str(e)})


@app.route('/')
def index():
    return jsonify({"status": "Virtual Try-On API is running"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
 