"""Build parts-bridge.json v2: maps OCR parts → 5 diagnostic groups → 3D meshes.

Uses user-specified 5-group mapping:
  electric: ev + battery
  fuel: engine + drivetrain
  suspension: chassis + brakes
  cabin: body + interior + hvac
  tech: infotainment + adas + sensors + lighting
"""
import sqlite3
import json
import sys
import datetime
from pathlib import Path
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

BASE = Path(__file__).resolve().parent.parent
DB_PATH = BASE / "knowledge-base" / "kb.db"
SC_PATH = BASE / "frontend" / "data" / "architecture" / "system-components.json"
GLOSSARY_PATH = BASE / "frontend" / "data" / "architecture" / "i18n-glossary-data.json"
OUTPUT_PATH = BASE / "frontend" / "data" / "architecture" / "parts-bridge.json"

# ===== 22 part catalog systems → 5 diagnostic groups =====
SYSTEM_TO_GROUP = {
    'Power Battery System': 'electric',
    'Power Drive System': 'electric',
    'Power & Signal Distribution': 'electric',
    'Electrical Accessories': 'electric',

    'Engine Assembly': 'fuel',
    'Engine/Drivetrain Mounts': 'fuel',
    'Fuel Supply System': 'fuel',
    'Intake System': 'fuel',
    'Exhaust System': 'fuel',

    'Front Suspension': 'suspension',
    'Rear Suspension': 'suspension',
    'Service Brake System': 'suspension',
    'Steering System': 'suspension',

    'Interior Trim System': 'cabin',
    'Seat System': 'cabin',
    'Closures (Doors, Hood, Tailgate)': 'cabin',
    'HVAC & Thermal Management': 'cabin',
    'Passive Safety System': 'cabin',
    'Body Structure': 'cabin',
    'Exterior Trim System': 'cabin',
    'Vehicle Accessories & Consumables': 'cabin',

    'Autonomous Driving System': 'tech',
    'Smart Cabin / Infotainment': 'tech',
    'Lighting System': 'tech',
}

SYSTEM_TO_KB_LAYERS = {
    'Power Battery System': ['ev', 'battery'],
    'Power Drive System': ['ev'],
    'Power & Signal Distribution': ['ev'],
    'Electrical Accessories': ['ev'],

    'Engine Assembly': ['engine'],
    'Engine/Drivetrain Mounts': ['engine', 'drivetrain'],
    'Fuel Supply System': ['engine'],
    'Intake System': ['engine'],
    'Exhaust System': ['engine'],

    'Front Suspension': ['chassis'],
    'Rear Suspension': ['chassis'],
    'Service Brake System': ['brakes'],
    'Steering System': ['brakes', 'chassis'],

    'Interior Trim System': ['interior'],
    'Seat System': ['interior'],
    'Closures (Doors, Hood, Tailgate)': ['body'],
    'HVAC & Thermal Management': ['hvac'],
    'Passive Safety System': ['interior'],
    'Body Structure': ['body'],
    'Exterior Trim System': ['body'],
    'Vehicle Accessories & Consumables': ['body'],

    'Autonomous Driving System': ['adas'],
    'Smart Cabin / Infotainment': ['infotainment'],
    'Lighting System': ['lighting'],
}

