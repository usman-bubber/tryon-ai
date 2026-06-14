"""
Virtual Try-On - Maximum Fallback Version
Tries 8 different spaces to ensure one always works
"""

import requests
import base64
import os
import time
import shutil
from pathlib import Path

FASHN_API_KEY     = "YOUR_FASHN_API_KEY"
REPLICATE_API_KEY = "YOUR_REPLICATE_API_KEY"


def _save_result(result, output_path):
    if not result:
        return False
    src = result
    if isinstance(src, (list, tuple)):
        src = src[0]
    if isinstance(src, dict):
        src = src.get("value") or src.get("path") or src.get("url") or ""
    src = str(src)
    if src and os.path.exists(src):
        shutil.copy(src, output_path)
        return True
    return False


def try_on_idmvton(user_image_path, cloth_image_path, output_path):
    try:
        from gradio_client import Client, handle_file
        print("Trying IDM-VTON...")
        client = Client("yisol/IDM-VTON")
        result = client.predict(
            dict={"background": handle_file(user_image_path), "layers": [], "composite": None},
            garm_img=handle_file(cloth_image_path),
            garment_des="upper body clothing",
            is_checked=True,
            is_checked_crop=False,
            denoise_steps=30,
            seed=42,
            api_name="/tryon"
        )
        if _save_result(result, output_path):
            return True, "IDM-VTON success"
    except Exception as e:
        print(f"  IDM-VTON failed: {e}")
    return False, "failed"


def try_on_leffa(user_image_path, cloth_image_path, output_path):
    try:
        from gradio_client import Client, handle_file
        print("Trying Leffa...")
        client = Client("franciszzj/Leffa")
        result = client.predict(
            src_image_path=handle_file(user_image_path),
            ref_image_path=handle_file(cloth_image_path),
            ref_acceleration=False,
            step=50,
            scale=2.5,
            seed=42,
            vt_model_type="viton_hd",
            vt_garment_type="upper_body",
            api_name="/leffa_predict_vt"
        )
        if _save_result(result, output_path):
            return True, "Leffa success"
    except Exception as e:
        print(f"  Leffa failed: {e}")
    return False, "failed"


def try_on_kolors(user_image_path, cloth_image_path, output_path):
    try:
        from gradio_client import Client, handle_file
        print("Trying Kolors...")
        client = Client("Kwai-Kolors/Kolors-Virtual-Try-On")
        result = client.predict(
            human_img=handle_file(user_image_path),
            garm_img=handle_file(cloth_image_path),
            garment_des="upper body clothing",
            api_name="/run"
        )
        if _save_result(result, output_path):
            return True, "Kolors success"
    except Exception as e:
        print(f"  Kolors failed: {e}")
    return False, "failed"


def try_on_ootd(user_image_path, cloth_image_path, output_path):
    try:
        from gradio_client import Client, handle_file
        print("Trying OOTDiffusion...")
        client = Client("levihsu/OOTDiffusion")
        result = client.predict(
            vton_img=handle_file(user_image_path),
            garm_img=handle_file(cloth_image_path),
            n_samples=1,
            n_steps=20,
            image_scale=2.0,
            seed=-1,
            api_name="/process_hd"
        )
        if _save_result(result, output_path):
            return True, "OOTDiffusion success"
    except Exception as e:
        print(f"  OOTDiffusion failed: {e}")
    return False, "failed"


def try_on_catvton(user_image_path, cloth_image_path, output_path):
    try:
        from gradio_client import Client, handle_file
        print("Trying CatVTON...")
        client = Client("zhengchong/CatVTON")
        result = client.predict(
            image=handle_file(user_image_path),
            condition_image=handle_file(cloth_image_path),
            mask=None,
            num_inference_steps=50,
            guidance_scale=2.5,
            seed=42,
            show_type="result only",
            api_name="/submit"
        )
        if _save_result(result, output_path):
            return True, "CatVTON success"
    except Exception as e:
        print(f"  CatVTON failed: {e}")
    return False, "failed"


def try_on_viton(user_image_path, cloth_image_path, output_path):
    try:
        from gradio_client import Client, handle_file
        print("Trying HR-VITON...")
        client = Client("postech-cvlab/HR-VITON")
        result = client.predict(
            handle_file(user_image_path),
            handle_file(cloth_image_path),
            api_name="/predict"
        )
        if _save_result(result, output_path):
            return True, "HR-VITON success"
    except Exception as e:
        print(f"  HR-VITON failed: {e}")
    return False, "failed"


