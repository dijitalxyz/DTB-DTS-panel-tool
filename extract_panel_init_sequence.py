# extract_panel_init_sequence.py

import os
import re

ROOT_DIR = r"G:\r36s\DTBs"

# < ... >  VEYA  [ ... ] formatlarını yakalar
PANEL_REGEX = re.compile(
    r"(panel-init-sequence\s*=\s*[\[<].*?[\]>]\s*;)",
    re.IGNORECASE | re.DOTALL
)


def extract_panel_sequence(dts_path):
    with open(dts_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    match = PANEL_REGEX.search(content)
    if not match:
        return None

    return match.group(1)


def main():
    print("▶ panel-init-sequence taraması başladı\n")

    for root, _, files in os.walk(ROOT_DIR):
        for file in files:
            if not file.lower().endswith(".dts"):
                continue

            dts_path = os.path.join(root, file)
            base = os.path.splitext(file)[0]
            panel_path = os.path.join(root, f"{base}.panel")

            print("────────────────────────────────")
            print(f"📁 Klasör : {root}")
            print(f"📄 DTS    : {file}")

            panel_data = extract_panel_sequence(dts_path)

            if not panel_data:
                print("⏭ panel-init-sequence yok")
                continue

            if os.path.exists(panel_path):
                print("⏭ .panel zaten var → atlandı")
                continue

            with open(panel_path, "w", encoding="utf-8") as f:
                f.write(panel_data.strip() + "\n")

            print(f"✅ .panel üretildi → {base}.panel")

    print("\n🏁 Tüm tarama tamamlandı.")


if __name__ == "__main__":
    main()

