#!/usr/bin/env python3
"""Generate L9 parts catalog reference from OCR content_list.json."""
import json, re, os

BASE = os.path.join(os.path.dirname(__file__), '..')
CONTENT_LIST = os.path.join(BASE, 'mineru-output',
    '941362155-2022-2023款理想L9零件手册', 'ocr',
    '941362155-2022-2023款理想L9零件手册_content_list.json')
OUT = os.path.join(BASE, 'knowledge-base', 'L9-PARTS-CATALOG.md')

SYSTEMS = {
    '动力电池系统': 'Power Battery System',
    '动力驱动系统': 'Power Drive System',
    '进气装置': 'Intake System',
    '排气装置': 'Exhaust System',
    '燃油供给装置': 'Fuel Supply System',
    '发动机装置': 'Engine Assembly',
    '悬置装置': 'Engine/Drivetrain Mounts',
    '前悬架装置': 'Front Suspension',
    '后悬架装置': 'Rear Suspension',
    '转向装置': 'Steering System',
    '行车制动装置': 'Service Brake System',
    '空调热管理系统': 'HVAC & Thermal Management',
    '电器附件系统': 'Electrical Accessories',
    '内饰系统': 'Interior Trim System',
    '电源和信号分配系统': 'Power & Signal Distribution',
    '灯具系统': 'Lighting System',
    '座椅系统': 'Seat System',
    '被动安全系统': 'Passive Safety System',
    '外饰系统': 'Exterior Trim System',
    '自动驾驶系统': 'Autonomous Driving System',
    '智能空间系统': 'Smart Cabin / Infotainment',
    '开闭件系统': 'Closures (Doors, Hood, Tailgate)',
    '车身装置': 'Body Structure',
    '整车附件装置': 'Vehicle Accessories & Consumables',
}

