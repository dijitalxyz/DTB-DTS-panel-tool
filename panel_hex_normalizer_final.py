# panel_hex_normalizer_final.py

import os
import re

WORK_DIR = os.getcwd()

# Her türlü 0x... yakala (0x5 → 0x150002ff)
HEX_REGEX = re.compile(r"0x([0-9a-fA-F]+)")


def hex_to_bytes(match):
    hexval = match.group(1).lower()

    # Tek hane ise byte'a tamamla
    if len(hexval) == 1:
        hexval = "0" + hexval

    # Byte hizasına getir
    if len(hexval) % 2 != 0:
        hexval = "0" + hexval

    # Byte byte ayır
    return " ".join(hexval[i:i+2] for i in range(0, len(hexval), 2))


def normalize_panel(text):
    # < > → [ ]
    text = text.replace("<", "[").replace(">", "]")

    # 0x... → byte dizisi
    text = HEX_REGEX.sub(hex_to_bytes, text)

    # Boşlukları temizle
    text = re.sub(r"\s+", " ", text)
    text = text.replace("[ ", "[").replace(" ]", "]")

    return text.strip() + "\n"


def main():
    print("▶ .panel HEX normalizasyonu (BYTE + 32-BIT) başladı\n")
    print(f"📂 Klasör: {WORK_DIR}\n")

    for file in os.listdir(WORK_DIR):
        if not file.lower().endswith(".panel"):
            continue

        path = os.path.join(WORK_DIR, file)
        print("────────────────────────")
        print(f"📄 Dosya: {file}")

        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                original = f.read()

            normalized = normalize_panel(original)

            if original == normalized:
                print("⏭ Zaten normalize")
                continue

            with open(path, "w", encoding="utf-8") as f:
                f.write(normalized)

            print("✅ BYTE + 32-bit değerler dönüştürüldü")

        except Exception as e:
            print(f"❌ Hata: {e}")

    print("\n🏁 İşlem tamamlandı.")


if __name__ == "__main__":
    main()
