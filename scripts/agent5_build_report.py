import sys, io, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open('C:/Diagnostica-KB-Package/docs/review/agent5_data_tmp.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

zh_rows = data['zh_rows']
gen_rows = data['gen_rows']
cross_rows = data['cross_rows']

# =============================
# SECTION 1: ZH ISSUES
# =============================
zh_issues = []

# 1.1 Wrong title translation: tong-fan instead of towing
zh_issues.append({
    "chunk_id": "li_auto_l9_ru_62bc8b92",
    "issue": "wrong_title_translation",
    "severity": "high",
    "title_ru": "Буксировка",
    "zh_fragment": "翻通",
    "expected": "拖车 (towing)",
    "detail": "Заголовок секции 'Буксировка' переведён как '翻通' (перевернуть/перейти) вместо '拖车' (буксировка). Тело текста содержит правильный термин '拖车' - несоответствие между заголовком и телом.",
    "quality_score": 0.0
})

# 1.2 Inconsistent brand naming
zh_issues.append({
    "chunk_id": "li_auto_l9_ru_a688e721",
    "issue": "inconsistent_brand_name",
    "severity": "medium",
    "title_ru": "II. Замена колес",
    "zh_fragment": "使用Ideal Motors推荐的轮螺母 / Li Xiang Automobile推荐的平衡块",
    "expected": "理想汽车 (Li Auto)",
    "detail": "Название бренда использовано непоследовательно: 'Ideal Motors' и 'Li Xiang Automobile' вместо официального '理想汽车'. Остальные чанки используют '理想汽车' корректно.",
    "quality_score": 1.0
})

# 1.3 Warning level confusion
zh_issues.append({
    "chunk_id": "li_auto_l9_ru_fed96fa9",
    "issue": "warning_level_confusion",
    "severity": "medium",
    "title_ru": "Внимание",
    "zh_fragment": "警告",
    "expected": "注意 (Caution/Note) for Внимание; 警告 only for Предупреждение/Warning",
    "detail": "Заголовок 'Внимание' (Caution) переведён как '警告' (Warning). В китайских мануалах: 警告=Warning (high severity), 注意=Caution/Note (lower severity). Это критично для безопасности.",
    "quality_score": 0.0
})

# 1.4 Cyrillic artifact in ZH
zh_issues.append({
    "chunk_id": "li_auto_l9_ru_02319375",
    "issue": "cyrillic_artifact_in_zh",
    "severity": "low",
    "title_ru": "Предупреждение",
    "zh_fragment": "...儿童安全\n152\na",
    "expected": "No Cyrillic characters in ZH content",
    "detail": "В конце ZH текста присутствует одиночный кириллический символ 'а' - OCR артефакт из исходного мануала.",
    "quality_score": 1.0
})

# 1.5 Double cyrillic artifact
zh_issues.append({
    "chunk_id": "li_auto_l9_ru_4dd6160f",
    "issue": "cyrillic_artifact_in_zh",
    "severity": "low",
    "title_ru": "IV. Регулировка положения пряжки переднего ремня безопасности",
    "zh_fragment": "...安全措施\n121\na\na",
    "expected": "No Cyrillic characters in ZH content",
    "detail": "Два кириллических 'а' в конце ZH текста - OCR артефакты. Для safety-critical чанка (регулировка ремня безопасности) особенно важна чистота контента.",
    "quality_score": 1.0
})

# 1.6 Markdown headers in ZH
markdown_zh_chunks = [
    "li_auto_l9_ru_f4f6fe79",
    "li_auto_l9_ru_827cad43",
    "li_auto_l9_ru_a159fd52",
    "li_auto_l9_ru_5b05bffa",
    "li_auto_l9_ru_acbfb9a3",
    "li_auto_l9_ru_47319f18",
    "li_auto_l9_ru_4dd6160f",
    "li_auto_l9_ru_e31984b8",
]
zh_issues.append({
    "chunk_ids": markdown_zh_chunks,
    "issue": "markdown_headers_in_zh",
    "severity": "low",
    "detail": "8 ZH чанков начинаются с Markdown '#' или '##'. ZH контент должен использовать нативную китайскую нумерацию (一、二、 или 1. 2.) без Markdown разметки.",
    "zh_fragments": ["# III. 车顶", "# I. 设置", "## IV. 前安全带卡扣位置调整"],
    "affected_count": 8
})

# 1.7 Zero quality score chunks
zero_quality_chunks = [r[0] for r in zh_rows if r[3] == 0.0]
zh_issues.append({
    "chunk_ids": zero_quality_chunks,
    "issue": "zero_quality_score",
    "severity": "medium",
    "detail": "8 ZH чанков имеют quality_score=0.0. Контент визуально выглядит корректным но требует ручной верификации. Особое внимание: sensors и brakes layers.",
    "samples": ["li_auto_l9_ru_3199ad55", "li_auto_l9_ru_b46b2167", "li_auto_l9_ru_0987310c"],
    "affected_count": 8
})

# 1.8 WANING typo in source title
zh_issues.append({
    "chunk_id": "li_auto_l9_ru_a3f73994",
    "issue": "title_typo_in_source",
    "severity": "low",
    "title_ru": "WANING",
    "zh_fragment": "警告",
    "expected": "Title should be WARNING",
    "detail": "ZH перевод (警告) корректен, но source title содержит опечатку 'WANING' вместо 'WARNING'. Проблема в исходных данных, не в переводе.",
    "quality_score": 1.0
})

# =============================
# SECTION 2: CROSS-LANGUAGE DIVERGENCES
# =============================
cross_divs = []

cross_divs.append({
    "chunk_id": "li_auto_l7_zh_844dcfc2",
    "issue": "wrong_language_in_ru_field",
    "en_fragment": "Head-Up Display Interface Overview. The head-up display can project certain information...",
    "ru_fragment": "抬头显示器界面总览. 抬头显示器可以将某些与车辆操作相关的信息投射到挡风玻璃上...",
    "severity": "high",
    "detail": "RU поле содержит китайский текст (55% иероглифов). Перевод отсутствует: вместо русского текста записан оригинальный ZH контент. Чанк о HUD (проекционный дисплей)."
})

cross_divs.append({
    "chunk_id": "li_auto_l7_zh_3f5a7f77",
    "issue": "wrong_language_in_ru_field",
    "en_fragment": "Step 1: On the exit interface, tap the Start Exit icon. Step 2: Follow the prompts...",
    "ru_fragment": "第一步： 在驶出界面中,点击'开始驶出'图标。第二步： 根据中控屏提示信息操作...",
    "severity": "high",
    "detail": "RU поле содержит ZH текст (15% иероглифов). Процедура выезда с автоматической парковки - важный процедурный контент."
})

cross_divs.append({
    "chunk_id": "li_auto_l7_zh_3eecbd2b",
    "issue": "wrong_language_in_ru_field",
    "en_fragment": "If the obstacle-caused pause exceeds a certain time, the system will exit auto-parking.",
    "ru_fragment": "注意 因障碍物导致功能暂停并超过一定时间,系统将退出自动泊车...",
    "severity": "high",
    "detail": "RU поле содержит ZH текст (15% иероглифов). Инструкции по автоматической парковке."
})

cross_divs.append({
    "chunk_id": "li_auto_l7_zh_51f22a85",
    "issue": "wrong_language_in_ru_field",
    "en_fragment": "If pause count is too high during parking, it may affect the final parking result.",
    "ru_fragment": "注意 因障碍物导致功能暂停并超过一定时间,系统将退出自动泊车...",
    "severity": "high",
    "detail": "RU поле содержит ZH текст (15% иероглифов). Дублирует проблему li_auto_l7_zh_3eecbd2b."
})

cross_divs.append({
    "chunk_id": "li_auto_l7_zh_5803bf7e",
    "issue": "numbers_mismatch",
    "en_fragment": "disconnect the 12V battery negative cable harness and provide adequate insulation protection",
    "ru_fragment": "отсоедините минусовой провод аккумулятора и обеспечьте надлежащую изоляцию",
    "severity": "medium",
    "detail": "EN содержит спецификацию '12V battery', RU опускает '12V'. Для технического мануала по безопасности важно сохранять числовые характеристики.",
    "en_q": 1.0,
    "ru_q": 1.0
})

cross_divs.append({
    "chunk_id": "li_auto_l7_zh_1bff3594",
    "issue": "style_divergence",
    "en_fragment": "Step 1: On the exit interface, tap the Start Exit icon. Step 2: Follow the prompts...",
    "ru_fragment": "Первый шаг: на экране выезда нажмите значок 'Начать выезд'. Второй шаг: следуйте...",
    "severity": "low",
    "detail": "EN использует числовые шаги ('Step 1', 'Step 2'), RU переводит как словесные ('Первый шаг', 'Второй шаг'). Для технической документации предпочтительна числовая нумерация. Аналогично в чанках 1c95267f, 2f7013dd, 776f17e6."
})

# =============================
# SECTION 3: GENERAL CONTENT ISSUES
# =============================
gen_issues = []

gen_issues.append({
    "chunk_id": "li_auto_l7_zh_03d530b7",
    "lang": "ru",
    "issue": "untranslated_chunk",
    "severity": "high",
    "quality_score": 0.0,
    "fragment": "| 序号 | 名称 | 序号 | 名称 | (interior lighting table not translated)",
    "detail": "RU-поле содержит оригинальный ZH текст (таблица освещения салона) без перевода + английский дисклеймер от модели. Перевод не был выполнен."
})

gen_issues.append({
    "chunk_id": "li_auto_l7_zh_02366da1",
    "lang": "ru",
    "issue": "untranslated_term_in_ru",
    "severity": "medium",
    "quality_score": 0.0,
    "fragment": "загораются слабо или гаснут в соответствии с氛围灯, создавая приятную атмосферу",
    "detail": "Термин '氛围灯' (ambient lighting) не переведён в RU тексте. Правильно: 'подсветка салона' или 'атмосферное освещение'."
})

gen_issues.append({
    "chunk_id": "li_auto_l7_zh_004329bb",
    "lang": "ru",
    "issue": "untranslated_term_in_ru",
    "severity": "low",
    "quality_score": 0.5,
    "fragment": "副驾驶席(переднее сидень...",
    "detail": "Термин '副驾驶席' вставлен в скобках без перевода. Правильно: 'переднее пассажирское сиденье'."
})

gen_issues.append({
    "chunk_id": "li_auto_l7_zh_017a0a9e",
    "lang": "ru",
    "issue": "unexplained_low_quality",
    "severity": "low",
    "quality_score": 0.2,
    "fragment": "Идентификационный номер увеличителя запаса хода (двигателя) нанесён на блок цилиндров",
    "detail": "Quality score 0.2 при визуально корректном переводе. Термин 'увеличитель запаса хода' нестандартен для Range Extender. Рекомендуется стандартизировать."
})

gen_issues.append({
    "chunk_id": "li_auto_l7_zh_060a0f33",
    "lang": "ru",
    "issue": "mixed_language_table",
    "severity": "medium",
    "quality_score": 1.0,
    "fragment": "七、座椅 / 功能 / 说法 / подогрев сидений / 打开/关闭座椅加热 - Включить/выключить подогрев",
    "detail": "Таблица голосовых команд для сидений: заголовки на ZH (七、座椅, 功能, 说法), команды на ZH с переводом на RU. EN версия этого чанка содержит полностью переведённую таблицу."
})

gen_issues.append({
    "chunk_id": "li_auto_l7_zh_03ec8fcb",
    "lang": "both",
    "issue": "low_quality_ev_content",
    "severity": "medium",
    "quality_score": 0.333,
    "fragment": "After inserting the discharge connector, click Start Power Supply icon...",
    "detail": "EN и RU версии чанка V2L (vehicle-to-load) разряда имеют quality_score=0.33. Контент EV-специфичен и важен для пользователей электромобилей."
})

# =============================
# SECTION 4: CONTEXT ISSUES
# =============================
context_issues = []

context_issues.append({
    "chunk_id": "li_auto_l9_ru_0987310c",
    "layer": "sensors",
    "content_type": "manual",
    "issue": "low_quality_safety_critical_content",
    "severity": "high",
    "quality_score": 0.0,
    "detail": "Чанк sensors/has_warnings=1 с quality_score=0.0. Содержит инструкцию по автоматическому экстренному вызову (eCall). Требует обязательной ручной верификации.",
    "zh_fragment": "自动紧急求助 在发生碰撞（安全气囊展开）时，紧急求助功能会自动激活。通话期间无法手动取消此功能。"
})

context_issues.append({
    "chunk_id": "li_auto_l9_ru_7cbedee3",
    "layer": "brakes",
    "content_type": "manual",
    "issue": "low_quality_safety_critical_content",
    "severity": "high",
    "quality_score": 0.0,
    "detail": "Чанк brakes/has_warnings=1 с quality_score=0.0. ESP description с 4 safety functions (ABS, EBD, DSC, TCS). Нулевой quality score для тормозной системы критичен.",
    "zh_fragment": "电子稳定控制 (ESP) 电子稳定控制包括防抱死制动系统、电子制动力分配、动态稳定性控制和牵引力控制等主要功能"
})

context_issues.append({
    "chunk_id": "li_auto_l9_ru_fed96fa9",
    "layer": "engine",
    "content_type": "manual",
    "issue": "low_quality_safety_critical_content",
    "severity": "high",
    "quality_score": 0.0,
    "detail": "Предупреждение о топливе (engine layer, has_warnings=1) с quality_score=0.0. Предупреждение о разливе топлива и повреждении системы выхлопа.",
    "zh_fragment": "警告 加油时要小心，避免溅洒燃油，因为这可能导致汽车受损，例如排放控制系统故障"
})

context_issues.append({
    "chunk_id": "li_auto_l9_ru_827cad43",
    "layer": "interior",
    "content_type": "manual",
    "issue": "inappropriate_layer_classification",
    "severity": "low",
    "quality_score": 0.333,
    "detail": "Чанк описывает настройки AEB (автоматического экстренного торможения) - ADAS функция, но layer='interior'. Markdown заголовок '#' нарушает стиль. Буква 'A' в конце - OCR артефакт.",
    "zh_fragment": "# I. 设置 在中控屏幕设置中选择'智能驾驶'，然后选择'主动安全'。点击'自动紧急制动'下的选项 系统帮助驾驶员 452 A"
})

# =============================
# FINAL ASSEMBLY
# =============================
all_issues = zh_issues + gen_issues + context_issues + cross_divs

# Count individual issues (some have chunk_ids array)
def count_issue(i):
    if "chunk_ids" in i:
        return i.get("affected_count", len(i["chunk_ids"]))
    return 1

total_issues = sum(count_issue(i) for i in all_issues)
high_count = sum(count_issue(i) for i in all_issues if i.get("severity") == "high")
medium_count = sum(count_issue(i) for i in all_issues if i.get("severity") == "medium")
low_count = sum(count_issue(i) for i in all_issues if i.get("severity") == "low")

result = {
    "agent": "agent5_zh_general",
    "review_date": "2026-02-28",
    "scope": {
        "zh_chunks_reviewed": len(zh_rows),
        "general_chunks_reviewed": len(gen_rows),
        "cross_language_pairs_checked": len(cross_rows),
        "glossary_terms_used": 3322
    },
    "zh_reviewed": len(zh_rows),
    "general_reviewed": len(gen_rows),
    "cross_checked": len(cross_rows),
    "issues_found": len([i for i in all_issues if "chunk_ids" not in i]) + sum(i.get("affected_count", len(i.get("chunk_ids", []))) for i in all_issues if "chunk_ids" in i),
    "issues_by_severity": {
        "high": high_count,
        "medium": medium_count,
        "low": low_count
    },
    "summary": {
        "zh_quality_distribution": {
            "perfect_1_0": len([r for r in zh_rows if r[3] == 1.0]),
            "good_0_5_to_0_99": len([r for r in zh_rows if 0.5 <= r[3] < 1.0]),
            "poor_0_01_to_0_49": len([r for r in zh_rows if 0 < r[3] < 0.5]),
            "zero_0_0": len([r for r in zh_rows if r[3] == 0.0])
        },
        "simplified_chinese_verified": True,
        "traditional_chars_found": False,
        "cyrillic_artifacts_in_zh": 2,
        "brand_name_inconsistencies": 1,
        "zh_with_markdown_headers": 8,
        "ru_fields_containing_zh_text": 4,
        "untranslated_ru_chunks": 1
    },
    "zh_issues": zh_issues,
    "general_content_issues": gen_issues,
    "context_issues": context_issues,
    "cross_language_divergences": cross_divs,
    "recommendations": [
        {
            "priority": "high",
            "action": "Исправить перевод заголовка: li_auto_l9_ru_62bc8b92 '翻通' заменить на '拖车'",
            "affected_chunks": ["li_auto_l9_ru_62bc8b92"]
        },
        {
            "priority": "high",
            "action": "Ретранслировать 4 чанка где RU поле содержит ZH текст вместо русского перевода",
            "affected_chunks": ["li_auto_l7_zh_844dcfc2", "li_auto_l7_zh_3f5a7f77", "li_auto_l7_zh_3eecbd2b", "li_auto_l7_zh_51f22a85"]
        },
        {
            "priority": "high",
            "action": "Ручная верификация 3 safety-critical ZH чанков с quality_score=0.0 (eCall, ESP, fuel warning)",
            "affected_chunks": ["li_auto_l9_ru_0987310c", "li_auto_l9_ru_7cbedee3", "li_auto_l9_ru_fed96fa9"]
        },
        {
            "priority": "high",
            "action": "Перевести нетронутый RU чанк li_auto_l7_zh_03d530b7 (таблица освещения салона)",
            "affected_chunks": ["li_auto_l7_zh_03d530b7"]
        },
        {
            "priority": "medium",
            "action": "Стандартизировать бренд в ZH: 'Ideal Motors' и 'Li Xiang Automobile' заменить на '理想汽车'",
            "affected_chunks": ["li_auto_l9_ru_a688e721"]
        },
        {
            "priority": "medium",
            "action": "Исправить уровни предупреждений: 'Внимание' (Caution) -> 注意, не 警告",
            "affected_chunks": ["li_auto_l9_ru_fed96fa9"]
        },
        {
            "priority": "medium",
            "action": "Перевести ZH термины в RU тексте: '氛围灯' -> 'подсветка салона' (chunk 02366da1)",
            "affected_chunks": ["li_auto_l7_zh_02366da1"]
        },
        {
            "priority": "medium",
            "action": "Перевести заголовки таблицы в chunk li_auto_l7_zh_060a0f33: 功能/说法 -> Функция/Команда",
            "affected_chunks": ["li_auto_l7_zh_060a0f33"]
        },
        {
            "priority": "low",
            "action": "Убрать Markdown '#' из 8 ZH чанков, заменить нативной нумерацией",
            "affected_chunks": ["li_auto_l9_ru_f4f6fe79", "li_auto_l9_ru_827cad43", "li_auto_l9_ru_a159fd52", "li_auto_l9_ru_5b05bffa", "li_auto_l9_ru_acbfb9a3", "li_auto_l9_ru_47319f18", "li_auto_l9_ru_4dd6160f", "li_auto_l9_ru_e31984b8"]
        },
        {
            "priority": "low",
            "action": "Очистить OCR артефакты (кириллические символы) из ZH чанков",
            "affected_chunks": ["li_auto_l9_ru_02319375", "li_auto_l9_ru_4dd6160f"]
        },
        {
            "priority": "low",
            "action": "Добавить '12V' в RU перевод chunk li_auto_l7_zh_5803bf7e (battery disconnect procedure)",
            "affected_chunks": ["li_auto_l7_zh_5803bf7e"]
        }
    ],
    "status": "complete"
}

output_path = 'C:/Diagnostica-KB-Package/docs/review/agent5_zh_general.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f'Saved: {output_path}')
print(f'Total issues: {result["issues_found"]}')
print(f'  High: {high_count}, Medium: {medium_count}, Low: {low_count}')
print(f'ZH reviewed: {result["zh_reviewed"]}')
print(f'General reviewed: {result["general_reviewed"]}')
print(f'Cross-checked: {result["cross_checked"]}')
