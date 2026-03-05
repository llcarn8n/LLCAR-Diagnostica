#!/usr/bin/env python3
# translate_batch005_correct.py
# Translates the actual 10 chunks in batch_005.json
# Replaces any previous output with the correct translations.
import json, os

OUTPUT = "C:/Diagnostica-KB-Package/knowledge-base/translate_batches/batch_005_out.json"

results = []

def add(chunk_id, en_title, en_content, ru_title, ru_content):
    results.append({"id": chunk_id, "lang": "en", "title": en_title, "content": en_content})
    results.append({"id": chunk_id, "lang": "ru", "title": ru_title, "content": ru_content})

# ===== CHUNK 0: li_auto_l7_zh_23b117b7 — Smart Exit Limitations (continuation) =====
add(
    "li_auto_l7_zh_23b117b7",
    "Smart Exit Function Limitations",
    """- Manually turn the steering wheel.
- Tap the "Cancel" icon on the pause screen.

## II. Functional Limitations

Smart Exit is a driver assistance function and cannot fully replace the driver in assessing environmental information. It cannot guarantee successful exit on every attempt and has limitations in the following situations.

The Smart Exit system cannot perform an exit if mechanical system conditions are not met, which may affect the exit result or prevent the vehicle from exiting the parking space, including but not limited to:

- The steering wheel has a heavy steering wheel cover installed, preventing precise steering control at the intended angle during the parking control process.
- Non-original-size tires are in use.
- Tire pressure is insufficient or inconsistent.
- Snow chains are installed.

When the exit system is operating, due to the characteristics of ultrasonic radar, obstacle recognition may be degraded or objects may go undetected in the following situations, potentially causing vehicle damage or personal injury, including but not limited to:

- Significant ground seams or cracks are present within or beside the parking space.

*User Manual — Page 892*""",

    "Ограничения функции умного выезда",
    """- Вручную повернуть рулевое колесо.
- Нажать значок «Отмена» на экране паузы.

## II. Функциональные ограничения

Функция «Умный выезд» является функцией помощи водителю и не может полностью заменить водителя при оценке дорожной обстановки. Функция не гарантирует успешного выезда при каждой попытке и имеет ограничения в следующих ситуациях.

Система умного выезда не может выполнить выезд, если механические условия не соблюдены, что может ухудшить результат выезда или не позволить транспортному средству покинуть парковочное место, включая, но не ограничиваясь:

- На рулевом колесе установлен массивный чехол, из-за которого невозможно точно управлять поворотом под нужным углом в процессе управления парковкой.
- Используются шины нестандартного размера.
- Давление в шинах недостаточно или неодинаково.
- Установлены снежные цепи.

Во время работы системы выезда из-за особенностей ультразвукового радара распознавание препятствий может быть ухудшено или объекты могут не распознаваться в следующих ситуациях, что может привести к повреждению транспортного средства или травмам, включая, но не ограничиваясь:

- В парковочном месте или рядом с ним имеются значительные швы или трещины в покрытии.

*Руководство пользователя — Стр. 892*"""
)

# ===== CHUNK 1: li_auto_l7_zh_23fa0656 — Special Road Conditions =====
add(
    "li_auto_l7_zh_23fa0656",
    "Special Road Conditions",
    """# Special Road Conditions

## Special Road Conditions

Tap [Road Mode] in the bottom function bar of the center console screen to select from three special road condition modes: [Hill Descent Control], [Slippery Road], and [Off-Road Extraction].

- **Hill Descent Control (HDC):** The Hill Descent Control system applies braking force to the wheels when the vehicle is descending a slope, maintaining a stable speed.
- **Slippery Road:** Activate Slippery Road mode when driving on slippery surfaces. In Slippery Road mode, the vehicle adjusts the power output of the front and rear axles to reduce wheel slip, enabling smooth passage over icy, snowy, or muddy roads.
- **Off-Road Extraction:** Activate Off-Road Extraction mode when driving off-road. When activated, the system uses electronic traction control on the wheels to generate maximum traction, while automatically adjusting the suspension height to improve vehicle clearance and help the vehicle escape from difficult terrain.
- When none of the three special road condition modes is selected, the interface displays Road Mode, which is suitable for normal driving.
- In Off-Road Extraction mode, the vehicle's acceleration performance and cornering stability are limited. Please deactivate this mode when driving at high speed.

## Using Hill Descent Control (HDC)

When the Hill Descent Control system is active, the HDC indicator light on the center console screen illuminates.

Once activated, when the vehicle enters a downhill section, the HDC system begins operating and controls the vehicle speed to decrease to the set value for steady driving. At this point, the HDC indicator light on the center console screen flashes.

While the HDC system is operating, the driver can adjust vehicle speed by pressing the brake or accelerator pedal:

- Press the accelerator pedal, accelerate to the desired speed (speed ≤40 km/h), then release — the current speed becomes the new target speed.
- Press the brake pedal, decelerate to the desired speed (speed >5 km/h), then release — the current speed becomes the new target speed.

**Notes:**
- HDC only serves as an assistance function. The driver is always responsible for vehicle safety and must remain attentive to surrounding traffic at all times.
- Although HDC actively maintains a steady downhill speed, the driver should drive carefully to avoid accidents caused by excessive downhill speed.
- During HDC activation, friction continuously increases the braking system temperature. When the temperature reaches a certain level, the function may temporarily become ineffective and the vehicle may show signs of acceleration. In this case, the driver should pull over to a safe area. HDC will reactivate once the braking system temperature decreases.
- HDC cannot be activated when vehicle speed exceeds 40 km/h.
- When vehicle speed is between 40 km/h and 60 km/h, HDC enters standby mode; if speed exceeds 60 km/h, HDC will shut off.""",

    "Специальные дорожные условия",
    """# Специальные дорожные условия

## Специальные дорожные условия

Нажмите [Режим дороги] на нижней панели функций центрального дисплея, чтобы выбрать один из трёх режимов специальных дорожных условий: [Помощь при спуске], [Скользкая дорога] и [Внедорожное освобождение].

- **Помощь при спуске (HDC):** Система помощи при спуске прикладывает тормозное усилие к колёсам при движении под уклон, обеспечивая стабильную скорость.
- **Скользкая дорога:** Включайте режим скользкой дороги при движении по скользким поверхностям. В этом режиме автомобиль регулирует мощность передней и задней осей, снижая вероятность пробуксовки колёс и облегчая преодоление обледенелых, заснеженных или грязных дорог.
- **Внедорожное освобождение:** Включайте режим внедорожного освобождения при движении по бездорожью. При активации система использует электронное управление тягой на колёсах для создания максимальной тяги, автоматически регулируя высоту подвески для улучшения проходимости и помощи в освобождении автомобиля из сложных условий.
- Если ни один из трёх режимов специальных дорожных условий не выбран, на дисплее отображается режим «Обычная дорога», подходящий для нормального вождения.
- В режиме внедорожного освобождения ускорение и устойчивость в поворотах ограничены. При движении на высокой скорости этот режим следует отключить.

## Использование системы помощи при спуске (HDC)

При активации системы помощи при спуске на центральном дисплее загорается индикатор HDC.

После активации, когда автомобиль начинает движение под уклон, система HDC включается и управляет скоростью автомобиля, снижая её до заданного значения для равномерного движения. При этом индикатор HDC на центральном дисплее мигает.

Во время работы системы HDC водитель может регулировать скорость нажатием педали тормоза или акселератора:

- Нажмите педаль акселератора, разгонитесь до желаемой скорости (скорость ≤40 км/ч), затем отпустите — текущая скорость становится новой целевой скоростью.
- Нажмите педаль тормоза, снизьте скорость до желаемой (скорость >5 км/ч), затем отпустите — текущая скорость становится новой целевой скоростью.

**Примечания:**
- HDC выполняет лишь вспомогательную функцию. Водитель всегда несёт ответственность за безопасность автомобиля и должен постоянно следить за дорожной обстановкой.
- Хотя HDC активно поддерживает равномерную скорость при спуске, водитель должен ехать осторожно, чтобы избежать аварий из-за чрезмерной скорости.
- Во время активации HDC трение непрерывно повышает температуру тормозной системы. При достижении определённого уровня температуры функция может временно перестать работать, и автомобиль может начать ускоряться. В этом случае водитель должен съехать в безопасное место. HDC повторно активируется после снижения температуры тормозной системы.
- HDC нельзя активировать, когда скорость превышает 40 км/ч.
- При скорости от 40 до 60 км/ч HDC переходит в режим ожидания; при скорости свыше 60 км/ч HDC отключается."""
)