SUBS = {
    '动力电池装置': 'Power Battery Assembly',
    '驱动轴装置': 'Drive Shaft Assembly',
    '前电驱动装置': 'Front Electric Drive Assembly',
    '后电驱动装置': 'Rear Electric Drive Assembly',
    '电源装置': 'Power Supply Unit',
    '增程器': 'Range Extender',
    '空气滤清器部件': 'Air Filter Assembly',
    '进气管路部件': 'Intake Duct Assembly',
    '燃油箱及管路部件': 'Fuel Tank & Lines',
    '燃油箱总成': 'Fuel Tank Assembly',
    '发动机总成部件': 'Engine Assembly Parts',
    '发动机总成附件部件': 'Engine Assembly Accessories',
    '扭矩限制器部件': 'Torque Limiter Assembly',
    '气缸盖部件': 'Cylinder Head Assembly',
    '气缸体部件': 'Cylinder Block Assembly',
    '凸轮轴部件': 'Camshaft Assembly',
    '机油泵部件': 'Oil Pump Assembly',
    '配气机构部件': 'Valve Train Assembly',
    '进排歧管部件': 'Intake/Exhaust Manifold',
    '油底壳及润滑部件': 'Oil Pan & Lubrication',
    '机油滤清器部件': 'Oil Filter Assembly',
    '曲轴通风系统部件': 'Crankcase Ventilation',
    '正时齿轮机构部件': 'Timing Gear Mechanism',
    '皮带轮及张紧轮部件': 'Pulley & Tensioner',
    '燃油管路及连接部件': 'Fuel Lines & Connectors',
    '电子节气门体部件': 'Electronic Throttle Body',
    '增压部件': 'Turbocharger Assembly',
    '蒸发器部件': 'Evaporator Assembly',
    '隔热罩部件': 'Heat Shield Assembly',
    '冷却系统装置部件': 'Cooling System Assembly',
    '水泵部件': 'Water Pump Assembly',
    '发动机系统传感器部件': 'Engine Sensors',
    '火花塞及点火线圈部件': 'Spark Plugs & Ignition Coils',
    '前悬置部件': 'Front Engine Mount',
    '后悬置部件': 'Rear Engine Mount',
    '左前摆臂部件': 'Left Front Control Arm',
    '右前摆臂': 'Right Front Control Arm',
    '前稳定杆部件': 'Front Stabilizer Bar',
    '前减振器部件': 'Front Shock Absorber',
    '后副车架部件': 'Rear Subframe',
    '右后摆臂部件': 'Right Rear Control Arm',
    '左后摆臂部件': 'Left Rear Control Arm',
    '后稳定杆部件': 'Rear Stabilizer Bar',
    '后减震器部件': 'Rear Shock Absorber',
    '悬架空气供给装置': 'Air Suspension Supply System',
    '空气悬架供给部件': 'Air Suspension Supply Parts',
    '空气控制部件': 'Air Control Assembly',
    '空气压缩部件': 'Air Compressor Assembly',
    '车轮装置': 'Wheel Assembly',
    '前制动部件': 'Front Brake Assembly',
    '后制动部件': 'Rear Brake Assembly',
    '制动踏板部件': 'Brake Pedal Assembly',
    '制动管路部件': 'Brake Lines',
    'ESP控制部件': 'ESP Control Unit',
    '随车工具装置': 'On-Board Tool Kit',
    '前端冷却部件装置': 'Front-End Cooling Assembly',
    '电机冷却装置': 'Motor Cooling Assembly',
    '电池及暖风冷却装置': 'Battery & Heater Cooling',
    '后电机冷却管路装置': 'Rear Motor Cooling Lines',
    '前电机冷却管路装置': 'Front Motor Cooling Lines',
    '电池冷却管路装置': 'Battery Cooling Lines',
    '暖风加热管路装置': 'Heater Lines Assembly',
    '发动机冷却管路装置': 'Engine Cooling Lines',
    'HAVC装置': 'HVAC Assembly',
    'HVAC装置': 'HVAC Assembly',
    'HVAC总成部件': 'HVAC Assembly Parts',
    '前HVAC本体部件': 'Front HVAC Body',
    '后HVAC本体部件': 'Rear HVAC Body',
    '制冷压缩机装置': 'Refrigeration Compressor',
    '冷凝器装置': 'Condenser Assembly',
    '空调管路装置': 'AC Lines Assembly',
    '空调控制装置': 'AC Control Assembly',
    '电气设备装置': 'Electrical Equipment',
    '电喇叭装置': 'Electric Horn',
    '门窗开关装置': 'Door/Window Switch',
    '组合开关装置': 'Combination Switch',
    '开关装置': 'Switch Assembly',
    '刮水器装置': 'Wiper Assembly',
    '风窗洗涤器装置': 'Windshield Washer',
    '地毯装置': 'Carpet Assembly',
    '副仪表板装置': 'Center Console Assembly',
    '副仪表板总成部件': 'Center Console Assembly Parts',
    '副仪表板后端上盖板本体部件': 'Center Console Rear Upper Cover',
    '副仪表板冰箱本体部件': 'Center Console Refrigerator',
    '副仪表板上本体部件': 'Center Console Upper Body',
    '副仪表板本体骨架部件': 'Center Console Frame',
    '仪表板装置': 'Dashboard Assembly',
    '仪表板总成部件': 'Dashboard Assembly Parts',
    '仪表板本体部件': 'Dashboard Body Parts',
    '仪表板管梁装置': 'Dashboard Cross-Beam',
    '隔热垫装置': 'Heat Insulation Pads',
    '后端隔热垫部件': 'Rear End Heat Insulation Pad',
    '立柱门槛内饰板装置': 'Pillar/Sill Interior Trim Panel',
    '左侧围内饰板部件': 'Left Side Interior Trim Panel',
    '右侧围内饰板部件': 'Right Side Interior Trim Panel',
    '顶棚及尾门内饰板部件': 'Headliner & Tailgate Interior Panel',
    '后侧围内饰板装置': 'Rear Side Interior Trim',
    '右后侧围内饰板装置': 'Right Rear Side Trim',
    '左后侧围内饰板装置': 'Left Rear Side Trim',
    '行李箱装置': 'Luggage Compartment',
    '顶棚装饰板装置': 'Headliner Trim',
    '前门装饰板装置': 'Front Door Trim Panel',
    '左前门装饰板部件': 'Left Front Door Trim',
    '右前门装饰板部件': 'Right Front Door Trim',
    '后门装饰板装置': 'Rear Door Trim Panel',
    '左后门装饰板部件': 'Left Rear Door Trim',
    '右后门装饰板部件': 'Right Rear Door Trim',
    '后背门内饰板装置': 'Tailgate Interior Trim',
    '前空调第二排吹脚风道装置': 'Front AC 2nd Row Foot Duct',
    '后空调顶棚风道装置': 'Rear AC Roof Duct',
    '后空调吹脚风道装置': 'Rear AC Foot Duct',
    '外循环风道装置': 'Fresh Air Duct',
    '遮阳板装置': 'Sun Visor Assembly',
    '顶棚拉手装置': 'Roof Grab Handles',
    '车辆识别代号标牌装置': 'VIN Plate Assembly',
    '高压线束装置': 'HV Wiring Harness',
    '低压线束装置': 'LV Wiring Harness',
    '前舱线束部件': 'Front Bay Harness',
    '车身线束部件': 'Body Harness',
    '侧门线束部件': 'Side Door Harness',
    '顶棚线束部件': 'Roof Harness',
    '蓄电池线束部件': '12V Battery Harness',
    '仪表板线束部件': 'Dashboard Harness',
    '轮速传感器线束部件': 'Wheel Speed Sensor Harness',
    '后背门线束部件': 'Tailgate Harness',
    '前保险杠线束部件': 'Front Bumper Harness',
    '后保险杠线束部件': 'Rear Bumper Harness',
    'DCDC搭铁线束': 'DC-DC Ground Harness',
    '油箱线束总成': 'Fuel Tank Harness',
    '后电机线束总成': 'Rear Motor Harness',
    '蓄电池装置': '12V Battery Assembly',
    '电路保护装置': 'Circuit Protection (Fuses/Relays)',
    '外部灯具装置': 'Exterior Lighting',
    '前组合灯部件': 'Front Combination Lamp',
    '后组合灯部件': 'Rear Combination Lamp',
    '后雾灯及回复反射器部件': 'Rear Fog Lamp & Reflector',
    '高位制动灯部件': 'High-Mount Stop Lamp',
    '牌照灯部件': 'License Plate Lamp',
    '内部灯具装置': 'Interior Lighting',
    '顶灯部件': 'Dome Lamp',
    '门灯及侧围灯部件': 'Door & Side Body Lamps',
    '仪表灯部件': 'Instrument Lighting',
    '驾驶员座椅总成部件': 'Driver Seat Assembly',
    '驾驶员座椅分总成': 'Driver Seat Sub-Assembly',
    '驾驶员座椅骨架部件': 'Driver Seat Frame',
    '副驾驶员座椅总成部件': 'Passenger Seat Assembly',
    '副驾驶员座椅分总成': 'Passenger Seat Sub-Assembly',
    '副驾驶员座椅骨架': 'Passenger Seat Frame',
    '第二排左侧座椅部件': '2nd Row Left Seat',
    '第二排左侧座椅骨架部件': '2nd Row Left Seat Frame',
    '第二排左侧座椅分总成部件': '2nd Row Left Seat Sub-Assembly',
    '第二排右侧座椅部件': '2nd Row Right Seat',
    '第二排右侧座椅骨架部件': '2nd Row Right Seat Frame',
    '第二排右侧座椅分总成部件': '2nd Row Right Seat Sub-Assembly',
    '第三排右侧座椅部件': '3rd Row Right Seat',
    '第三排右侧座椅分总成部件': '3rd Row Right Seat Sub-Assembly',
    '第三排左侧座椅部件': '3rd Row Left Seat',
    '第三排左侧座椅分总成部件': '3rd Row Left Seat Sub-Assembly',
    '第三排座椅坐垫部件': '3rd Row Seat Cushion',
    '第三排座椅坐垫分总成部件': '3rd Row Seat Cushion Sub-Assembly',
    '方向盘': 'Steering Wheel (Airbag)',
    '安全带装置': 'Seat Belt Assembly',
    '安全气囊装置': 'Airbag Assembly',
    '被动安全附件装置': 'Passive Safety Accessories',
    '车身外装饰件装置': 'Body Exterior Trim',
    '翼子板装饰件装置': 'Fender Trim',
    '激光雷达装饰板装置': 'LiDAR Trim Cover',
    '发动机舱上护板装置': 'Engine Bay Upper Guard',
    '扰流板装置': 'Spoiler Assembly',
    '前围通风饰板装置': 'Front Cowl Vent Trim',
    'LOGO装置': 'Logo/Emblem Assembly',
    '背门外饰板装置': 'Tailgate Exterior Trim',
    '前挡风玻璃装置': 'Front Windshield',
    '后挡风玻璃装置': 'Rear Windshield',
    '天窗装置': 'Sunroof Assembly',
    '天窗总成部件': 'Sunroof Assembly Parts',
    '天窗本体部件': 'Sunroof Body Parts',
    '内后视镜装置': 'Interior Rearview Mirror',
    '左侧外后视镜本体部件': 'Left Exterior Mirror Body',
    '右侧外后视镜本体部件': 'Right Exterior Mirror Body',
    '外后视镜部件': 'Exterior Mirror Assembly',
    '前保险杠装置': 'Front Bumper Assembly',
    '前保险杠本体部件': 'Front Bumper Body',
    '前保险杠总成部件': 'Front Bumper Assembly Parts',
    '主动格栅装置': 'Active Grille Shutter',
    '后保险杠装置': 'Rear Bumper Assembly',
    '后保险杠总成部件': 'Rear Bumper Assembly Parts',
    '后保险杠本体部件': 'Rear Bumper Body',
    '车身底部装饰件装置': 'Underbody Trim',
    '轮罩装置': 'Wheel Arch Liner',
    '轮眉装置': 'Fender Flare',
    '前端框架装置': 'Front-End Module Frame',
    '前组合灯安装支架装置': 'Front Lamp Mounting Bracket',
    '大腿防护横梁装置': 'Pedestrian Protection Beam',
    '侧踏板装置': 'Running Board / Side Step',
    '侧围下裙板装置': 'Side Sill Skirt',
    '车门下装饰板装置': 'Door Lower Trim Panel',
    '侧围通风框装置': 'Side Vent Grille Frame',
    '自动驾驶装置': 'ADAS Hardware Assembly',
    '多媒体装置': 'Multimedia System',
    '摄像头装置': 'Camera Assembly',
    '音响装置': 'Audio System',
    'PEPS装置': 'PEPS (Keyless Entry/Start)',
    '车辆控制装置': 'Vehicle Control Unit',
    '左前门装置': 'Left Front Door Assembly',
    '右前门装置': 'Right Front Door Assembly',
    '左后门装置': 'Left Rear Door Assembly',
    '右后门装置': 'Right Rear Door Assembly',
    '侧围角窗及饰件装置': 'Quarter Window & Trim',
    '发动机盖附件装置': 'Hood Accessories',
    '背门附件装置': 'Tailgate Accessories',
    '前门附件装置': 'Front Door Accessories',
    '左前门密封件部件': 'Left Front Door Seals',
    '左前门玻璃及堵盖部件': 'Left Front Door Glass & Plugs',
    '右前门密封件部件': 'Right Front Door Seals',
    '右前门玻璃及堵盖部件': 'Right Front Door Glass & Plugs',
    '后门附件装置': 'Rear Door Accessories',
    '左后门锁部件': 'Left Rear Door Lock',
    '左后门密封件部件': 'Left Rear Door Seals',
    '左后门玻璃及堵盖部件': 'Left Rear Door Glass & Plugs',
    '右后门锁部件': 'Right Rear Door Lock',
    '右后门密封件部件': 'Right Rear Door Seals',
    '右后门玻璃及堵盖部件': 'Right Rear Door Glass & Plugs',
    '背门装置': 'Tailgate Assembly',
    '发动机盖装置': 'Hood Assembly',
    '车身总成部件': 'Body Assembly Parts',
    '车身前端部件': 'Front Body Structure',
    '前围板部件': 'Firewall / Cowl Panel',
    '左前机舱纵梁部件': 'Left Front Engine Bay Rail',
    '右前机舱纵梁部件': 'Right Front Engine Bay Rail',
    '顶盖外板部件': 'Roof Outer Panel',
    '前地板部件': 'Front Floor Panel',
    '后地板部件': 'Rear Floor Panel',
    '中后地板部件': 'Center-Rear Floor Panel',
    '翼子板部件': 'Fender Panel',
    '防撞梁部件': 'Impact/Crash Beam',
    '加油口盖部件': 'Fuel Filler Door',
    '堵盖及贴片部件': 'Plugs & Adhesive Patches',
    '左侧围内板部件': 'Left Side Inner Panel',
    '右侧围内板部件': 'Right Side Inner Panel',
    '右侧围外板部件': 'Right Side Outer Panel',
    '左侧围外板部件': 'Left Side Outer Panel',
    '胶水': 'Adhesives / Sealant',
    '密封圈': 'O-rings / Gaskets',
    '线束修复': 'Wiring Harness Repair',
    '养护': 'Maintenance Fluids',
    '油漆': 'Paint',
    '油脂': 'Grease / Lubricants',
    '其他': 'Other Consumables',
    '机舱线束保险丝': 'Engine Bay Fuses',
    '后部保险丝盒': 'Rear Fuse Box',
    '抽芯铆钉': 'Blind Rivets / Fasteners',
    # Additional entries found during cleanup
    '后电驱动装置': 'Rear Electric Drive Assembly',
    '燃油箱及管路部件': 'Fuel Tank & Lines',
    '气缸盖部件': 'Cylinder Head Assembly',
    '气缸体部件': 'Cylinder Block Assembly',
    '机油滤清器部件': 'Oil Filter Assembly',
    '燃油管路及连接部件': 'Fuel Lines & Connectors',
    '隔热罩部件': 'Heat Shield Assembly',
    '冷却系统装置部件': 'Cooling System Assembly',
    '水泵部件': 'Water Pump Assembly',
    '发动机系统传感器部件': 'Engine Sensors',
    '发动机总成附件部件': 'Engine Assembly Accessories',
    '右前摆臂': 'Right Front Control Arm',
    '前稳定杆部件': 'Front Stabilizer Bar',
    '前减振器部件': 'Front Shock Absorber',
    '右后摆臂部件': 'Right Rear Control Arm',
    '后减震器部件': 'Rear Shock Absorber',
    '空气悬架供给部件': 'Air Suspension Supply Parts',
    '空气控制部件': 'Air Control Assembly',
    '空气压缩部件': 'Air Compressor Assembly',
    '前制动部件': 'Front Brake Assembly',
    '后制动部件': 'Rear Brake Assembly',
    '制动管路部件': 'Brake Lines',
    '前端冷却部件装置': 'Front-End Cooling Assembly',
    '电机冷却装置': 'Motor Cooling Assembly',
    '风窗洗涤器装置': 'Windshield Washer',
    '前HVAC本体部件': 'Front HVAC Body',
    '左前门装饰板部件': 'Left Front Door Trim',
    '右前门装饰板部件': 'Right Front Door Trim',
    '左后门装饰板部件': 'Left Rear Door Trim',
    '右后门装饰板部件': 'Right Rear Door Trim',
    '高压线束装置': 'HV Wiring Harness',
    '前组合灯部件': 'Front Combination Lamp',
    '驾驶员座椅分总成': 'Driver Seat Sub-Assembly',
    '副驾驶员座椅分总成': 'Passenger Seat Sub-Assembly',
    '第二排左侧座椅分总成部件': '2nd Row Left Seat Sub-Assembly',
    '第二排右侧座椅分总成部件': '2nd Row Right Seat Sub-Assembly',
    '第三排右侧座椅分总成部件': '3rd Row Right Seat Sub-Assembly',
    '天窗装置': 'Sunroof Assembly',
    '天窗本体部件': 'Sunroof Body Parts',
    '前保险杠装置': 'Front Bumper Assembly',
    '前保险杠本体部件': 'Front Bumper Body',
    '前保险杠总成部件': 'Front Bumper Assembly Parts',
    '主动格栅装置': 'Active Grille Shutter',
    '后保险杠装置': 'Rear Bumper Assembly',
    '后保险杠总成部件': 'Rear Bumper Assembly Parts',
    '背门外饰板装置': 'Tailgate Exterior Trim',
    '外后视镜部件': 'Exterior Mirror Assembly',
    '前门附件装置': 'Front Door Accessories',
    '后门附件装置': 'Rear Door Accessories',
    '自动驾驶装置': 'ADAS Hardware Assembly',
    '多媒体装置': 'Multimedia System',
    'PEPS装置': 'PEPS (Keyless Entry/Start)',
    '发动机盖装置': 'Hood Assembly',
    '防撞梁部件': 'Impact/Crash Beam',
    '堵盖及贴片部件': 'Plugs & Adhesive Patches',
    '翼子板部件': 'Fender Panel',
    '整车附件装置': 'Vehicle Accessories & Consumables',
    '胶水': 'Adhesives / Sealant',
    '线束修复': 'Wiring Harness Repair',
    '养护': 'Maintenance Fluids',
    '油脂': 'Grease / Lubricants',
    '其他': 'Other Consumables',
    'HAVC装置': 'HVAC Assembly',
    '方向盘': 'Steering Wheel (Airbag)',
}


