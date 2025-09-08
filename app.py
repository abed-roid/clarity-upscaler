import os
import subprocess
import base64
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
import glob
app = FastAPI()

OUTPUT_FILE = "/root/clarity-upscaler/output.0.webp"

@app.get("/ping")
async def ping():
    return JSONResponse(content={"message": "pong"}, status_code=200)

@app.post("/upscale")
def upscale(
    image_url: str = Form(...),
    mask_url: str = Form(None)
):
    try:
        # Step 1: Delete old output if exists
        if os.path.exists(OUTPUT_FILE):
            os.remove(OUTPUT_FILE)

        for f in glob.glob(os.path.join("/root/clarity-upscaler", "*.webp")):
            os.remove(f)
        # Step 2: Build command dynamically
        cmd = [
            "cog", "predict",
            "-i", f'image={image_url}',
            "-i", f'mask={mask_url}',
            "-i", 'prompt=masterpiece, best quality, highres, <lora:more_details:.3>',
            "-i", "dynamic=1",
            "-i", "sharpen=0",
            "-i", 'sd_model=epicrealism_naturalSinRC1VAE.safetensors [84d76a0328]',
            "-i", "creativity=0.54",
            "-i", "resemblance=2.2",
            "-i", "scale_factor=2",
            "-i", "tiling_width=112",
            "-i", "tiling_height=144",
            "-i", 'output_format=webp',
            "-i", "negative_prompt=worst quality, low quality, normal quality, lowres, low details, oversaturated, undersaturated, overexposed, underexposed, grayscale, bw, bad photo, bad photography, bad art",
            "-i", "num_inference_steps=20"
        ]

        # Step 3: Execute cog command
        subprocess.run(cmd, check=True)

        # Step 4: Read output file as base64
        if not os.path.exists(OUTPUT_FILE):
            return JSONResponse({"error": "Output file not generated"}, status_code=500)

        with open(OUTPUT_FILE, "rb") as f:
            img_bytes = f.read()
            img_b64 = base64.b64encode(img_bytes).decode("utf-8")

        return img_b64

    except subprocess.CalledProcessError as e:
        return JSONResponse({"error": f"Cog execution failed: {e}"}, status_code=500)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