# ===== CHUNK 2: li_auto_l7_zh_24001ef6 — Snow Chains & Range Extender Notes =====
add(
    "li_auto_l7_zh_24001ef6",
    "Snow Chains and Range Extender Precautions",
    """- Snow chain thickness must not exceed 10 mm.
- Unsuitable snow chains may damage the vehicle's tires, wheels, and braking system. Select snow chains compatible with this vehicle's tires and refer to the snow chain manufacturer's instructions for use.
- Snow chains may only be installed on the rear wheels.
- After installing snow chains, do not exceed 50 km/h or the maximum speed permitted by the snow chain manufacturer, whichever is lower.
- Drive carefully; avoid road bumps, potholes, sharp turns, or wheel lock-up, as these may adversely affect the vehicle.
- To avoid wheel damage or excessive snow chain wear, snow chains must be removed when driving on roads without snow.

Applicable rim and tire size specifications for snow chains on this vehicle:

| Rim Specification | Tire Specification |
|-------------------|--------------------|
| 20×8.5J           | 255/50 R20         |
| 21×9.0J           | 265/45 R21         |

**WARNING:**
- Do not exceed road speed limits or the specified speed limit of the winter tires in use while driving.
- Do not drive on bumpy or pothole-filled roads.
- Do not use snow chains on roads without snow accumulation.
- Do not use tires outside of the specified specifications.
- Do not allow tire pressure to fall outside the recommended range.
- Do not exceed the speed limit specified for the snow chains being used.
- Do not perform sudden acceleration, steering, braking, or gear changes.
- Do not enter corners at high speed in order to maintain vehicle control.

## Range Extender Vehicle Precautions

### I. Traction Battery Precautions

If the traction battery charge is critically low, the vehicle can only be driven by the power generated by the range extender, resulting in very poor overall vehicle performance. Therefore, a portion of the battery charge should be reserved to handle more demanding driving conditions (e.g., overtaking, spirited driving, hill climbing).

*User Manual — Page 778*""",

    "Цепи противоскольжения и меры предосторожности для увеличителя запаса хода",
    """- Толщина цепей противоскольжения не должна превышать 10 мм.
- Неподходящие цепи могут повредить шины, колёса и тормозную систему автомобиля. Выбирайте цепи, совместимые с шинами данного автомобиля, и следуйте инструкции по применению цепей.
- Цепи противоскольжения разрешается устанавливать только на задние колёса.
- После установки цепей не превышайте скорость 50 км/ч или максимально допустимую скорость по инструкции производителя цепей — в зависимости от того, что меньше.
- Езжайте осторожно; избегайте дорожных неровностей, ям, резких поворотов и блокировки колёс — это может негативно повлиять на автомобиль.
- Во избежание повреждения колёс или чрезмерного износа цепей их необходимо снимать при езде по дорогам без снега.

Допустимые размеры обода и шин для установки цепей противоскольжения:

| Размер обода | Размер шины  |
|--------------|--------------|
| 20×8.5J      | 255/50 R20   |
| 21×9.0J      | 265/45 R21   |

**ПРЕДУПРЕЖДЕНИЕ:**
- Не превышайте ограничения скорости на дороге или допустимую скорость зимних шин при движении.
- Не ездите по неровным дорогам или дорогам с ямами.
- Не используйте цепи противоскольжения на дорогах без снежного покрова.
- Не используйте шины вне указанных спецификаций.
- Не допускайте выхода давления в шинах за пределы рекомендуемого диапазона.
- Не превышайте ограничение скорости, указанное для используемых цепей противоскольжения.
- Не выполняйте резкое ускорение, рулевые манёвры, торможение и переключение передач.
- Не входите в повороты на высокой скорости, чтобы сохранять контроль над автомобилем.

## Меры предосторожности для автомобиля с увеличителем запаса хода

### I. Меры предосторожности для тяговой батареи

Если заряд тяговой батареи критически низок, автомобиль может двигаться только за счёт энергии, вырабатываемой увеличителем запаса хода, что приводит к очень низкой общей производительности. Поэтому часть заряда батареи следует резервировать для более сложных условий вождения (например, обгон, интенсивное вождение, подъём в гору).

*Руководство пользователя — Стр. 778*"""
)

