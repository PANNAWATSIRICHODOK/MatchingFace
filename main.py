import face_recognition
import cv2
import os
import shutil

# 🔹 นามสกุลภาพที่รองรับ
valid_exts = (".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp")

# 🔹 โหลด known faces
known_encodings = []
known_names = []

print("📥 โหลดข้อมูล known faces...")
for filename in os.listdir("known"):
    if filename.lower().endswith(valid_exts):
        name = os.path.splitext(filename)[0]
        image = face_recognition.load_image_file(
            os.path.join("known", filename))
        encodings = face_recognition.face_encodings(image)
        if encodings:
            known_encodings.append(encodings[0])
            known_names.append(name)
            print(f"✅ โหลด: {filename} เป็น {name}")
        else:
            print(f"❌ ไม่พบใบหน้าใน: {filename}")

# 🔹 เตรียม output
group_folder = "group_photos"
base_output = "output"
os.makedirs(base_output, exist_ok=True)

print("\n🧹 เคลียร์โฟลเดอร์ output...")
# เคลียร์โฟลเดอร์ของแต่ละคน + unknown
for name in known_names + ["unknown"]:
    folder_path = os.path.join(base_output, name)
    shutil.rmtree(folder_path, ignore_errors=True)
    os.makedirs(folder_path, exist_ok=True)
    print(f"📁 พร้อมใช้งาน: {folder_path}")

# เพิ่มโฟลเดอร์พิเศษสำหรับภาพที่ไม่พบใบหน้า
folder_no_faces = os.path.join(base_output, "no_faces")
shutil.rmtree(folder_no_faces, ignore_errors=True)
os.makedirs(folder_no_faces, exist_ok=True)
print(f"📁 พร้อมใช้งาน: {folder_no_faces}")

# 🔹 เริ่มประมวลผลภาพ
print("\n🔍 เริ่มประมวลผลภาพ...")
for filename in os.listdir(group_folder):
    if filename.lower().endswith(valid_exts):
        path = os.path.join(group_folder, filename)
        image = face_recognition.load_image_file(path)
        face_locations = face_recognition.face_locations(image)
        face_encodings = face_recognition.face_encodings(image, face_locations)

        # 🛑 ถ้าไม่เจอใบหน้าเลย
        if len(face_encodings) == 0:
            print(
                f"\n📸 {filename}: ❌ ไม่พบใบหน้าในภาพ — (อาจเบลอ, หันหลัง, บังหน้า ฯลฯ) 💾 บันทึกใน: output/no_faces/{filename}")
            save_path = os.path.join(folder_no_faces, filename)
            cv2.imwrite(save_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
            continue

        image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        people_found = set()

        for i, (top, right, bottom, left) in enumerate(face_locations):
            face_encoding = face_encodings[i]
            matches = face_recognition.compare_faces(
                known_encodings, face_encoding)
            name = "unknown"
            color = (0, 0, 255)

            if True in matches:
                index = matches.index(True)
                name = known_names[index]
                color = (0, 255, 0)
                people_found.add(name)
            else:
                people_found.add("unknown")

            # 🔲 วาดกรอบ + ใส่ชื่อ
            cv2.rectangle(image_bgr, (left, top), (right, bottom), color, 2)
            cv2.putText(image_bgr, name, (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # 🧾 สรุปผล
        print(f"\n📸 {filename}: เจอ {len(face_encodings)} ใบหน้า → ", end="")
        if people_found == {"unknown"}:
            save_path = os.path.join(base_output, "unknown", filename)
            cv2.imwrite(save_path, image_bgr)
            print("❌ ไม่พบคนรู้จัก → 💾 บันทึกใน: unknown/")
        else:
            for person in people_found:
                if person != "unknown":
                    save_path = os.path.join(base_output, person, filename)
                    cv2.imwrite(save_path, image_bgr)
            names_to_log = ', '.join(
                [p for p in people_found if p != "unknown"])
            folders_logged = ', '.join(
                [f"{p}/" for p in people_found if p != "unknown"])
            print(f"✅ พบ: {names_to_log} → 💾 บันทึกใน: {folders_logged}")

print("\n✅ เสร็จสิ้น")
