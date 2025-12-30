# dtb_dts_md5_audit_and_convert.py

import os
import subprocess
import hashlib

ROOT_DIR = r"G:\r36s\DTBs"


def md5_uret(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def md5_dosya_yaz(path):
    with open(path + ".md5", "w", encoding="utf-8") as f:
        f.write(f"{md5_uret(path)}  {os.path.basename(path)}\n")


def md5_dogrula(path):
    md5_path = path + ".md5"

    if not os.path.exists(md5_path):
        md5_dosya_yaz(path)
        print(f"🆕 MD5 üretildi → {os.path.basename(path)}")
        return True

    try:
        with open(md5_path, "r", encoding="utf-8") as f:
            satir = f.readline().strip()

        kayitli_hash = satir.split()[0]
        guncel_hash = md5_uret(path)

        if kayitli_hash != guncel_hash:
            print(f"❌ MD5 UYUMSUZ → {os.path.basename(path)}")
            return False
        return True

    except Exception as e:
        print(f"⚠ MD5 okunamadı ({os.path.basename(path)}): {e}")
        return False


def dosya_ismi_bul(path):
    if not os.path.exists(path):
        return path
    d = os.path.dirname(path)
    n, e = os.path.splitext(os.path.basename(path))
    i = 1
    while True:
        p = os.path.join(d, f"{n}_{i}{e}")
        if not os.path.exists(p):
            return p
        i += 1


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dtc_path = os.path.join(script_dir, "dtc.exe")

    if not os.path.exists(dtc_path):
        print("❌ dtc.exe bulunamadı")
        return

    print("▶ MD5 denetimi + DTB→DTS işlemi başladı\n")

    for root, _, files in os.walk(ROOT_DIR):
        for file in files:
            if not file.lower().endswith((".dtb", ".dts")):
                continue

            full_path = os.path.join(root, file)

            print("────────────────────────────────")
            print(f"📁 Klasör : {root}")
            print(f"📄 Dosya  : {file}")

            md5_dogrula(full_path)

            # Sadece DTB dönüşüme girer
            if not file.lower().endswith(".dtb"):
                continue

            isim = os.path.splitext(file)[0]
            dts_path = os.path.join(root, f"{isim}.dts")

            if os.path.exists(dts_path):
                eski_md5 = md5_uret(dts_path)

                temp_dts = dosya_ismi_bul(os.path.join(root, f"{isim}_temp.dts"))
                subprocess.run(
                    [dtc_path, "-I", "dtb", "-O", "dts", full_path, "-o", temp_dts],
                    capture_output=True
                )

                yeni_md5 = md5_uret(temp_dts)

                if eski_md5 == yeni_md5:
                    os.remove(temp_dts)
                    print("⏭ DTS güncel → dönüşüm atlandı")
                    continue
                else:
                    os.remove(dts_path)
                    os.rename(temp_dts, dts_path)
                    print("♻ DTS farklı → yeniden üretildi")
            else:
                subprocess.run(
                    [dtc_path, "-I", "dtb", "-O", "dts", full_path, "-o", dts_path],
                    capture_output=True
                )
                print("✅ DTS oluşturuldu")

            # Doğrulama
            check_dtb = dosya_ismi_bul(os.path.join(root, f"{isim}_check.dtb"))
            subprocess.run(
                [dtc_path, "-I", "dts", "-O", "dtb", dts_path, "-o", check_dtb],
                capture_output=True
            )

            try:
                if open(full_path, "rb").read() == open(check_dtb, "rb").read():
                    os.remove(check_dtb)
                    print("✔ Doğrulama OK (_check.dtb silindi)")
                else:
                    print("⚠ Doğrulama farkı (_check.dtb korundu)")
            except Exception as e:
                print(f"⚠ Doğrulama hatası: {e}")

            md5_dosya_yaz(full_path)
            md5_dosya_yaz(dts_path)

    print("\n🏁 Tüm denetim ve işlemler tamamlandı.")


if __name__ == "__main__":
    main()