# ===== Expanded layers for mesh matching (broader than KB layers) =====
SYSTEM_TO_MESH_LAYERS = {
    'Power Battery System': ['ev', 'battery'],
    'Power Drive System': ['ev', 'drivetrain'],
    'Power & Signal Distribution': ['ev'],
    'Electrical Accessories': ['ev'],
    'Engine Assembly': ['engine'],
    'Engine/Drivetrain Mounts': ['engine', 'drivetrain'],
    'Fuel Supply System': ['engine'],
    'Intake System': ['engine'],
    'Exhaust System': ['engine', 'body'],
    'Front Suspension': ['chassis', 'drivetrain'],
    'Rear Suspension': ['chassis', 'drivetrain'],
    'Service Brake System': ['brakes', 'interior', 'drivetrain'],
    'Steering System': ['brakes', 'chassis', 'drivetrain'],
    'Interior Trim System': ['interior', 'body', 'sensors'],
    'Seat System': ['interior'],
    'Closures (Doors, Hood, Tailgate)': ['body', 'interior'],
    'HVAC & Thermal Management': ['hvac', 'body', 'engine', 'interior', 'brakes', 'ev'],
    'Passive Safety System': ['interior', 'body', 'brakes'],
    'Body Structure': ['body', 'ev', 'drivetrain'],
    'Exterior Trim System': ['body'],
    'Vehicle Accessories & Consumables': ['body'],
    'Autonomous Driving System': ['adas', 'sensors'],
    'Smart Cabin / Infotainment': ['infotainment', 'interior', 'sensors'],
    'Lighting System': ['lighting', 'body'],
    'Power & Signal Distribution': ['ev', 'sensors', 'interior'],
}