# ===== CHUNK 3: li_auto_l7_zh_2484047e — Rear AC Controls (continuation) =====
add(
    "li_auto_l7_zh_2484047e",
    "Rear Air Conditioning Controls",
    """**Note:** When the rear air conditioning is turned on while the front air conditioning is off, the front air conditioning will also turn on simultaneously.

### 2. Auto Off

This function is disabled by default. It can be enabled by tapping the "Auto Off" icon in the air conditioning system control interface. Once enabled, if the system detects no passengers in the rear seats, the rear air conditioning will automatically turn off after 10 minutes.

### 3. Temperature Setting

Tap the up/down arrow of the "Temperature" icon in the air conditioning system control interface to set the rear temperature. Each tap increases or decreases the temperature by 0.5°C; long press the up/down arrow of the "Temperature" icon for rapid temperature adjustment.

The set temperature is adjustable within the range of 16°C to 28°C. When the set temperature is 16°C, the display shows "Lo"; when the set temperature is 28°C, the display shows "Hi".

### 4. Fan Speed Setting

Tap the up/down arrow of the "Fan Speed" icon in the air conditioning system control interface to adjust the fan speed level. Each tap changes the fan speed by one level. Long press the up/down arrow of the "Fan Speed" icon for rapid fan speed adjustment.

In manual mode, the rear air conditioning has 9 fan speed levels available; in automatic mode, the rear air conditioning has 5 automatic levels available, with fan speed automatically adjusted within the selected level range.

### 5. Air Distribution Mode Setting

Tap any one or more of the icons under "Air Distribution Mode" in the air conditioning system control interface to set different combinations of air distribution modes. There are three modes available: face, feet, and face+feet.

### 6. AC Lock

This function is disabled by default. It can be enabled by tapping the "AC Lock" icon in the air conditioning system control interface. Once enabled, the rear air conditioning control panel is locked and cannot be operated.

### 7. Auto Mode

*Vehicle Usage Scenarios — Page 2414*""",

    "Управление задним кондиционером",
    """**Примечание:** При включении заднего кондиционера, если передний кондиционер выключен, он также включается одновременно.

### 2. Автоматическое отключение

По умолчанию эта функция выключена. Её можно включить, нажав значок «Авто. откл.» в интерфейсе управления системой кондиционирования. После включения, если система не обнаруживает пассажиров на задних сиденьях, задний кондиционер автоматически отключится через 10 минут.

### 3. Установка температуры

Нажмите стрелку вверх/вниз значка «Температура» в интерфейсе управления системой кондиционирования для настройки температуры в задней части. Каждое нажатие увеличивает или уменьшает температуру на 0,5°C; длительное нажатие стрелки вверх/вниз позволяет быстро регулировать температуру.

Установка температуры возможна в диапазоне от 16°C до 28°C. При установке 16°C на дисплее отображается «Lo»; при 28°C — «Hi».

### 4. Установка скорости вентилятора

Нажмите стрелку вверх/вниз значка «Скорость вентилятора» для регулировки уровня скорости обдува. Каждое нажатие изменяет скорость на одну ступень. Длительное нажатие стрелки позволяет быстро регулировать скорость вентилятора.

В ручном режиме задний кондиционер имеет 9 уровней скорости вентилятора; в автоматическом режиме — 5 автоматических уровней, скорость вентилятора регулируется автоматически в пределах выбранного диапазона.

### 5. Установка режима подачи воздуха

Нажмите один или несколько значков в разделе «Режим подачи воздуха» для настройки различных комбинаций распределения воздуха. Доступны три режима: на лицо, на ноги и на лицо + ноги.

### 6. Блокировка кондиционера

По умолчанию эта функция выключена. Её можно включить, нажав значок «Блокировка кондиционера». После включения панель управления задним кондиционером блокируется и не может использоваться.

### 7. Автоматический режим

*Сценарии использования — Стр. 2414*"""
)

# ===== CHUNK 4: li_auto_l7_zh_24fb9074 — Product Recall & Owner Change Records =====
add(
    "li_auto_l7_zh_24fb9074",
    "Product Recall and Owner Change Records",
    """- In the event of a product recall, Li Auto will provide a reasonable repair solution based on the product defect. In general, the problem can be resolved by repairing or replacing parts. To eliminate defects in the Li Auto L7 as quickly as possible and ensure owner driving safety, owners should actively cooperate with Li Auto to complete recall-related repair services after receiving a recall notice from Li Auto or learning of recall information through official channels.

## Owner Change Records

**Change Record 1**

| Field | Details |
|-------|---------|
| Current Owner (Company/Individual): | |
| Contact Person: | |
| Current Owner Address: | |
| ID Number: | |
| Postal Code: | |
| Current Owner Phone: | |
| Email: | |
| Mobile: | |
| Previous Owner (Company/Individual): | |
| Contact Person: | |
| Previous Owner Address: | |
| ID Number: | |
| Postal Code: | |
| Previous Owner Phone: | |
| Email: | |
| Mobile: | |
| Vehicle Identification Number (VIN): | |
| Drive Motor Number: | |
| Vehicle Model: | |
| Registration Date: | |
| Mileage at Transfer: | |
| Transfer Date: | |
| License Plate Number: | |
| Stamp: | |

**Change Record 2**

| Field | Details |
|-------|---------|
| Current Owner (Company/Individual): | |
| Contact Person: | |
| Current Owner Address: | |
| ID Number: | |
| Postal Code: | |
| Current Owner Phone: | |
| Email: | |
| Mobile: | |
| Previous Owner (Company/Individual): | |
| Contact Person: | |
| Previous Owner Address: | |
| ID Number: | |

*User Manual — Page 2070*""",

    "Отзывная кампания и записи о смене владельца",
    """- В случае отзывной кампании Li Auto предложит разумное решение по ремонту в соответствии с дефектом продукта. Как правило, проблема решается путём ремонта или замены деталей. Для скорейшего устранения дефектов Li Auto L7 и обеспечения безопасности езды владелец должен активно сотрудничать с Li Auto при прохождении сервисного обслуживания в рамках отзывной кампании после получения уведомления от Li Auto или ознакомления с информацией об отзыве по официальным каналам.

## Записи о смене владельца

**Запись о смене 1**

| Поле | Данные |
|------|--------|
| Текущий владелец (организация/ФЛ): | |
| Контактное лицо: | |
| Адрес текущего владельца: | |
| Номер удостоверения личности: | |
| Почтовый индекс: | |
| Телефон текущего владельца: | |
| Электронная почта: | |
| Мобильный телефон: | |
| Предыдущий владелец (организация/ФЛ): | |
| Контактное лицо: | |
| Адрес предыдущего владельца: | |
| Номер удостоверения личности: | |
| Почтовый индекс: | |
| Телефон предыдущего владельца: | |
| Электронная почта: | |
| Мобильный телефон: | |
| Идентификационный номер транспортного средства (VIN): | |
| Номер тягового электродвигателя: | |
| Модель автомобиля: | |
| Дата регистрации: | |
| Пробег при смене владельца: | |
| Дата смены владельца: | |
| Номерной знак: | |
| Печать: | |

**Запись о смене 2**

| Поле | Данные |
|------|--------|
| Текущий владелец (организация/ФЛ): | |
| Контактное лицо: | |
| Адрес текущего владельца: | |
| Номер удостоверения личности: | |
| Почтовый индекс: | |
| Телефон текущего владельца: | |
| Электронная почта: | |
| Мобильный телефон: | |
| Предыдущий владелец (организация/ФЛ): | |
| Контактное лицо: | |
| Адрес предыдущего владельца: | |
| Номер удостоверения личности: | |

*Руководство пользователя — Стр. 2070*"""
)