def clean_name(text):
    """Remove dates, version suffixes, OCR artifacts from component names."""
    c = text
    # Remove trailing Chinese suffixes
    for suffix in ['-新', '-改', '-优化', '新版']:
        if c.endswith(suffix):
            c = c[:-len(suffix)]
    # Remove trailing version/model suffixes like -9, -1, -11
    c = re.sub(r'-\d+$', '', c)
    # Remove date patterns
    c = re.sub(r'\s*[\(-]?\d{4}[-/]\d{1,2}[-/]\d{1,2}\)?', '', c)
    c = re.sub(r'\s*[\(-]?2022[-/]?\d{0,6}\)?', '', c)
    c = re.sub(r'\s*[\(-]?2023[-/]?\d{1,2}[-/]?\d{1,2}\)?', '', c)
    c = re.sub(r'-\d+-\d+$', '', c)
    # Remove OCR artifacts: trailing G, .svg.svg, (1), （）, （, ）
    c = re.sub(r'\.svg\.svg$', '', c)
    c = re.sub(r'\s*[\(（]\s*[\d]*\s*[\)）]?\s*$', '', c)
    c = re.sub(r'\s*[（\(]\s*$', '', c)
    c = re.sub(r'\s*[）\)]\s*$', '', c)
    # Remove "第一张", "第二张", "第-张" etc
    c = re.sub(r'第[一二三四\-]张.*$', '', c)
    # Remove trailing "一 1" (OCR for page ref)
    c = re.sub(r'[一二三]\s*\d*\s*$', '', c)
    # Remove trailing G/g (common OCR artifact on Chinese text)
    c = re.sub(r'[Gg]\s*$', '', c)
    # Remove trailing digits after Chinese (e.g. 部件1, 装置2)
    c = re.sub(r'([\u4e00-\u9fff])\d+$', r'\1', c)
    # Remove trailing -新, -1, -08-18, etc that survived earlier cleaning
    c = re.sub(r'-新$', '', c)
    c = re.sub(r'-\d+(-\d+)*$', '', c)
    c = c.strip(' -')
    return c