# ===== Keywords → mesh-bearing glossary_ids (sorted longest-first per layer) =====
MESH_KEYWORDS = {
    'ev': [
        ('动力电池包', 'traction_battery_hv_battery@ev'),
        ('动力电池', 'traction_battery_hv_battery@ev'),
        ('电池包', 'traction_battery_hv_battery@ev'),
        ('高压线束', 'high_voltage_wiring@ev'),
        ('充电插座', 'charge_port_door@ev'),
        ('充电口盖', 'charge_port_door@ev'),
        ('充电口', 'charge_port_door@ev'),
        ('电机控制器', 'motor_control_unit@sensors'),
        ('前电机', 'front_electric_motor@ev'),
        ('后电机', 'rear_electric_motor@ev'),
        ('电驱动', 'rear_electric_motor@ev'),
        ('双电机带减速器', 'differential@drivetrain'),
        ('双电机', 'rear_electric_motor@ev'),
    ],
    'engine': [
        ('进气歧管', 'intake_manifold@engine'),
        ('排气歧管', 'exhaust_manifold@engine'),
        ('排气管', 'exhaust_pipe_tailpipe@engine'),
        ('消声器', 'exhaust_system@engine'),
        ('排气净化', 'exhaust_system@engine'),
        ('增程器', 'range_extender@engine'),
        ('增压器', 'range_extender@engine'),
        ('节气门', 'throttle_body@engine'),
        ('加油口盖', 'fuel_filler_cap@engine'),
        ('加油口', 'fuel_filler_cap@engine'),
        ('燃油箱', 'fuel_tank@engine'),
        ('燃油泵', 'fuel_tank@engine'),
        ('发动机支架', 'engine_mount@engine'),
        ('发动机悬置', 'engine_mount@engine'),
        ('动力悬置', 'engine_mount@engine'),
        ('机脚', 'engine_mount@engine'),
        ('悬置支架', 'engine_mount@engine'),
        ('悬置', 'engine_mount@engine'),
        ('组合仪表', 'instrument_cluster@engine'),
        ('油箱', 'fuel_tank@engine'),
        ('发动机', 'engine@engine'),
        ('发电机', 'engine@engine'),
        ('曲轴', 'engine@engine'),
        ('凸轮轴', 'engine@engine'),
        ('缸盖', 'engine@engine'),
        ('缸体', 'engine@engine'),
        ('机油泵', 'engine@engine'),
        ('喷油器', 'engine@engine'),
        ('动力系统', 'transmission_drivetrain_powertrain@engine'),
        ('变速器', 'transmission_drivetrain_powertrain@engine'),
        ('排气', 'exhaust_system@engine'),
    ],
    'drivetrain': [
        ('空气弹簧带减振器', 'shock_absorber_damper@drivetrain'),
        ('空气弹簧带减震器', 'shock_absorber_damper@drivetrain'),
        ('空气弹簧及减振器', 'shock_absorber_damper@drivetrain'),
        ('横向稳定杆', 'stabilizer_bar_anti_roll_bar@drivetrain'),
        ('前横向稳定杆', 'front_anti_roll_bar@drivetrain'),
        ('后横向稳定杆', 'rear_anti_roll_bar@drivetrain'),
        ('前稳定杆', 'front_anti_roll_bar@drivetrain'),
        ('后稳定杆', 'rear_anti_roll_bar@drivetrain'),
        ('稳定杆连接杆', 'stabilizer_bar_anti_roll_bar@drivetrain'),
        ('防倾杆', 'stabilizer_bar_anti_roll_bar@drivetrain'),
        ('稳定杆', 'stabilizer_bar_anti_roll_bar@drivetrain'),
        ('空气弹簧', 'air_suspension@drivetrain'),
        ('空气悬架', 'air_suspension@drivetrain'),
        ('减振器', 'shock_absorber_damper@drivetrain'),
        ('减震器', 'shock_absorber_damper@drivetrain'),
        ('减震支柱', 'strut@drivetrain'),
        ('螺旋弹簧', 'coil_spring@drivetrain'),
        ('差速器', 'differential@drivetrain'),
        ('减速器', 'differential@drivetrain'),
        ('前副车架', 'subframe@drivetrain'),
        ('后副车架', 'subframe@drivetrain'),
        ('副车架', 'subframe@drivetrain'),
        ('传动轴', 'propeller_shaft@drivetrain'),
        ('驱动轴', 'half_shaft_cv_axle@drivetrain'),
        ('半轴', 'half_shaft_cv_axle@drivetrain'),
        ('等速驱动', 'half_shaft_cv_axle@drivetrain'),
        ('分动箱', 'transfer_case@drivetrain'),
        ('左前上摆臂', 'front_left_control_arm@drivetrain'),
        ('右前上摆臂', 'front_right_control_arm@drivetrain'),
        ('左前下摆臂', 'front_left_control_arm@drivetrain'),
        ('右前下摆臂', 'front_right_control_arm@drivetrain'),
        ('左前摆臂', 'front_left_control_arm@drivetrain'),
        ('右前摆臂', 'front_right_control_arm@drivetrain'),
        ('前下摆臂', 'front_left_control_arm@drivetrain'),
        ('左后上横臂', 'rear_left_control_arm@drivetrain'),
        ('右后上横臂', 'rear_right_control_arm@drivetrain'),
        ('左后导向臂', 'rear_left_control_arm@drivetrain'),
        ('右后导向臂', 'rear_right_control_arm@drivetrain'),
        ('左后前束', 'rear_left_control_arm@drivetrain'),
        ('右后前束', 'rear_right_control_arm@drivetrain'),
        ('上横臂', 'rear_left_control_arm@drivetrain'),
        ('导向臂', 'rear_left_control_arm@drivetrain'),
        ('控制臂', 'rear_left_control_arm@drivetrain'),
        ('摆臂', 'front_left_control_arm@drivetrain'),
        ('轮毂轴承', 'wheel_hub@drivetrain'),
        ('轮毂单元', 'wheel_hub@drivetrain'),
        ('转向节', 'wheel_hub_hub@drivetrain'),
        ('轮毂', 'wheel_hub_hub@drivetrain'),
        ('轮辋', 'wheel@drivetrain'),
        ('轮胎', 'tire_tyre@drivetrain'),
        ('车轮', 'wheel@drivetrain'),
    ],
    'brakes': [
        ('制动卡钳', 'brake_caliper@brakes'),
        ('制动钳支架', 'brake_caliper@brakes'),
        ('制动钳', 'brake_caliper@brakes'),
        ('刹车卡钳', 'brake_caliper@brakes'),
        ('制动盘', 'brake_caliper@brakes'),
        ('制动片', 'brake_caliper@brakes'),
        ('制动踏板', 'brake_pedal@brakes'),
        ('刹车踏板', 'brake_pedal@brakes'),
        ('转向横拉杆', 'tie_rod@brakes'),
        ('转向外拉杆', 'tie_rod@brakes'),
        ('转向拉杆', 'tie_rod@brakes'),
        ('横拉杆', 'tie_rod@brakes'),
        ('转向中间轴', 'steering_box@brakes'),
        ('转向机', 'steering_box@brakes'),
        ('转向器', 'steering_box@brakes'),
        ('转向柱', 'steering_box@brakes'),
        ('方向盘', 'steering_wheel@brakes'),
        ('组合开关', 'column_switch@brakes'),
        ('换挡拨片', 'paddle_shifter@brakes'),
        ('组合仪表', 'instrument_cluster@brakes'),
    ],
    'body': [
        ('前挡风玻璃', 'windscreen_windshield@body'),
        ('后挡风玻璃', 'rear_window@body'),
        ('挡风玻璃', 'windscreen_windshield@body'),
        ('前风挡', 'windscreen_windshield@body'),
        ('后风挡', 'rear_window@body'),
        ('门玻璃', 'door_glass@body'),
        ('车窗玻璃', 'door_glass@body'),
        ('玻璃升降器', 'door_glass@body'),
        ('侧窗玻璃', 'side_window@body'),
        ('侧窗', 'side_window@body'),
        ('前保险杠', 'front_bumper@body'),
        ('后保险杠', 'rear_bumper@body'),
        ('防撞梁', 'bumper_reinforcement@body'),
        ('吸能盒', 'bumper_reinforcement@body'),
        ('保险杠骨架', 'bumper_reinforcement@body'),
        ('保险杠饰条', 'bumper_reinforcement@body'),
        ('发动机盖', 'bonnet_hood@body'),
        ('发动机罩', 'bonnet_hood@body'),
        ('机盖', 'bonnet_hood@body'),
        ('前组合灯', 'headlight@body'),
        ('前大灯', 'headlight@body'),
        ('大灯透镜', 'headlight_lens@body'),
        ('大灯罩', 'headlight_lens@body'),
        ('大灯壳', 'headlight_lens@body'),
        ('大灯', 'headlight@body'),
        ('尾灯透镜', 'tail_light_lens@body'),
        ('尾灯罩', 'tail_light_lens@body'),
        ('尾灯壳', 'tail_light_lens@body'),
        ('背门灯', 'taillight@body'),
        ('组合灯', 'headlight@body'),
        ('尾灯', 'taillight@body'),
        ('后备箱盖', 'trunk_lid@body'),
        ('行李箱盖', 'trunk_lid@body'),
        ('背门总成', 'trunk_lid@body'),
        ('背门钣金', 'trunk_lid@body'),
        ('背门锁', 'trunk_lid@body'),
        ('背门', 'trunk_lid@body'),
        ('尾门', 'trunk_lid@body'),
        ('后备箱', 'boot_trunk@body'),
        ('行李箱', 'boot_trunk@body'),
        ('门把手', 'door_handle@body'),
        ('门内开', 'door_handle@body'),
        ('门外开', 'door_handle@body'),
        ('门内饰板', 'door_trim_panel@body'),
        ('门饰板', 'door_trim_panel@body'),
        ('门槛内饰板', 'door_trim_panel@body'),
        ('侧围内饰板', 'door_trim_panel@body'),
        ('车牌框', 'licence_plate_bracket@body'),
        ('车牌', 'licence_plate@body'),
        ('翼子板内衬', 'fender_liner@body'),
        ('叶子板内衬', 'fender_liner@body'),
        ('翼子板', 'fender_wing@body'),
        ('叶子板', 'fender_wing@body'),
        ('底盘护板', 'underbody_cover@body'),
        ('底盘下护板', 'underbody_cover@body'),
        ('底护板', 'underbody_cover@body'),
        ('护板', 'underbody_cover@body'),
        ('轮罩', 'fender_liner@body'),
        ('轮拱', 'wheel_arch_liner@body'),
        ('轮眉', 'wheel_arch_liner@body'),
        ('外后视镜', 'wing_mirror_door_mirror_side_mirror@body'),
        ('侧后视镜', 'wing_mirror_door_mirror_side_mirror@body'),
        ('后视镜', 'wing_mirror_door_mirror_side_mirror@body'),
        ('天窗玻璃', 'sunroof_glass@body'),
        ('天窗', 'sunroof_panel@body'),
        ('车顶', 'roof@body'),
        ('顶棚', 'roof@body'),
        ('后侧围', 'quarter_panel@body'),
        ('散热器', 'radiator@body'),
        ('中冷器', 'radiator@body'),
        ('进气格栅', 'grille@body'),
        ('主动格栅', 'grille@body'),
        ('格栅', 'grille@body'),
        ('隔热板', 'heat_shield@body'),
        ('隔热罩', 'heat_shield@body'),
        ('隔热垫', 'heat_shield@body'),
        ('饰条', 'body_trim_moulding@body'),
        ('装饰条', 'body_trim_moulding@body'),
        ('门槛防尘条', 'sill_rocker_panel@body'),
        ('门槛板', 'sill_rocker_panel@body'),
        ('门槛', 'sill_rocker_panel@body'),
        ('副车架', 'subframe@body'),
        ('底板', 'floor_pan@body'),
        ('地板', 'floor_pan@body'),
        ('前车门', 'front_door@body'),
        ('前门玻璃', 'door_glass@body'),
        ('后门玻璃', 'door_glass@body'),
        ('前门', 'front_door@body'),
        ('后车门', 'rear_door@body'),
        ('后门', 'rear_door@body'),
        ('车门', 'rear_door@body'),
        ('门限位器', 'front_door@body'),
        ('门铰链', 'front_door@body'),
        ('车身', 'body_shell@body'),
        ('徽标', 'emblem@body'),
        ('LOGO', 'emblem@body'),
        ('内饰板', 'door_trim_panel@body'),
        ('内饰', 'interior_trim@body'),
        ('防水膜', 'front_door@body'),
        ('水切', 'front_door@body'),
    ],
    'interior': [
        ('加速踏板', 'accelerator_pedal_gas_pedal@interior'),
        ('油门踏板', 'accelerator_pedal_gas_pedal@interior'),
        ('仪表板', 'dashboard_instrument_panel_fascia@interior'),
        ('仪表台', 'dashboard_instrument_panel_fascia@interior'),
        ('手套箱', 'glove_box_glove_compartment@interior'),
        ('储物箱', 'glove_box_glove_compartment@interior'),
        ('中控屏', 'infotainment_screen_multimedia_display@interior'),
        ('副驾屏', 'infotainment_screen_multimedia_display@interior'),
        ('娱乐屏', 'infotainment_screen_multimedia_display@interior'),
        ('显示屏', 'infotainment_screen_multimedia_display@interior'),
        ('内后视镜', 'interior_rearview_mirror@interior'),
        ('方向盘', 'steering_wheel@brakes'),
        ('遮阳板', 'sun_visor@interior'),
        ('香氛', 'air_freshener@interior'),
        ('组合仪表', 'instrument_cluster@interior'),
        ('中控台', 'interior_trim@interior'),
        ('内饰板', 'door_trim_panel@interior'),
        ('后排座椅', 'rear_seat@interior'),
        ('三排座椅', 'rear_seat@interior'),
        ('二排座椅', 'rear_seat@interior'),
        ('座椅坐垫', 'seat_cushion_seat_base@interior'),
        ('座垫面套', 'seat_cushion_seat_base@interior'),
        ('坐垫面套', 'seat_cushion_seat_base@interior'),
        ('一排座垫', 'front_seat@interior'),
        ('一排靠背', 'front_seat@interior'),
        ('一排座椅', 'front_seat@interior'),
        ('前排座椅', 'front_seat@interior'),
        ('一排', 'front_seat@interior'),
        ('座椅骨架', 'seat@interior'),
        ('座椅调节', 'seat@interior'),
        ('座椅', 'seat@interior'),
        ('座垫', 'seat_cushion_seat_base@interior'),
        ('坐垫', 'seat_cushion_seat_base@interior'),
        ('靠背', 'seat@interior'),
        ('头枕', 'seat@interior'),
    ],
    'hvac': [
        ('电池热管理', 'battery_thermal_management_system_btms@hvac'),
        ('Chiller', 'battery_thermal_management_system_btms@hvac'),
        ('chiller', 'battery_thermal_management_system_btms@hvac'),
        ('chhiller', 'battery_thermal_management_system_btms@hvac'),
        ('BTMS', 'battery_thermal_management_system_btms@hvac'),
        ('散热器', 'radiator@hvac'),
        ('冷凝器', 'radiator@hvac'),
    ],
    'sensors': [
        ('电机控制器', 'motor_control_unit@sensors'),
        ('中控主机', 'head_unit@sensors'),
        ('域控制器', 'head_unit@sensors'),
        ('智能座舱', 'head_unit@sensors'),
        ('HMI中控屏', 'head_unit@sensors'),
    ],
    'infotainment': [
        ('中控主机', 'head_unit@sensors'),
        ('域控制器', 'head_unit@sensors'),
        ('智能座舱', 'head_unit@sensors'),
        ('HMI中控屏', 'head_unit@sensors'),
    ],
}