# ===== CHUNK 5: li_auto_l7_zh_2539f8ba — Warning and Indicator Lights (full table) =====
add(
    "li_auto_l7_zh_2539f8ba",
    "Warning Lights and Indicator Lights",
    """# Warning Lights and Indicator Lights

## III. Settings

In the center console screen Settings, tap "General", select "Preferences", tap the option under "Quick Control" to enter the Control Center customization interface:
- Tap the "-" or "+" at the top right of an icon to add or remove displayed items.
- Long press an icon and drag to set the display order.

## Warning Lights and Indicator Lights

The warning lights and indicator lights on the center console screen status bar show the driver the operating status of each vehicle system.

*Vehicle Usage Scenarios — Page 1207*

---

## I. Indicator Lights

| Icon | Name | Description |
|------|------|-------------|
| | Left Turn Signal Indicator | When flashing, indicates the left turn signal is active. |
| | Right Turn Signal Indicator | When flashing, indicates the right turn signal is active. |
| | Hazard Warning Light | When both the left and right turn signal indicators flash simultaneously, the hazard warning lights are active. |
| | Position Lamp Indicator | When illuminated, indicates the position lamps are on. |

*Page 1208*

| Icon | Name | Description |
|------|------|-------------|
| | Automatic Emergency Braking Suppression Indicator | When illuminated, indicates the AEB function is on, but is temporarily suppressed because an occupant is not seated or has not fastened their seatbelt. |
| | Low Beam Indicator | When illuminated, indicates the low beams are on. |
| | High Beam Indicator | When illuminated, indicates the high beams are on. |
| | Rear Fog Lamp Indicator | When illuminated, indicates the rear fog lamp is on. |
| | Smart Low Beam Indicator | When illuminated, indicates the smart low beam function is active. |
| | Smart High Beam On Indicator | Illuminates when the smart high beam function is on but the system has not activated the high beams. |
| | Smart High Beam Active Indicator | Illuminates when the smart high beam function is on and the system has activated the high beams. |
| | Anti-theft Authentication Failure Indicator | When illuminated, indicates vehicle anti-theft system authentication has failed. Contact Li Auto customer service. |
| | Electronic Parking Brake Indicator | Illuminates for a few seconds at vehicle startup, then goes out — indicates normal system. When illuminated, indicates the electronic parking brake is engaged. |

*Page 1209*

| Icon | Name | Description |
|------|------|-------------|
| | Hill Descent Control (HDC) Indicator | Illuminates for a few seconds at vehicle startup, then goes out — indicates normal system. When illuminated, indicates HDC is active. When flashing, indicates HDC is engaged. |
| | Auto Hold Indicator | When illuminated, indicates the auto hold function is activated. |
| | Charging Gun Connection Status Indicator | Illuminates when the vehicle is connected to a charging or discharging gun. |
| | READY Indicator | Illuminates when the vehicle is started. |
| | Charging Status Indicator | When illuminated, indicates the vehicle is being charged via a charging gun. |
| | Charging Complete Indicator | When illuminated, indicates vehicle charging is complete. |
| | Low Fuel Indicator | When illuminated, indicates remaining fuel is low — refuel promptly. |
| | Low Traction Battery Indicator | When illuminated, indicates traction battery charge is low — charge the vehicle promptly. |
| | Washer Fluid Level Indicator | When illuminated, indicates washer fluid level is abnormal — check the washer fluid level promptly. |

*Page 1210*

---

## II. Warning Lights

| Icon | Name | Description |
|------|------|-------------|
| | Brake System Fault Warning Light | Illuminates for a few seconds at vehicle startup, then goes out — indicates brake system and brake fluid level are normal. When illuminated, indicates low brake fluid level or a brake system fault. Pull over to a safe location and contact Li Auto customer service immediately — continuing to drive may be dangerous! |
| | Emission System Fault Warning Light | Illuminates for a few seconds at vehicle startup, then goes out — indicates emission system is normal. When illuminated, indicates an emission system fault. Drive carefully and contact Li Auto customer service or visit a Li Auto service center immediately to avoid vehicle damage or accidents. |
| | Airbag System Fault Warning Light | Illuminates for a few seconds at vehicle startup, then goes out — indicates airbag system is normal. When illuminated, indicates a fault in the airbag, airbag control unit, or seatbelt pretensioner. Contact Li Auto customer service. |
| | Low Engine Oil Pressure Indicator | Illuminates for a few seconds at vehicle startup, then goes out — indicates oil pressure sensor is normal. When illuminated, indicates abnormal oil level. Pull over to a safe location and contact Li Auto customer service immediately — continuing to drive may be dangerous! |

*Page 1211*

| Icon | Name | Description |
|------|------|-------------|
| | ABS System Fault Warning Light | Illuminates for a few seconds at vehicle startup, then goes out — indicates ABS system is normal. When illuminated, indicates an ABS fault. Drive carefully and contact Li Auto customer service or visit a service center immediately. |
| | Electric Power Steering (EPS) System Fault Warning Light | Illuminates for a few seconds at vehicle startup, then goes out — indicates EPS system is normal. When illuminated, indicates an EPS fault — greater steering force will be required. Contact Li Auto customer service as soon as possible. |
| | High-Voltage Disconnect Indicator | When illuminated, indicates the vehicle cannot receive high-voltage power. Contact Li Auto customer service as soon as possible. |
| | ESP System Operating/Fault Warning Light | Illuminates for a few seconds at vehicle startup, then goes out — indicates ESP system is normal. When flashing, indicates ESP is operating. When illuminated, indicates an ESP fault. Drive carefully and contact Li Auto customer service or visit a service center immediately. |
| | Traction Battery High Temperature Warning Light | When illuminated, indicates traction battery temperature is too high. Pull over to a safe location and contact Li Auto customer service — continuing to drive may be dangerous! |

*Page 1212*

| Icon | Name | Description |
|------|------|-------------|
| | Electronic Parking System Fault Warning Light | Illuminates for a few seconds at vehicle startup, then goes out — indicates EPB system is normal. When illuminated, indicates an EPB fault. Drive carefully and contact Li Auto customer service or visit a service center immediately. |
| | i-Booster Warning Light | Indicates a fault in the i-Booster (electromechanical brake booster) or ESP system. Drive carefully and contact Li Auto customer service or visit a service center immediately. |
| | Tire Pressure/Temperature Abnormal / TPMS Fault Warning Light | Illuminates for a few seconds at vehicle startup, then goes out — indicates TPMS is normal. When illuminated, indicates low tire pressure, high tire pressure, high tire temperature, or TPMS fault — check tire condition and contact Li Auto customer service or visit a service center if necessary. When flashing, indicates TPMS control module is not powered — contact Li Auto customer service or visit a service center. |
| | Drive System Fault Warning Light | Illuminates for a few seconds at vehicle startup, then goes out — indicates drive system is normal. When illuminated, indicates a drive system fault. Pull over to a safe location and contact Li Auto customer service — continuing to drive may be dangerous! |

*Page 1213*

| Icon | Name | Description |
|------|------|-------------|
| | Seatbelt Warning Light | When illuminated, indicates the driver, front passenger, or second-row passenger has not fastened their seatbelt. If the light remains on after fastening the seatbelt, contact Li Auto customer service. |
| | Range Extender Coolant High Temperature Indicator | Illuminates for a few seconds at vehicle startup, then goes out — indicates range extender cooling system is normal. When illuminated, indicates range extender coolant temperature is too high. Pull over to a safe location and contact Li Auto customer service — continuing to drive may be dangerous! |
| | Low 12V Battery / Battery System Fault Indicator | Illuminates for a few seconds at vehicle startup, then goes out — indicates 12V battery system is normal. When illuminated, indicates low 12V battery charge or a battery system fault. Contact Li Auto customer service. |
| | Exterior Lighting Fault Indicator | When illuminated, indicates a fault in the exterior lights. Contact Li Auto customer service. |
| | Drive System Power Limited Indicator | When illuminated, indicates overall vehicle power is limited. |
| | Brake Pad Wear Indicator | When illuminated, indicates brake pads have worn to the limit — visit a Li Auto service center to replace the brake pads promptly. |
| | Suspension Electronic Adjustment Fault Warning Light | When illuminated, indicates a fault in the suspension height control system — suspension height cannot be adjusted. Contact Li Auto customer service. |

*Page 1214*""",

    "Предупреждающие и контрольные лампы",
    """# Предупреждающие и контрольные лампы

## III. Настройки

В настройках центрального дисплея нажмите «Общие», выберите «Предпочтения», нажмите параметр под «Быстрое управление», чтобы войти в интерфейс настройки центра управления:
- Нажмите «-» или «+» в правом верхнем углу значка, чтобы добавить или удалить отображаемые элементы.
- Удерживайте значок и перетащите его, чтобы изменить порядок отображения.

## Предупреждающие и контрольные лампы

Предупреждающие и контрольные лампы на строке состояния центрального дисплея информируют водителя о рабочем состоянии каждой системы автомобиля.

*Сценарии использования — Стр. 1207*

---

## I. Контрольные лампы

| Значок | Название | Описание |
|--------|----------|----------|
| | Указатель левого поворота | При мигании — левый указатель поворота включён. |
| | Указатель правого поворота | При мигании — правый указатель поворота включён. |
| | Аварийная сигнализация | При одновременном мигании левого и правого указателей — аварийная сигнализация включена. |
| | Указатель габаритных огней | При свечении — габаритные огни включены. |

*Стр. 1208*

| Значок | Название | Описание |
|--------|----------|----------|
| | Индикатор подавления автоматического экстренного торможения | При свечении — функция АЭТ включена, но временно подавлена, так как пассажир не занял место или не пристегнул ремень. |
| | Индикатор ближнего света | При свечении — ближний свет включён. |
| | Индикатор дальнего света | При свечении — дальний свет включён. |
| | Индикатор заднего противотуманного фонаря | При свечении — задний противотуманный фонарь включён. |
| | Индикатор интеллектуального ближнего света | При свечении — функция интеллектуального ближнего света активна. |
| | Индикатор включения интеллектуального дальнего света | Светится, когда функция интеллектуального дальнего света включена, но система не активировала дальний свет. |
| | Индикатор активации интеллектуального дальнего света | Светится, когда функция интеллектуального дальнего света включена и система активировала дальний свет. |
| | Индикатор сбоя аутентификации противоугонной системы | При свечении — аутентификация противоугонной системы не прошла. Обратитесь в сервисный центр Li Auto. |
| | Индикатор электронного стояночного тормоза | При запуске автомобиля светится несколько секунд, затем гаснет — система в норме. При свечении — электронный стояночный тормоз активирован. |

*Стр. 1209*

| Значок | Название | Описание |
|--------|----------|----------|
| | Индикатор HDC (помощь при спуске) | При запуске автомобиля светится несколько секунд, затем гаснет — система в норме. При свечении — HDC включён. При мигании — HDC активирован. |
| | Индикатор автоматического удержания | При свечении — функция автоматического удержания активирована. |
| | Индикатор состояния подключения зарядного пистолета | Светится при подключении зарядного или разрядного пистолета. |
| | Индикатор READY | Светится при запуске автомобиля. |
| | Индикатор состояния зарядки | При свечении — автомобиль заряжается через зарядный пистолет. |
| | Индикатор завершения зарядки | При свечении — зарядка автомобиля завершена. |
| | Индикатор низкого уровня топлива | При свечении — оставшееся топливо на исходе, заправьтесь. |
| | Индикатор низкого заряда тяговой батареи | При свечении — заряд тяговой батареи низкий, зарядите автомобиль. |
| | Индикатор уровня жидкости стеклоомывателя | При свечении — уровень жидкости стеклоомывателя ненормальный, проверьте уровень. |

*Стр. 1210*

---

## II. Предупреждающие лампы

| Значок | Название | Описание |
|--------|----------|----------|
| | Предупреждающая лампа неисправности тормозной системы | При запуске светится несколько секунд, затем гаснет — тормозная система и уровень тормозной жидкости в норме. При свечении — низкий уровень тормозной жидкости или неисправность тормозной системы. Остановитесь в безопасном месте и немедленно обратитесь в сервис Li Auto — продолжение движения может быть опасным! |
| | Предупреждающая лампа неисправности системы выброса | При запуске светится несколько секунд, затем гаснет — система выброса в норме. При свечении — неисправность системы выброса. Езжайте осторожно и немедленно обратитесь в сервис Li Auto, чтобы избежать повреждения или аварии. |
| | Предупреждающая лампа неисправности системы подушек безопасности | При запуске светится несколько секунд, затем гаснет — система подушек безопасности в норме. При свечении — неисправность подушки безопасности, блока управления подушками или преднатяжителя ремня безопасности. Обратитесь в сервис Li Auto. |
| | Индикатор низкого давления масла | При запуске светится несколько секунд, затем гаснет — датчик давления масла в норме. При свечении — уровень масла ненормальный. Остановитесь в безопасном месте и немедленно обратитесь в сервис Li Auto — продолжение движения может быть опасным! |

*Стр. 1211*

| Значок | Название | Описание |
|--------|----------|----------|
| | Предупреждающая лампа неисправности ABS | При запуске светится несколько секунд, затем гаснет — ABS в норме. При свечении — неисправность ABS. Езжайте осторожно и немедленно обратитесь в сервис Li Auto. |
| | Предупреждающая лампа неисправности ЭУР | При запуске светится несколько секунд, затем гаснет — ЭУР в норме. При свечении — неисправность ЭУР, для управления рулём потребуется большее усилие. Как можно скорее обратитесь в сервис Li Auto. |
| | Индикатор отключения высокого напряжения | При свечении — автомобиль не может принять высокое напряжение. Как можно скорее обратитесь в сервис Li Auto. |
| | Предупреждающая лампа работы/неисправности ESP | При запуске светится несколько секунд, затем гаснет — ESP в норме. При мигании — ESP работает. При свечении — неисправность ESP. Езжайте осторожно и немедленно обратитесь в сервис Li Auto. |
| | Предупреждающая лампа перегрева тяговой батареи | При свечении — температура тяговой батареи слишком высокая. Остановитесь в безопасном месте и обратитесь в сервис Li Auto — продолжение движения может быть опасным! |

*Стр. 1212*

| Значок | Название | Описание |
|--------|----------|----------|
| | Предупреждающая лампа неисправности электронного стояночного тормоза | При запуске светится несколько секунд, затем гаснет — система EPB в норме. При свечении — неисправность EPB. Езжайте осторожно и немедленно обратитесь в сервис Li Auto. |
| | Предупреждающая лампа i-Booster | Неисправность i-Booster (электромеханического усилителя тормозов) или системы ESP. Езжайте осторожно и немедленно обратитесь в сервис Li Auto. |
| | Предупреждающая лампа аномального давления/температуры шин / неисправности TPMS | При запуске светится несколько секунд, затем гаснет — TPMS в норме. При свечении — низкое или высокое давление в шинах, высокая температура шины или неисправность TPMS. Проверьте состояние шин, при необходимости обратитесь в сервис Li Auto. При мигании — блок управления TPMS не под напряжением. Обратитесь в сервис Li Auto. |
| | Предупреждающая лампа неисправности системы привода | При запуске светится несколько секунд, затем гаснет — система привода в норме. При свечении — неисправность системы привода. Остановитесь в безопасном месте и немедленно обратитесь в сервис Li Auto — продолжение движения может быть опасным! |

*Стр. 1213*

| Значок | Название | Описание |
|--------|----------|----------|
| | Предупреждающая лампа непристёгнутого ремня безопасности | При свечении — водитель, передний пассажир или пассажир второго ряда не пристегнули ремень безопасности. Если лампа продолжает гореть после пристёгивания ремня, обратитесь в сервис Li Auto. |
| | Индикатор перегрева охлаждающей жидкости увеличителя запаса хода | При запуске светится несколько секунд, затем гаснет — система охлаждения увеличителя запаса хода в норме. При свечении — температура охлаждающей жидкости слишком высокая. Остановитесь в безопасном месте и немедленно обратитесь в сервис Li Auto — продолжение движения может быть опасным! |
| | Индикатор низкого заряда АКБ / неисправности аккумуляторной системы | При запуске светится несколько секунд, затем гаснет — система АКБ в норме. При свечении — низкий заряд АКБ или неисправность системы. Обратитесь в сервис Li Auto. |
| | Индикатор неисправности внешнего освещения | При свечении — неисправность внешнего освещения. Обратитесь в сервис Li Auto. |
| | Индикатор ограничения мощности системы привода | При свечении — мощность автомобиля ограничена. |
| | Индикатор износа тормозных колодок | При свечении — тормозные колодки изношены до предельного положения. Срочно посетите сервисный центр Li Auto для замены. |
| | Предупреждающая лампа неисправности электронной регулировки подвески | При свечении — неисправность системы регулировки высоты подвески, высота подвески не регулируется. Обратитесь в сервис Li Auto. |

*Стр. 1214*"""
)