def try_on_outfit_anyone(user_image_path, cloth_image_path, output_path):
    try:
        from gradio_client import Client, handle_file
        print("Trying OutfitAnyone...")
        client = Client("HumanAIGC/OutfitAnyone")
        result = client.predict(
            handle_file(user_image_path),
            handle_file(cloth_image_path),
            api_name="/predict"
        )
        if _save_result(result, output_path):
            return True, "OutfitAnyone success"
    except Exception as e:
        print(f"  OutfitAnyone failed: {e}")
    return False, "failed"


def try_on_fashn(user_image_path, cloth_image_path, output_path):
    try:
        def to_b64(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()

        print("Trying FASHN.ai...")
        resp = requests.post(
            "https://api.fashn.ai/v1/run",
            headers={"Authorization": f"Bearer {FASHN_API_KEY}"},
            json={
                "model_image":   f"data:image/jpeg;base64,{to_b64(user_image_path)}",
                "garment_image": f"data:image/jpeg;base64,{to_b64(cloth_image_path)}",
                "category":      "tops",
                "mode":          "balanced",
            },
            timeout=30
        )
        resp.raise_for_status()
        prediction_id = resp.json()["id"]
        for _ in range(60):
            time.sleep(3)
            poll = requests.get(
                f"https://api.fashn.ai/v1/status/{prediction_id}",
                headers={"Authorization": f"Bearer {FASHN_API_KEY}"},
                timeout=10
            )
            data = poll.json()
            if data["status"] == "completed":
                img_resp = requests.get(data["output"][0], timeout=30)
                with open(output_path, "wb") as f:
                    f.write(img_resp.content)
                return True, "FASHN success"
            elif data["status"] == "failed":
                return False, "FASHN failed"
        return False, "FASHN timeout"
    except Exception as e:
        print(f"  FASHN failed: {e}")
    return False, "failed"


def try_on_replicate(user_image_path, cloth_image_path, output_path):
    try:
        import replicate
        os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_KEY
        print("Trying Replicate...")

        def to_b64_url(path):
            ext = Path(path).suffix.lstrip(".")
            with open(path, "rb") as f:
                data = base64.b64encode(f.read()).decode()
            return f"data:image/{ext};base64,{data}"

        output = replicate.run(
            "cuuupid/idm-vton:906425dbca90663ff5427624839572cc56ea7d380343d13e2a4c4b09d3f0c30f",
            input={
                "human_img":       to_b64_url(user_image_path),
                "garm_img":        to_b64_url(cloth_image_path),
                "garment_des":     "upper body clothing",
                "is_checked":      True,
                "is_checked_crop": False,
                "denoise_steps":   30,
                "seed":            42,
            }
        )
        if output:
            resp = requests.get(str(output), timeout=30)
            with open(output_path, "wb") as f:
                f.write(resp.content)
            return True, "Replicate success"
    except Exception as e:
        print(f"  Replicate failed: {e}")
    return False, "failed"


# ── MAIN — tries ALL options until one works ──────────────────────────────────
def try_on(user_image_path, cloth_image_path, output_path):
    print("\n" + "="*50)
    print("Virtual Try-On Starting — Trying all options...")
    print("="*50)

    methods = [
        try_on_idmvton,
        try_on_leffa,
        try_on_kolors,
        try_on_ootd,
        try_on_catvton,
        try_on_viton,
        try_on_outfit_anyone,
    ]

    # Add paid APIs if keys are set
    if FASHN_API_KEY != "YOUR_FASHN_API_KEY":
        methods.append(try_on_fashn)
    if REPLICATE_API_KEY != "YOUR_REPLICATE_API_KEY":
        methods.append(try_on_replicate)

    for method in methods:
        try:
            success, msg = method(user_image_path, cloth_image_path, output_path)
            if success:
                print(f"✅ Success: {msg}")
                return True, msg
        except Exception as e:
            print(f"  Method {method.__name__} crashed: {e}")
            continue

    return False, "All AI spaces are currently offline. Please try again in 10 minutes."