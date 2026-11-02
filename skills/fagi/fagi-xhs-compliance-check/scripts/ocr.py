#!/usr/bin/env python3
"""
小红书内容合规检测 — 图片文字识别脚本
用法:
    python3 scripts/ocr.py <图片路径>

依赖:
    - macOS 自带 Vision 框架（通过 pyobjc）
    - 或 pillow + pytesseract（如已安装 tesseract）
    
自动检测可用引擎：macOS Vision > Tesseract > 不可用（返回提示）
"""

import sys
import os
import json
import subprocess
import platform


def extract_text_via_vision(image_path):
    """使用 macOS Vision 框架识别图片文字（最快，最准确）"""
    try:
        import Quartz
        import Vision
        from PIL import Image
        
        img = Image.open(image_path)
        # 将 PIL Image 转为 NSImage
        # 简化为使用命令行工具
        result = subprocess.run(
            ['/usr/bin/xcrun', 'run', 'native', '-e', 
             f'''
             using ImageIO
             using Vision
             
             let img = NSImage(contentsOf: NSURL(fileURLWithPath: "{image_path}"))
             guard let cgImage = img?.cgImage else {{ exit(1) }}
             
             let request = VNRecognizeTextRequest()
             request.recognitionLevel = .accurate
             
             let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
             try handler.perform([request])
             
             guard let observations = request.results else {{ exit(1) }}
             for observation in observations {{
                 print(observation.topCandidates(1).first?.string ?? "")
             }}
             '''],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    return None


def extract_text_via_tesseract(image_path):
    """使用 Tesseract OCR 识别"""
    try:
        import pytesseract
        from PIL import Image
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang='chi_sim+eng')
        return text.strip() if text.strip() else None
    except Exception:
        pass
    return None


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "请提供图片路径", "text": ""}, ensure_ascii=False))
        sys.exit(1)

    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(json.dumps({"error": f"文件不存在: {image_path}", "text": ""}, ensure_ascii=False))
        sys.exit(1)

    # 检查文件是否为图片
    ext = os.path.splitext(image_path)[1].lower()
    if ext not in ('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff', '.heic'):
        print(json.dumps({"error": f"不支持的图片格式: {ext}，支持 png/jpg/webp/bmp/tiff/heic", "text": ""}, ensure_ascii=False))
        sys.exit(1)

    text = None
    
    # 尝试 macOS Vision（最优先）
    if platform.system() == 'Darwin':
        text = extract_text_via_vision(image_path)
        engine = "macOS Vision"
    
    # 尝试 Tesseract
    if not text:
        text = extract_text_via_tesseract(image_path)
        engine = "Tesseract"

    if text:
        result = {
            "engine": engine,
            "text": text,
            "char_count": len(text),
            "file": os.path.basename(image_path)
        }
    else:
        result = {
            "engine": "none",
            "text": "",
            "char_count": 0,
            "file": os.path.basename(image_path),
            "note": "未检测到文字，或图片中无文字内容。请手动输入图片中的文字。"
        }

    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