# ===== CHUNK 6: li_auto_l7_zh_25506f9c — Smart Parking Assist System Sensors =====
add(
    "li_auto_l7_zh_25506f9c",
    "Smart Parking Assist System Sensors",
    """# Smart Parking Assist System Sensors

## Smart Parking Assist System Sensors

The smart parking assist system uses sensors such as cameras and ultrasonic radar to detect the surrounding environment and, based on detection results, assists the driver in taking appropriate actions to improve safety and comfort during parking.

## Surround-View Camera

Used during parking or low-speed driving to detect parking spaces, obstacles, and other objects around the vehicle, providing relevant information to the smart parking assist system.

Many factors can affect the performance of the surround-view cameras. The following situations may affect the normal operation of the parking system, including but not limited to:

- The left or right exterior rearview mirror cameras or front/rear cameras are damaged, causing them to malfunction or become misaligned.
- Camera lenses are dirty or obstructed.
- Ambient light is excessively bright — e.g., the camera is in direct sunlight.
- Ambient light is excessively dark — e.g., an unlit underground garage or nighttime.
- Significant and inconsistent ambient light variation — e.g., dappled shadows from trees, reflective epoxy-painted parking spaces.
- Parking space lines are unclear or the contrast between lines and the parking surface is low — e.g., tiled parking spaces, graffiti-marked spaces, wet tire tracks on the ground.
- Non-standard parking spaces — e.g., trapezoidal spaces with different widths at front and back, curved spaces in parking structures, spaces tight against a curb, ramp spaces, step spaces.
- Round or square columns beside the parking space, or concrete columns whose base color matches the floor color.
- Obstacles partially intruding into or pressed against the parking space.
- The system may be unable to identify and exclude parking spaces with no-parking markings, cones, no-parking signs, ground locks, or reserved parking designations.
- The system may be unable to exclude parking spaces with obstacles inside — e.g., pedestrians, bicycles, tricycles, low-lying objects, bricks.

**Notes:**
- It is strictly prohibited to disassemble or modify the cameras without authorization.
- The recognition range of cameras is limited — they cannot recognize objects beyond extreme distances or outside their field of view.
- Do not attach red ribbons or other decorations to the exterior rearview mirrors, and do not apply learner driver stickers around the cameras, as these may interfere with normal camera operation.
- If a camera malfunctions or is damaged, contact a Li Auto service center for repair or replacement promptly.

## Ultrasonic Radar

Used during parking or low-speed driving to detect obstacles around the vehicle, providing relevant information to the smart parking assist system.

Many factors can affect the performance of the ultrasonic radar. The following situations may affect the normal operation of the parking system, including but not limited to:

- Ultrasonic radar sensors are dirty or obstructed.
- Small objects, objects under the bumper, objects that are too close or too far from the vehicle.
- Suspended objects that the ultrasonic radar cannot detect.
- Surrounding ultrasonic noise of the same frequency — e.g., metal sounds, exhaust sounds.
- Obstacles that are thin or unable to reflect effective sound waves — e.g., wire mesh, fences, poles, ropes, shopping carts.
- Obstacles made of snow, cotton, or materials with sound-absorbing surfaces.
- Cone-shaped obstacles or objects with inclined surfaces.
- Right-angle objects — e.g., wall corners, vehicle rear ends.
- Parking on grass or uneven surfaces.
- Temperature stratification occurring near the radar.
- Ultrasonic radar damaged, misaligned, or covered by foreign objects or car covers.

**Notes:**
- To prevent ultrasonic radar detection performance from being limited, it is strictly prohibited to paint, modify, or alter the bumper without authorization.
- The detection range of the ultrasonic radar is limited — it cannot detect objects beyond its maximum range.
- If ultrasonic radar malfunctions or is damaged, contact a Li Auto service center for repair or replacement promptly.

## Radar Warning Settings

When the vehicle speed is below approximately 8 km/h and the ultrasonic radar detects obstacles around the vehicle, an audible warning is emitted. The radar warning sound and distance can be adjusted via the center console screen.

In the center console screen: [Settings] > [Sound] > [Volume] > [Radar Warning Volume] — set the radar warning volume to [Minimum], [Moderate], or [Maximum].

After setting, this is valid only for the current driving cycle. At the next vehicle startup, the default radar warning volume is [Moderate].

In the center console screen: [Settings] > [Sound] > [Volume] > [Radar Warning Distance] — set the radar warning distance to [Off], [Short], [Medium], or [Long].

After setting, this is valid only for the current driving cycle. At the next vehicle startup, the default radar warning distance is [Long].

| No. | Name | No. | Name |
|-----|------|-----|------|
| 1 | Ultrasonic Radar × 12 | 2 | Surround-View Camera × 4 |""",

    "Датчики системы умной помощи при парковке",
    """# Датчики системы умной помощи при парковке

## Датчики системы умной помощи при парковке

Система умной помощи при парковке использует датчики — камеры и ультразвуковые радары — для обнаружения окружающей обстановки и, на основе результатов обнаружения, помогает водителю принимать соответствующие меры для повышения безопасности и комфорта при парковке.

## Камера кругового обзора

Используется при парковке или движении на малой скорости для обнаружения парковочных мест, препятствий и других объектов вокруг автомобиля, предоставляя соответствующую информацию системе умной помощи при парковке.

На производительность камеры кругового обзора могут влиять многие факторы. Следующие ситуации могут нарушить нормальную работу системы парковки, включая, но не ограничиваясь:

- Камеры левого или правого наружного зеркала заднего вида или камеры спереди/сзади повреждены, что приводит к их неисправности или смещению.
- Объективы камер загрязнены или перекрыты.
- Освещённость слишком высокая — например, камера направлена прямо на солнечный свет.
- Освещённость слишком низкая — например, неосвещённый подземный гараж или ночное время.
- Значительные и непоследовательные изменения освещённости — например, пятнистые тени от деревьев, парковочные места с отражающим эпоксидным покрытием.
- Линии парковочного места нечёткие или контраст между линиями и покрытием низкий — например, плиточные парковочные места, места с граффити, следы от мокрых шин на земле.
- Нестандартные парковочные места — например, трапециевидные места с разной шириной спереди и сзади, изогнутые места в многоэтажных парковках, места вплотную к бордюру, пандусные или ступенчатые места.
- Круглые или квадратные колонны рядом с парковочным местом, или бетонные колонны, цвет плинтуса которых совпадает с цветом пола.
- Препятствия, частично вторгающиеся в парковочное место или вплотную прилегающие к нему.
- Система может быть не в состоянии идентифицировать и исключить парковочные места с запрещающей разметкой, конусами, знаками запрета стоянки, наземными замками или обозначениями специального назначения.
- Система может быть не в состоянии исключить парковочные места с препятствиями внутри — например, пешеходами, велосипедами, трициклами, низкими предметами, кирпичами.

**Примечания:**
- Строго запрещается самостоятельно разбирать или модифицировать камеры.
- Зона распознавания камер ограничена — они не могут распознавать объекты за пределами крайних расстояний или вне поля зрения.
- Не прикрепляйте красные ленты или другие украшения к наружным зеркалам заднего вида и не наклеивайте наклейки начинающего водителя рядом с камерами — это может нарушить нормальную работу камер.
- При неисправности или повреждении камеры незамедлительно обратитесь в сервисный центр Li Auto для ремонта или замены.

## Ультразвуковой радар

Используется при парковке или движении на малой скорости для обнаружения препятствий вокруг автомобиля, предоставляя соответствующую информацию системе умной помощи при парковке.

На производительность ультразвукового радара могут влиять многие факторы. Следующие ситуации могут нарушить нормальную работу системы парковки, включая, но не ограничиваясь:

- Датчики ультразвукового радара загрязнены или перекрыты.
- Маленькие объекты, объекты под бампером, объекты слишком близко или слишком далеко от автомобиля.
- Подвешенные объекты, которые ультразвуковой радар не может обнаружить.
- Окружающий ультразвуковой шум той же частоты — например, металлические звуки, звуки выхлопных газов.
- Препятствия, которые являются тонкими или не могут отражать эффективные звуковые волны — например, проволочная сетка, заборы, столбы, верёвки, тележки для покупок.
- Препятствия из снега, хлопка или материалов с поглощающими звук поверхностями.
- Конусообразные препятствия или объекты с наклонными поверхностями.
- Объекты с прямыми углами — например, углы стен, задние части автомобилей.
- Парковка на траве или неровных поверхностях.
- Температурное расслоение вблизи радара.
- Ультразвуковой радар повреждён, смещён или прикрыт посторонними предметами или чехлом автомобиля.

**Примечания:**
- Во избежание ограничения производительности ультразвукового радара строго запрещается красить, модифицировать или изменять бампер без разрешения.
- Зона обнаружения ультразвукового радара ограничена — он не может обнаруживать объекты за пределами максимального диапазона.
- При неисправности или повреждении ультразвукового радара незамедлительно обратитесь в сервисный центр Li Auto для ремонта или замены.

## Настройки предупреждения радара

Когда скорость автомобиля ниже приблизительно 8 км/ч и ультразвуковой радар обнаруживает препятствия вокруг автомобиля, подаётся звуковой сигнал. Звук и дальность предупреждения радара можно настроить через центральный дисплей.

На центральном дисплее: [Настройки] > [Звук] > [Громкость] > [Громкость предупреждения радара] — установите громкость предупреждения: [Минимум], [Средний] или [Максимум].

После настройки действует только в текущем цикле вождения. При следующем запуске автомобиля системой по умолчанию задаётся [Средний].

На центральном дисплее: [Настройки] > [Звук] > [Громкость] > [Дальность предупреждения радара] — установите дальность: [Откл.], [Близкая], [Средняя] или [Дальняя].

После настройки действует только в текущем цикле вождения. При следующем запуске автомобиля системой по умолчанию задаётся [Дальняя].

| № | Название | № | Название |
|---|----------|---|----------|
| 1 | Ультразвуковой радар × 12 | 2 | Камера кругового обзора × 4 |"""
)

