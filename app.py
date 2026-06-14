from flask import Flask, request, jsonify, send_from_directory
import os
import uuid
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

        if success:
            # Get Railway domain from environment variable
            base_url = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "")
            if base_url:
                output_url = f"https://{base_url}/outputs/{output_filename}"
            else:
                output_url = f"https://tryon-ai-production.up.railway.app/outputs/{output_filename}"
            
            return jsonify({
                "output": output_url,
                "message": message
            })
        else:
            return jsonify({"error": message})

    except Exception as e:
        return jsonify({"error": str(e)})


@app.route('/outputs/<filename>')
def get_output(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)


@app.route('/')
def index():
    return jsonify({"status": "Virtual Try-On API is running"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)