def is_ocr_garbage(text):
    """Detect OCR garbage entries that should be skipped."""
    # Random alphanumeric strings (no Chinese chars)
    if re.match(r'^[\dA-Za-z\s\-\.,:;]+$', text) and len(text) < 40:
        return True
    # "删除" (delete) instructions from editors
    if '删除' in text:
        return True
    # Internal codes like LI7M4-BZ_NZVU21FM
    if re.match(r'^[A-Z0-9]{4,}-BZ', text):
        return True
    # FR. codes
    if text.startswith('FR.'):
        return True
    # Very short entries (single char, numbers only)
    if len(text) < 2:
        return True
    # Pure numbers/dots/dashes
    if re.match(r'^[\d\.\-\s]+$', text):
        return True
    # Mixed garbage: mostly Latin/numbers with very few Chinese chars
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    latin_chars = len(re.findall(r'[A-Za-z]', text))
    if latin_chars > 4 and chinese_chars <= 1 and len(text) < 40:
        return True
    return False


def lookup_en(zh_name):
    """Find English translation."""
    if zh_name in SUBS:
        return SUBS[zh_name]
    # Try without trailing digits
    base = re.sub(r'\d+$', '', zh_name).strip()
    if base in SUBS:
        return SUBS[base]
    return ''


def main():
    with open(CONTENT_LIST, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Collect all text entries (both level=1 and level=None)
    all_entries = []
    for item in data:
        text = item.get('text', '').strip()
        level = item.get('text_level')
        page = item.get('page_idx', -1)
        if not text or text == '理想' or text.startswith('理想 '):
            continue
        if is_ocr_garbage(text):
            continue
        all_entries.append((page, level, text))

    # Build hierarchy (merge duplicate system names)
    current_system = None
    systems = []
    systems_by_name = {}  # zh_name -> system dict

    for page, level, text in all_entries:
        clean = clean_name(text)
        if not clean or len(clean) < 2:
            continue
        if is_ocr_garbage(clean):
            continue
        if clean in SYSTEMS:
            if clean in systems_by_name:
                # Merge into existing system
                current_system = systems_by_name[clean]
            else:
                current_system = {'zh': clean, 'en': SYSTEMS[clean], 'page': page, 'subs': []}
                systems.append(current_system)
                systems_by_name[clean] = current_system
        elif current_system is not None:
            en = lookup_en(clean)
            existing = [s['zh'] for s in current_system['subs']]
            if clean not in existing:
                current_system['subs'].append({'zh': clean, 'en': en, 'page': page})

    # Write MD
    total_subs = sum(len(s['subs']) for s in systems)

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('# Li Auto L9 (2022-2023) \u2014 \u041f\u043e\u043b\u043d\u044b\u0439 \u043a\u0430\u0442\u0430\u043b\u043e\u0433 \u0441\u0438\u0441\u0442\u0435\u043c \u0438 \u043a\u043e\u043c\u043f\u043e\u043d\u0435\u043d\u0442\u043e\u0432\n\n')
        f.write('> \u0418\u0441\u0442\u043e\u0447\u043d\u0438\u043a: `mineru-output/941362155-2022-2023\u6b3e\u7406\u60f3L9\u96f6\u4ef6\u624b\u518c/` (415 \u0441\u0442\u0440., MinerU OCR)\n\n')
        f.write(f'**\u0421\u0438\u0441\u0442\u0435\u043c:** {len(systems)} | **\u041f\u043e\u0434\u0441\u0438\u0441\u0442\u0435\u043c/\u043a\u043e\u043c\u043f\u043e\u043d\u0435\u043d\u0442\u043e\u0432:** {total_subs}\n\n')

        # Summary table
        f.write('## \u041e\u0433\u043b\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u0441\u0438\u0441\u0442\u0435\u043c\n\n')
        f.write('| # | \u0421\u0438\u0441\u0442\u0435\u043c\u0430 (ZH) | System (EN) | \u041f\u043e\u0434\u0441\u0438\u0441\u0442\u0435\u043c | \u0421\u0442\u0440. |\n')
        f.write('|---|-------------|-------------|-----------|------|\n')
        for i, sys in enumerate(systems, 1):
            f.write(f'| {i} | **{sys["zh"]}** | {sys["en"]} | {len(sys["subs"])} | {sys["page"]} |\n')

        f.write('\n---\n\n')

        # Detailed sections
        for i, sys in enumerate(systems, 1):
            f.write(f'## {i}. {sys["zh"]} \u2014 {sys["en"]}\n\n')
            if sys['subs']:
                f.write('| # | \u041a\u043e\u043c\u043f\u043e\u043d\u0435\u043d\u0442 (ZH) | Component (EN) | \u0421\u0442\u0440. |\n')
                f.write('|---|---------------|----------------|------|\n')
                for j, sub in enumerate(sys['subs'], 1):
                    en = sub['en'] if sub['en'] else '\u2014'
                    f.write(f'| {j} | {sub["zh"]} | {en} | {sub["page"]} |\n')
            else:
                f.write('*(\u0435\u0434\u0438\u043d\u044b\u0439 \u0431\u043b\u043e\u043a, \u0431\u0435\u0437 \u043f\u043e\u0434\u043a\u043e\u043c\u043f\u043e\u043d\u0435\u043d\u0442\u043e\u0432)*\n')
            f.write('\n')

        f.write('---\n\n')
        f.write('## \u0424\u043e\u0440\u043c\u0430\u0442\u044b \u043d\u043e\u043c\u0435\u0440\u043e\u0432 \u0437\u0430\u043f\u0447\u0430\u0441\u0442\u0435\u0439\n\n')
        f.write('| \u0424\u043e\u0440\u043c\u0430\u0442 | \u041f\u0440\u0438\u043c\u0435\u0440 | \u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435 |\n')
        f.write('|--------|--------|----------|\n')
        f.write('| `X01-XXXXXXXX` | X01-90000002 | \u0421\u043e\u0431\u0441\u0442\u0432\u0435\u043d\u043d\u044b\u0435 \u043d\u043e\u043c\u0435\u0440\u0430 Li Auto |\n')
        f.write('| `1XXXXXXX` | 1000468, 1002791 | \u0412\u043d\u0443\u0442\u0440\u0435\u043d\u043d\u0438\u0435 \u043d\u043e\u043c\u0435\u0440\u0430 \u043f\u043e\u0441\u0442\u0430\u0432\u0449\u0438\u043a\u043e\u0432 (\u0434\u0432\u0438\u0433\u0430\u0442\u0435\u043b\u044c) |\n')
        f.write('| `QXXXXXXXXX` | Q32006F61 | \u0421\u0442\u0430\u043d\u0434\u0430\u0440\u0442\u043d\u044b\u0435 \u043a\u0440\u0435\u043f\u0451\u0436\u043d\u044b\u0435 \u0434\u0435\u0442\u0430\u043b\u0438 (GB/T) |\n\n')
        f.write('## \u041f\u0440\u0438\u043c\u0435\u0447\u0430\u043d\u0438\u044f\n\n')
        f.write('- \u041a\u0430\u0442\u0430\u043b\u043e\u0433 \u0441\u043e\u0434\u0435\u0440\u0436\u0438\u0442 415 \u0441\u0442\u0440\u0430\u043d\u0438\u0446 \u0441 \u0432\u0437\u0440\u044b\u0432-\u0434\u0438\u0430\u0433\u0440\u0430\u043c\u043c\u0430\u043c\u0438 \u0434\u0435\u0442\u0430\u043b\u0435\u0439\n')
        f.write('- 351 \u0442\u0430\u0431\u043b\u0438\u0446\u0430 \u0434\u0435\u0442\u0430\u043b\u0435\u0439 \u0441\u043e\u0445\u0440\u0430\u043d\u0435\u043d\u0430 \u043a\u0430\u043a \u0438\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u044f (JPG) \u0432 `ocr/images/`\n')
        f.write('- \u0422\u0430\u0431\u043b\u0438\u0446\u044b \u0438\u043c\u0435\u044e\u0442 \u0444\u043e\u0440\u043c\u0430\u0442: **\u5e8f\u53f7 | \u70ed\u70b9ID | \u96f6\u4ef6\u53f7\u7801 | \u96f6\u4ef6\u540d\u79f0**\n')
        f.write('- \u0414\u043b\u044f \u0438\u0437\u0432\u043b\u0435\u0447\u0435\u043d\u0438\u044f \u043d\u043e\u043c\u0435\u0440\u043e\u0432 \u0434\u0435\u0442\u0430\u043b\u0435\u0439 \u043d\u0443\u0436\u0435\u043d OCR \u0442\u0430\u0431\u043b\u0438\u0446 (PaddleOCR/table-transformer)\n')
        f.write('- \u0412\u0441\u0435 \u0438\u043b\u043b\u044e\u0441\u0442\u0440\u0430\u0446\u0438\u0438 \u2014 \u0432\u0437\u0440\u044b\u0432-\u0434\u0438\u0430\u0433\u0440\u0430\u043c\u043c\u044b \u0441 \u043f\u043e\u0437\u0438\u0446\u0438\u043e\u043d\u043d\u044b\u043c\u0438 \u043d\u043e\u043c\u0435\u0440\u0430\u043c\u0438\n')

    size = os.path.getsize(OUT) / 1024
    print(f'Created: {OUT} ({size:.0f} KB)')
    print(f'Systems: {len(systems)}, Subsystems/Components: {total_subs}')


if __name__ == '__main__':
    main()