# ===== CHUNK 7: li_auto_l7_zh_2559a80f — Lane Departure Assist Activation Conditions =====
add(
    "li_auto_l7_zh_2559a80f",
    "Lane Departure Assist — Activation Conditions",
    """## II. Function Activation

The lane departure assist function activates when all of the following conditions are simultaneously met:

- Vehicle speed is between 60 km/h and 135 km/h.
- The vehicle is within the current lane and has been traveling continuously for more than 5 seconds.
- The driver crosses a lane marking without activating the turn signal.

If the following conditions are met, the correction function will be forcibly activated even without the lane departure assist switch being enabled:

- Vehicle speed is between 45 km/h and 135 km/h.
- The vehicle is in Adaptive Cruise Control / Lane Keep Assist / Navigation Assisted Driving mode.
- The driver crosses a lane marking without activating the turn signal.

The following driver control actions may suppress activation of the lane departure assist function:

- Pressing the accelerator pedal.
- Pressing the brake pedal.
- Turning the steering wheel.
- Activating the turn signal or hazard warning lights.

*User Manual — Page 1848*""",

    "Помощь при выезде из полосы — условия активации",
    """## II. Активация функции

Функция помощи при выезде из полосы активируется при одновременном выполнении всех следующих условий:

- Скорость автомобиля составляет от 60 до 135 км/ч.
- Автомобиль находится в текущей полосе движения и непрерывно движется более 5 секунд.
- Водитель пересекает разметку полосы без включения указателя поворота.

Если выполняются следующие условия, функция коррекции принудительно активируется, даже если переключатель помощи при выезде из полосы не включён:

- Скорость автомобиля составляет от 45 до 135 км/ч.
- Автомобиль движется в режиме адаптивного круиз-контроля / поддержания полосы движения / навигационной помощи в вождении.
- Водитель пересекает разметку полосы без включения указателя поворота.

Следующие действия водителя по управлению автомобилем могут подавить активацию функции помощи при выезде из полосы:

- Нажатие педали акселератора.
- Нажатие педали тормоза.
- Поворот рулевого колеса.
- Включение указателя поворота или аварийной сигнализации.

*Руководство пользователя — Стр. 1848*"""
)

