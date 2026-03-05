#!/usr/bin/env python3
"""Apply the remaining 81 untranslated parts (mostly fasteners) to the SQLite database."""

import sqlite3
import os
import sys
import io

# Fix Windows terminal encoding for Chinese characters
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "knowledge-base", "kb.db")

REMAINING_TRANSLATIONS = {
    "A型簧片螺母": "A-Type Spring Nut",
    "Tilt电机固定台阶螺栓": "Tilt Motor Mounting Step Bolt",
    "下摆臂球销锥形垫": "Lower Control Arm Ball Pin Taper Washer",
    "中央螺栓": "Central Bolt",
    "中心销（带密封环)": "Center Pin (with Seal Ring)",
    "中空螺栓": "Hollow Bolt",
    "侧门锁扣总成": "Side Door Latch Assembly",
    "偏心螺栓": "Eccentric Bolt",
    "六角头带法兰盘螺栓": "Hex Head Flange Bolt",
    "六角法兰面导向螺栓": "Hex Flange Guide Bolt",
    "六角法兰面承面带齿螺母": "Hex Flange Serrated Nut",
    "内六花圆柱头法兰盘螺栓": "Torx Cylinder Head Flange Bolt",
    "内六角圆柱头螺钉": "Hex Socket Head Cap Screw",
    "内六角盘头螺钉": "Hex Socket Pan Head Screw",
    "内六角花型沉头螺钉": "Torx Countersunk Head Screw",
    "内六角花型盘头螺钉": "Torx Pan Head Screw",
    "内六角花形盘头法兰面螺钉": "Torx Pan Head Flange Screw",
    "内插螺栓": "Insert Bolt",
    "减震皮带轮螺栓": "Damper Pulley Bolt",
    "前视摄像头固定螺钉": "Front Camera Mounting Screw",
    "副仪表板冰箱风扇螺钉": "Center Console Refrigerator Fan Screw",
    "十字槽半沉头螺钉": "Phillips Oval Head Screw",
    "双头螺栓柱": "Stud Bolt",
    "可调螺母活动件": "Adjustable Nut Moving Part",
    "右前门内扣手电镀亮圈": "Right Front Door Inner Handle Chrome Ring",
    "右拉杆锁扣": "Right Tie Rod Lock Clip",
    "后吊耳安装螺栓": "Rear Tow Hook Mounting Bolt",
    "固定螺栓": "Mounting Bolt",
    "圆头螺栓": "Round Head Bolt",
    "塑料螺母": "Plastic Nut",
    "塑料螺母座": "Plastic Nut Seat",
    "外侧护板安装螺钉": "Outer Guard Panel Mounting Screw",
    "外六角法兰螺栓": "Hex Flange Bolt",
    "外六角法兰螺母": "Hex Flange Nut",
    "外六角盘头螺栓": "Hex Pan Head Bolt",
    "外六角盘头螺栓（带胶)": "Hex Pan Head Bolt (with Adhesive)",
    "外六角组合螺栓": "Hex Combination Bolt",
    "安装螺栓": "Mounting Bolt",
    "安装螺钉": "Mounting Screw",
    "定位销防水海绵": "Locating Pin Waterproof Foam",
    "密封塑料螺母座": "Sealing Plastic Nut Seat",
    "左前门内扣手电镀亮圈": "Left Front Door Inner Handle Chrome Ring",
    "左拉杆锁扣": "Left Tie Rod Lock Clip",
    "平头铆螺母": "Flat Head Rivet Nut",
    "座椅升降电机安装螺栓": "Seat Height Motor Mounting Bolt",
    "座椅升降电机安装螺母": "Seat Height Motor Mounting Nut",
    "座靠连接螺栓": "Seat-Back Connecting Bolt",
    "开口方型螺母": "Open Square Nut",
    "扳螺母": "Wrench Nut",
    "拉线电机安装螺栓": "Cable Motor Mounting Bolt",
    "排气螺钉": "Bleed Screw",
    "排气链轮安装螺栓": "Exhaust Camshaft Sprocket Mounting Bolt",
    "放油螺栓": "Drain Bolt",
    "气囊固定螺母": "Airbag Mounting Nut",
    "法兰面螺母": "Flange Nut",
    "注油/放油螺栓": "Oil Fill/Drain Bolt",
    "滑轨安装螺母": "Rail Mounting Nut",
    "电机螺栓": "Motor Bolt",
    "电磁阀固定螺栓1": "Solenoid Valve Mounting Bolt 1",
    "电磁阀固定螺栓2": "Solenoid Valve Mounting Bolt 2",
    "簧片螺母": "Spring Nut",
    "缸盖螺栓": "Cylinder Head Bolt",
    "背门静音锁扣总成": "Tailgate Silent Latch Assembly",
    "腿托骨架安装螺栓": "Leg Rest Frame Mounting Bolt",
    "自攻锁紧螺钉 ST4.8X9.5": "Self-Tapping Locking Screw ST4.8X9.5",
    "蘑菇搭扣": "Mushroom Snap Fastener",
    "蘑菇搭扣-上片": "Mushroom Snap Fastener - Upper Piece",
    "螺栓": "Bolt",
    "螺母": "Nut",
    "螺母座": "Nut Seat",
    "螺钉": "Screw",
    "螺钉 3.5x12": "Screw 3.5x12",
    "转向器固定螺钉": "Steering Gear Mounting Screw",
    "转向盘安装螺栓": "Steering Wheel Mounting Bolt",
    "铰链固定螺钉": "Hinge Mounting Screw",
    "销螺栓": "Pin Bolt",
    "镜圈固定螺钉": "Mirror Ring Mounting Screw",
    "隔热罩安装螺栓": "Heat Shield Mounting Bolt",
    "飞轮螺栓": "Flywheel Bolt",
    "高压油泵组合螺栓": "High Pressure Fuel Pump Combination Bolt",
    "高压油泵组合螺栓（带胶)": "High Pressure Fuel Pump Combination Bolt (with Adhesive)",
}

def main():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    updated = 0
    for zh, en in REMAINING_TRANSLATIONS.items():
        c.execute(
            "UPDATE parts SET part_name_en = ? WHERE part_name_zh = ? AND (part_name_en IS NULL OR part_name_en = '')",
            (en, zh)
        )
        updated += c.rowcount

    conn.commit()

    c.execute("SELECT COUNT(*) FROM parts")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM parts WHERE part_name_en IS NOT NULL AND part_name_en != ''")
    with_en = c.fetchone()[0]

    print(f"Additional rows updated from remaining translations: {updated}")
    print()
    print("FINAL STATS:")
    print(f"  Total parts in DB: {total}")
    print(f"  Parts with English names: {with_en}")
    print(f"  Parts without English names: {total - with_en}")
    print(f"  Coverage: {with_en / total * 100:.1f}%")

    if total - with_en > 0:
        print()
        print("Still untranslated:")
        c.execute(
            "SELECT part_name_zh FROM parts WHERE (part_name_en IS NULL OR part_name_en = '') LIMIT 50"
        )
        for row in c.fetchall():
            print(f"  {row[0]}")

    conn.close()

if __name__ == "__main__":
    main()