def _match_part_to_mesh_gid(part_name_zh, system_en):
    """Match a part name to a mesh-bearing glossary_id using keyword rules."""
    valid_layers = SYSTEM_TO_MESH_LAYERS.get(system_en, [])
    for layer in valid_layers:
        keywords = MESH_KEYWORDS.get(layer, [])
        for kw, gid in keywords:
            if kw in part_name_zh:
                return gid
    return None


def build_bridge():
    print(f"DB: {DB_PATH}")
    print(f"System components: {SC_PATH}")
    print(f"Output: {OUTPUT_PATH}")

    # Load system-components for L9 mesh → glossary_id mapping
    with open(SC_PATH, 'r', encoding='utf-8') as f:
        sc = json.load(f)

    # Build glossary_id → mesh name mapping (L9)
    gid_to_meshes = defaultdict(set)
    mesh_to_gid = {}
    for group_name, group in sc['groups'].items():
        for comp in group.get('components', {}).get('l9', []):
            gid = comp['glossary_id']
            mesh = comp['mesh']
            gid_to_meshes[gid].add(mesh)
            mesh_to_gid[mesh] = gid

    print(f"L9 meshes: {len(mesh_to_gid)}, unique glossary_ids: {len(gid_to_meshes)}")

    # Load glossary for name matching
    with open(GLOSSARY_PATH, 'r', encoding='utf-8') as f:
        glossary = json.load(f)
    glossary_comps = glossary.get('components', {})

    # Build zh→glossary_id map
    zh_to_gid = {}
    for gid, entry in glossary_comps.items():
        zh = entry.get('zh', '')
        if zh:
            zh_to_gid[zh] = gid

    print(f"Glossary: {len(zh_to_gid)} zh→gid entries")

    # Load parts from DB
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute("""
        SELECT part_number, part_name_zh, part_name_en, part_name_ru, hotspot_id,
               system_zh, system_en, page_idx, is_fastener
        FROM parts
        ORDER BY system_en, page_idx
    """)
    all_parts = c.fetchall()
    conn.close()
    print(f"Parts from DB: {len(all_parts)}")

    # Group parts by system_en
    systems_data = defaultdict(list)
    system_zh_map = {}
    for pn, zh, en, ru, hotspot, szh, sen, page, is_fast in all_parts:
        if not sen:
            continue
        systems_data[sen].append({
            'number': pn,
            'name_zh': zh,
            'name_en': en,
            'name_ru': ru,
            'hotspot': hotspot,
            'page_idx': page,
            'is_fastener': bool(is_fast),
        })
        if szh and sen not in system_zh_map:
            system_zh_map[sen] = szh

    # Build bridge structure
    bridge_systems = {}
    total_mapped = 0
    total_with_mesh = 0
    total_with_gid = 0

    for system_en, parts in sorted(systems_data.items()):
        group = SYSTEM_TO_GROUP.get(system_en, 'cabin')
        kb_layers = SYSTEM_TO_KB_LAYERS.get(system_en, [])
        system_key = system_en.lower().replace(' ', '_').replace('/', '_').replace('&', 'and')
        system_key = ''.join(c for c in system_key if c.isalnum() or c == '_')
        # Deduplicate underscores
        while '__' in system_key:
            system_key = system_key.replace('__', '_')
        system_key = system_key.strip('_')

        # Find glossary_ids relevant to this system (via kb_layers)
        relevant_gids = set()
        relevant_meshes = set()
        for gid in gid_to_meshes:
            layer = gid.split('@')[-1] if '@' in gid else ''
            if layer in kb_layers:
                relevant_gids.add(gid)
                for m in gid_to_meshes[gid]:
                    relevant_meshes.add(m)

        # Try to match individual parts to glossary_ids
        # Pass 1: match against mesh-bearing glossary_ids (keyword rules)
        # Pass 2: fallback to general glossary match
        for part in parts:
            pname = part['name_zh']
            matched_gid = None

            # Pass 1: mesh-keyword matching (prioritized)
            mesh_gid = _match_part_to_mesh_gid(pname, system_en)
            if mesh_gid:
                matched_gid = mesh_gid

            # Pass 2: general glossary fallback
            if not matched_gid:
                if pname in zh_to_gid:
                    matched_gid = zh_to_gid[pname]
                else:
                    clean_name = pname.replace('总成', '').strip()
                    if clean_name in zh_to_gid:
                        matched_gid = zh_to_gid[clean_name]
                    else:
                        for zh, gid in zh_to_gid.items():
                            if len(zh) >= 4 and zh in pname:
                                matched_gid = gid
                                break

            if matched_gid:
                part['glossary_id'] = matched_gid
                total_with_gid += 1
                meshes = list(gid_to_meshes.get(matched_gid, []))
                if meshes:
                    total_with_mesh += 1

        system_zh = system_zh_map.get(system_en, '')

        bridge_systems[system_key] = {
            'zh': system_zh,
            'en': system_en,
            'group': group,
            'kb_layers': kb_layers,
            'glossary_ids': sorted(relevant_gids)[:25],
            'meshes_l9': sorted(relevant_meshes),
            'parts_count': len(parts),
            'parts': parts,
        }
        total_mapped += len(parts)

    bridge = {
        'meta': {
            'version': '2.0',
            'generated': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            'vehicle': 'l9',
            'parts_count': total_mapped,
            'parts_with_glossary_id': total_with_gid,
            'parts_with_mesh': total_with_mesh,
            'systems_count': len(bridge_systems),
            'groups': sorted(set(s['group'] for s in bridge_systems.values())),
        },
        'group_mapping': SYSTEM_TO_GROUP,
        'systems': bridge_systems,
    }

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(bridge, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"Bridge v2 saved to: {OUTPUT_PATH}")
    print(f"  Systems: {len(bridge_systems)}")
    print(f"  Total parts: {total_mapped}")
    print(f"  Parts with glossary_id: {total_with_gid} ({total_with_gid*100//total_mapped}%)")
    print(f"  Parts with specific mesh: {total_with_mesh} ({total_with_mesh*100//total_mapped}%)")

    # Per-group summary
    group_stats = defaultdict(lambda: {'parts': 0, 'systems': 0, 'meshes': 0})
    for sys_data in bridge_systems.values():
        g = sys_data['group']
        group_stats[g]['parts'] += sys_data['parts_count']
        group_stats[g]['systems'] += 1
        group_stats[g]['meshes'] += len(sys_data['meshes_l9'])

    print(f"\n  Per-group breakdown:")
    for g in ['electric', 'fuel', 'suspension', 'cabin', 'tech']:
        s = group_stats[g]
        print(f"    {g:12s}: {s['parts']:4d} parts, {s['systems']:2d} systems, {s['meshes']:3d} meshes")


if __name__ == '__main__':
    build_bridge()