# ===== CHUNK 8: li_auto_l7_zh_258a0415 — Autonomous Lane Change: Waiting and In Progress =====
add(
    "li_auto_l7_zh_258a0415",
    "Autonomous Lane Change — Waiting and In Progress",
    """**Lane Change Waiting:** During a lane change, if the system detects that the target lane width is insufficient, there are other vehicles present, or the target lane boundary is a solid line, the assisted lane change function enters a waiting state. The center console screen displays a lane change waiting message and the guide line disappears.

**Lane Change Cancelled:** If the lane change waiting state exceeds approximately 30 seconds, the system will cancel the lane change and continue traveling in the current lane. The center console screen displays a lane change cancelled message. During the lane change, the driver can short-press the "Back" stalk on the right side of the steering wheel downward, or turn off the turn signal to cancel the lane change. If more than 1/4 of the vehicle body has already entered the target lane, the vehicle will continue merging into the target lane; if less than 1/4 of the vehicle body has entered the target lane, the vehicle will return to the original lane.

*Vehicle Usage Scenarios*

**Lane Change in Progress:** When the adjacent lane meets lane change conditions, the system will control the vehicle to execute the lane change. During the lane change, the center console screen displays a lane change in progress message, and a parking space frame appears in the target lane.

*Vehicle Usage Scenarios — Page 274*""",

    "Автономная смена полосы — ожидание и выполнение",
    """**Ожидание смены полосы:** Во время смены полосы, если система обнаруживает недостаточную ширину целевой полосы, наличие других транспортных средств или сплошную разметку на границе целевой полосы, функция вспомогательной смены полосы переходит в режим ожидания. На центральном дисплее отображается сообщение об ожидании смены полосы, а направляющая линия исчезает.

**Отмена смены полосы:** Если состояние ожидания смены полосы длится более 30 секунд, система отменяет смену полосы и продолжает движение в текущей полосе. На центральном дисплее отображается сообщение об отмене смены полосы. Во время смены полосы водитель может коротко нажать рычаг «Назад» справа на рулевом колесе вниз или выключить указатель поворота, чтобы отменить смену полосы. Если более 1/4 кузова автомобиля уже въехало в целевую полосу — автомобиль продолжит перестроение; если менее 1/4 кузова въехало в целевую полосу — автомобиль вернётся в исходную полосу.

*Сценарии использования*

**Смена полосы выполняется:** Когда соседняя полоса соответствует условиям смены полосы, система управляет автомобилем для выполнения смены полосы. В процессе смены полосы на центральном дисплее отображается сообщение о выполнении смены полосы, а в целевой полосе появляется рамка места стоянки.

*Сценарии использования — Стр. 274*"""
)

# ===== CHUNK 9: li_auto_l7_zh_25a116da — Airbag Non-Deployment Conditions (Side) & Customer Service Contact =====
add(
    "li_auto_l7_zh_25a116da",
    "Airbag Non-Deployment Conditions and Customer Service",
    """7. If the object that was collided with deforms or moves, the impact force from the collision may be reduced, and the airbag may not deploy.
8. When colliding head-on with a vehicle of equal weight at a stationary state, the airbag may not deploy.

However, regardless of the type of collision, as long as it causes sufficient forward deceleration, the front airbags may deploy.

## VI. Situations Where Side Airbags May Not Deploy

When the vehicle's side is struck at a certain angle to the vehicle body, or when the collision affects a side area of the body other than the passenger cabin, the side airbags and side curtain airbags may not deploy. Examples include:

1. A side collision affecting an area of the vehicle body other than the passenger cabin.
2. A side collision occurring at a certain angle to the vehicle body.

*Vehicle Usage Scenarios — Page 1067*

3. When the vehicle sustains a low-speed side collision or a rear collision, the side airbags and side curtain airbags generally will not deploy.
4. When the collision area is small (pole impact).

*Vehicle Usage Scenarios — Page 1068*

## VII. When to Contact Li Auto Customer Service

In the following situations, contact Li Auto customer service as soon as possible:

- Any airbag has deployed.
- The front of the vehicle is damaged or deformed, or the vehicle has sustained a collision that was not severe enough to deploy the front airbags.

*Vehicle Usage Scenarios — Page 1069*

- A certain part of the door is damaged or deformed, or the vehicle has sustained a collision that was not severe enough to deploy the side curtain airbags or side airbags.
- The steering wheel trim cover, or the instrument panel near the front passenger airbag, has scratches, cracks, or other damage.

*Vehicle Usage Scenarios — Page 1070*

- The seat surface in the side airbag installation area has scratches, cracks, or other damage.
- The side curtain airbag installation area has scratches, cracks, or other damage.

*Vehicle Usage Scenarios — Page 1071*""",

    "Условия несрабатывания подушек безопасности и обращение в сервис",
    """7. Если объект, с которым произошло столкновение, деформируется или перемещается, сила удара может уменьшиться, и подушка безопасности может не сработать.
8. При лобовом столкновении с автомобилем равного веса, находящимся в неподвижном состоянии, подушка безопасности может не сработать.

Однако, независимо от типа столкновения, если оно вызывает достаточное замедление вперёд, передние подушки безопасности могут сработать.

## VI. Ситуации, при которых боковые подушки безопасности могут не сработать

Если боковая часть автомобиля подвергается удару под определённым углом к кузову или если удар приходится на боковую область кузова, не являющуюся пассажирским салоном, боковые подушки безопасности и боковые шторки безопасности могут не сработать. Примеры:

1. Боковое столкновение, затрагивающее область кузова, не являющуюся пассажирским салоном.
2. Боковое столкновение, происходящее под определённым углом к кузову.

*Сценарии использования — Стр. 1067*

3. При низкоскоростном боковом столкновении или ударе сзади боковые подушки безопасности и боковые шторки, как правило, не срабатывают.
4. При небольшой площади контакта при столкновении (удар о столб).

*Сценарии использования — Стр. 1068*

## VII. Когда обращаться в сервисный центр Li Auto

В следующих ситуациях как можно скорее обратитесь в сервисный центр Li Auto:

- Любая подушка безопасности сработала.
- Передняя часть автомобиля повреждена или деформирована, или автомобиль получил удар, недостаточный для срабатывания передних подушек безопасности.

*Сценарии использования — Стр. 1069*

- Какая-либо часть двери повреждена или деформирована, или автомобиль получил удар, недостаточный для срабатывания боковых шторок или боковых подушек безопасности.
- На декоративной крышке рулевого колеса или на панели приборов рядом с подушкой безопасности переднего пассажира имеются царапины, трещины или иные повреждения.

*Сценарии использования — Стр. 1070*

- На поверхности сиденья в зоне установки боковой подушки безопасности имеются царапины, трещины или иные повреждения.
- В области установки боковой шторки безопасности имеются царапины, трещины или иные повреждения.

*Сценарии использования — Стр. 1071*"""
)

# ===== Write the output file =====
with open(OUTPUT, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"Written {len(results)} entries to {OUTPUT}")

# Verify
source_ids = [
    "li_auto_l7_zh_23b117b7",
    "li_auto_l7_zh_23fa0656",
    "li_auto_l7_zh_24001ef6",
    "li_auto_l7_zh_2484047e",
    "li_auto_l7_zh_24fb9074",
    "li_auto_l7_zh_2539f8ba",
    "li_auto_l7_zh_25506f9c",
    "li_auto_l7_zh_2559a80f",
    "li_auto_l7_zh_258a0415",
    "li_auto_l7_zh_25a116da",
]
out_ids = {e['id'] for e in results}
missing = set(source_ids) - out_ids
extra = out_ids - set(source_ids)
print(f"Expected 20 entries (10 chunks x 2 langs): {len(results) == 20}")
print(f"Missing IDs: {missing if missing else 'None'}")
print(f"Extra IDs: {extra if extra else 'None'}")
all_have_both = all(
    any(e['id'] == cid and e['lang'] == 'en' for e in results) and
    any(e['id'] == cid and e['lang'] == 'ru' for e in results)
    for cid in source_ids
)
print(f"All chunks have EN+RU: {all_have_both}")
print("DONE.")
