#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Translate batch_005.json chunks 38-49 (final)"""
import json

out_path = 'C:/Diagnostica-KB-Package/knowledge-base/translate_batches/batch_005_out.json'
with open(out_path, 'r', encoding='utf-8') as f:
    results = json.load(f)

def add(chunk_id, en_title, en_content, ru_title, ru_content):
    results.append({"id": chunk_id, "lang": "en", "title": en_title, "content": en_content})
    results.append({"id": chunk_id, "lang": "ru", "title": ru_title, "content": ru_content})

# ── CHUNK 38 ── li_auto_l7_zh_415287be  220V power outlet
add("li_auto_l7_zh_415287be",
"220V Power Outlet",
"""220V Power Outlet

Warning
Do not use devices with power exceeding 180W on the 12V power outlet to avoid fuse or circuit burnout or even fire due to excessive current.
Note
When the 12V power outlet is not in use, always keep the outlet cover closed to avoid damage from foreign objects or liquid entering the outlet.
220V Power Outlet
The 220V power outlet is located beneath the second-row seat cushion.
When the power is on, the 220V power outlet can supply power to devices rated at 220V with a maximum power of 1100W.
Driving Scenario


I. Enabling and Disabling
In the center console screen settings, tap "Vehicle", select "Maintenance", tap the "Power Outlet" icon. Set the 220V power outlet to on or off.
The 220V power outlet will automatically turn off or cannot be turned on in the following situations:
● Traction battery is too low.
● During vehicle OTA update.
● Connected device power is too high.
● A system fault has occurred.
Warning
● Do not use devices with power exceeding 1100W on the 220V power outlet to avoid circuit burnout or even fire due to excessive current.
● Do not allow children to touch the 220V power outlet to avoid children inserting fingers or other objects into the outlet causing electric shock or damage.
Driving Scenario""",
"220V Электрическая розетка",
"""220V Электрическая розетка

Предупреждение
Не используйте устройства мощностью более 180 Вт на 12В розетке во избежание перегорания предохранителей или проводки и даже пожара из-за чрезмерного тока.
Примечание
Когда 12В розетка не используется, всегда держите крышку розетки закрытой во избежание повреждения от попадания посторонних предметов или жидкости.
220В Электрическая розетка
220В электрическая розетка расположена под подушкой сиденья второго ряда.
При включённом питании 220В электрическая розетка может питать устройства с напряжением 220В и максимальной мощностью 1100 Вт.
Сценарий использования


I. Включение и выключение
В настройках центрального экрана нажмите «Автомобиль», выберите «Обслуживание», нажмите иконку «Электрическая розетка». Установите 220В электрическую розетку во включённое или выключенное состояние.
220В электрическая розетка автоматически выключится или не сможет быть включена в следующих ситуациях:
● Заряд тяговой батареи слишком низкий.
● Во время обновления автомобиля OTA.
● Мощность подключённого устройства слишком высока.
● Произошёл сбой системы.
Предупреждение
● Не используйте устройства мощностью более 1100 Вт на 220В розетке во избежание перегорания проводки и даже пожара из-за чрезмерного тока.
● Не позволяйте детям прикасаться к 220В розетке во избежание вставления пальцев или других предметов, что может вызвать поражение электрическим током или повреждение розетки.
Сценарий использования""")

# ── CHUNK 39 ── li_auto_l7_zh_41b01542  Maintenance schedule + hood opening
add("li_auto_l7_zh_41b01542",
"www.carobook.com",
"""

Range Extender Major Service
(engine oil, oil filter, air filter)
2 years
Range extender operated for 20,000 km
Spark Plug Service
Range extender operated for 40,000 km
Cabin Air Filter Service
1 year
Driven 20,000 km
Fluid Service
(front reducer oil, brake fluid)
4 years
Driven 80,000 km
Coolant Service
6 years
Driven 120,000 km
For Li Auto L7 vehicles frequently driven under the following harsh conditions, additional maintenance items or shortened maintenance intervals may be required — please contact a Li Auto Service Center for details:
● Driving in high-dust environments such as construction sites or deserts.
● Driving in extreme cold (below 0°C) or extreme heat (above 40°C) ambient temperatures.
● Driving in humid environments or frequent wading.
● Driving on roads with heavy salt or corrosive materials.
● Frequent hard acceleration and deceleration in mountainous conditions.
● Used as a taxi, for commercial operations, or frequently under heavy load or other special uses.
● Engaged in racing or competitive activities.
● Retrofitted or modified without Li Auto authorization.
Hood
I. Opening the Hood
1. Pull the hood release handle twice consecutively to unlock the hood.
User Manual
1985


2X""",
"www.carobook.com",
"""

Техническое обслуживание увеличителя запаса хода (ТО)
(моторное масло, масляный фильтр, воздушный фильтр)
2 года
Наработка увеличителя запаса хода 20 000 км
Обслуживание свечей зажигания
Наработка увеличителя запаса хода 40 000 км
Обслуживание фильтра салонного воздуха
1 год
Пробег 20 000 км
Обслуживание технических жидкостей
(масло переднего редуктора, тормозная жидкость)
4 года
Пробег 80 000 км
Обслуживание охлаждающей жидкости
6 лет
Пробег 120 000 км
Для автомобилей Li Auto L7, часто эксплуатируемых в следующих суровых условиях, могут потребоваться дополнительные виды технического обслуживания или сокращённые интервалы — обратитесь в сервисный центр Li Auto за подробной информацией:
● Движение в условиях высокой запылённости, например, на строительных площадках или в пустынях.
● Движение при экстремально низких (ниже 0°C) или экстремально высоких (выше 40°C) температурах окружающей среды.
● Движение во влажных условиях или частое преодоление водных преград.
● Движение по дорогам с большим количеством соли или коррозионных материалов.
● Частые резкие ускорения и торможения в горных условиях.
● Используется в качестве такси, для коммерческой деятельности или часто при высокой нагрузке или для других специальных целей.
● Участие в гонках или соревновательных мероприятиях.
● Модернизация или модификация без авторизации Li Auto.
Капот
I. Открытие капота
1. Дважды последовательно потяните ручку разблокировки капота для разблокировки.
Руководство пользователя
1985


2X""")

# ── CHUNK 40 ── li_auto_l7_zh_41ded843  LCC Full-scenario driving assistance
add("li_auto_l7_zh_41ded843",
"Full-Scenario Assisted Driving (LCC)",
"""Full-Scenario Assisted Driving (LCC)

## Full-Scenario Assisted Driving (LCC)

The Full-Scenario Assisted Driving function actively controls vehicle acceleration and deceleration, and through camera recognition of lane markings and traffic lights, the system controls the vehicle to stay in the center of the lane, autonomously changes lanes to overtake slower vehicles ahead, and autonomously responds to traffic light signals to stop or proceed on straight-through lanes.

## Settings

Go to Center Console > [Settings] > [AD Max] > [Smart Driving] > [Full-Scenario Assisted Driving (LCC)] to enable or disable Full-Scenario Assisted Driving.
After enabling Full-Scenario Assisted Driving, tap the options under [Highway Autonomous Lane Change] to enable or disable highway autonomous lane change.
Before using this function for the first time, complete the smart driving video learning and assessment. When lending the vehicle to others, log out of the account and inform the relevant personnel to complete the video learning and assessment before using this function.

## Activation and Exit

• Activation
Activation
When the vehicle is in Drive (D) gear, speed is between 0 and 130 km/h, and the turn signal is off, if the system determines the current environment meets the Full-Scenario Assisted Driving activation conditions, the center console screen will display a grey LCC icon. At this point, push the gear shifter down twice consecutively to activate Full-Scenario Assisted Driving. After activation, the LCC icon is highlighted, the center console screen prompts that assisted driving is enabled with an audible prompt. The current cruise lane is displayed in blue.
When Full-Scenario Assisted Driving is activated and Highway Autonomous Lane Change is enabled, if the vehicle's route passes through a highway, Highway Autonomous Lane Change will be activated.
Full-Scenario Assisted Driving on urban roads:
• Before intersections, changes to a straight-through lane; if unable to enter a straight-through lane in time, proceeds straight in a left/right-turn lane.
• When activated in a non-straight lane (left-turn, right-turn, or U-turn), autonomously changes to a straight-through lane.
• At T-intersections without a straight-through arrow, the vehicle will turn right.
• Exit
Exit
The driver can exit Full-Scenario Assisted Driving by pushing the gear shifter up, turning the steering wheel, or pressing the brake pedal. The system emits an exit tone and the center console screen displays that assisted driving has exited, and the highlighted LCC icon disappears.
In the following situations, Full-Scenario Assisted Driving will exit with a prompt — the driver should maintain vehicle control and intervene promptly:
• Deeply pressing the accelerator pedal for an extended time.
Deeply pressing the accelerator pedal for an extended time.
• Vehicle is not in Drive (D) gear.
Vehicle is not in Drive (D) gear.
• A door, trunk door, or front hood is opened.
A door, trunk door, or front hood is opened.
• Driver or passenger unfastens or has not fastened their seatbelt.
Driver or passenger unfastens or has not fastened their seatbelt.
• Vehicle is driving on a sharp curve.
Vehicle is driving on a sharp curve.
• Highway exit
Highway exit
When driving on a highway, if the system cannot detect lane markings, the wheels cross a lane marking, or the driver turns the steering wheel to control the vehicle, Full-Scenario Assisted Driving will exit. If the Takeover Deceleration Assist function is currently enabled, the vehicle will slowly decelerate to a stop. If Takeover Deceleration Assist is disabled, the vehicle will exit directly and hand control to the driver.

## Adjusting Cruise Speed

When assisted driving is active, scroll the right steering wheel roller up or down to adjust the cruise speed between 5 km/h and 130 km/h. Scroll up to increase cruise speed by 5 km/h; scroll down to decrease by 5 km/h.
One-touch speed limit setting: Press the right steering wheel roller — the system sets the cruise speed based on the current road speed limit and the driver's configured speed limit offset.
When assisted driving is active, the cruise speed can also be adjusted by tapping the [Cruise Speed] icon in the lower left of the environment perception interface on the center console screen.
When the driver actively accelerates beyond the set cruise speed, push the gear shifter down once to set the current speed as the cruise speed (e.g., if the current set cruise speed is 60 km/h and the vehicle is driven at 70 km/h by pressing the accelerator, push the shifter down once to change the cruise speed to 70 km/h).
• In heavy fog, the system automatically adjusts cruise speed and following distance and automatically turns on hazard warning lights and fog lights.
• In heavy snow or heavy rain, the system automatically adjusts cruise speed and following distance.
• The one-touch speed limit setting only takes effect once and will not change based on changes in road speed limits.
• Speed limit and speed camera information is for reference only; please follow actual road information and drive safely.
• In non-navigation mode, the speed limit information is the system's default road speed limit value, for reference only.
After function activation, when the right steering wheel roller is first scrolled, if the current cruise speed is not a multiple of 5 km/h, it directly jumps to the nearest multiple of 5 km/h (e.g., if the current set cruise speed is 43 km/h, scrolling up or down will increase it to 45 km/h or decrease it to 40 km/h).

## Adjusting Following Distance

When assisted driving is active, the following distance can also be adjusted by tapping the [Following Distance] icon in the lower left of the environment perception interface on the center console screen.
• The shorter the following distance, the less reaction time is reserved for the driver — the driver always has the responsibility to choose an appropriate following distance.
• Carefully adjust speed and following distance based on external factors such as traffic ahead, real-time weather, and road conditions to ensure safe driving.

## Assisted Lane Change

When vehicle speed is between 0 and 130 km/h and Full-Scenario Assisted Driving is active with an adjacent lane marked by a dashed line, after the driver activates the turn signal, the system will assess whether the adjacent lane conditions on the corresponding side meet the lane change requirements. If conditions are met, it will autonomously change to the adjacent lane.
The driver can follow these steps to use Assisted Lane Change:
• Confirm whether the target lane environment meets the lane change conditions (e.g., no rapidly approaching vehicle in the target lane).
Confirm whether the target lane environment meets the lane change conditions (e.g., no rapidly approaching vehicle in the target lane).
• Activate the turn signal on the corresponding side; when the system detects conditions are met, it autonomously executes the lane change.
Activate the turn signal on the corresponding side; when the system detects conditions are met, it autonomously executes the lane change.
• During the autonomous lane change, the driver must always monitor traffic conditions in the target lane, maintain vehicle control, and intervene promptly.
During the autonomous lane change, the driver must always monitor traffic conditions in the target lane, maintain vehicle control, and intervene promptly.
• Assisted Lane Change can only assist with one lane change at a time; consecutive lane changes require repeating the above steps.
• During the lane change preparation state, the current lane change can be cancelled by turning off the turn signal.
In the following scenarios when Assisted Lane Change is activated, the function will enter a waiting state and change lanes once target lane conditions are met:
• Lane markings on the change side do not meet requirements.
Lane markings on the change side do not meet requirements.
• A vehicle in the target lane is blocking the lane change.
A vehicle in the target lane is blocking the lane change.
• Curve radius is too small for the lane change.
Curve radius is too small for the lane change.
• After entering the waiting state for approximately 30 seconds, the system will cancel the lane change and continue in the current lane.
• Assisted Lane Change will display corresponding prompt information on the center console screen when operating.
During the lane change process:
• The vehicle will assess the scenario risk and decide to continue or cancel the lane change.
The vehicle will assess the scenario risk and decide to continue or cancel the lane change.
• If a vehicle approaches rapidly from behind and the vehicle centerline has already crossed the lane marking, continue with the lane change.
If a vehicle approaches rapidly from behind and the vehicle centerline has already crossed the lane marking, continue with the lane change.
• Assisted Lane Change is a driving assistance function — this function must never replace the driver's observation and judgment of traffic conditions. The driver should always keep hands on the wheel, maintain vehicle control, and bear responsibility for safe driving.
• When Assisted Lane Change is active, the system may not respond to rapidly approaching vehicles from the diagonal rear — the driver must cancel the lane change and intervene promptly.
• When Assisted Lane Change is active, the system cannot respond to vehicles simultaneously merging into the same target lane — the driver must cancel the lane change and intervene promptly.
• When there are no lane markings, multiple lane markings, worn markings, faint markings, or markings covered by other objects, the system may not operate normally.
• Do not use Assisted Lane Change when driving on roads with construction (e.g., construction signs, traffic cones).
• Do not use Assisted Lane Change on sharp curves, steep grades, icy, or slippery roads, or in rain, snow, or fog conditions.

## Traffic Light Response

When Full-Scenario Assisted Driving is active, the system uses perception information to autonomously respond to traffic light signals to stop or proceed in straight-through lanes.
When the system cannot confirm the traffic light status, it will prompt via the center console screen and voice, reminding the driver to confirm the status. The driver can confirm passage through the intersection by briefly pressing up the "OK" paddle on the right side of the steering wheel. If no confirmation is made, the system will control the vehicle to stop before the stop line.
• Press the "OK" button to confirm the traffic light status based on the actual situation. After confirmation, the system will control the vehicle to pass through the intersection ignoring the traffic light.
• Traffic light recognition may be incorrect — always monitor the road and system, maintain vehicle control, and intervene promptly.
• The system may not recognize temporary traffic lights, center-road traffic lights, or non-standard traffic lights.
• When multiple traffic lights exist, the system may not correctly identify them.
• Full-Scenario Assisted Driving cannot recognize traffic police hand signals — understand hand signal rules yourself to avoid violations.
• Full-Scenario Assisted Driving cannot recognize dynamic text on roadside electronic signs — always observe road conditions to avoid violations.
• Traffic lights placed too close together, obstructed traffic lights, or very high traffic light placement will affect system recognition — always monitor the road and system, maintain vehicle control, and intervene promptly.

## Highway Autonomous Lane Change

After enabling Highway Autonomous Lane Change and with Full-Scenario Assisted Driving active on a highway, the system will activate Highway Autonomous Lane Change and autonomously overtake slower vehicles ahead based on surrounding vehicle conditions.
During the lane change process:
• The vehicle will assess the scenario risk and decide to continue or cancel the lane change.
The vehicle will assess the scenario risk and decide to continue or cancel the lane change.
• If a vehicle approaches rapidly from behind and the vehicle centerline has already crossed the lane marking, continue with the lane change.
If a vehicle approaches rapidly from behind and the vehicle centerline has already crossed the lane marking, continue with the lane change.
Highway Autonomous Lane Change can only assist with one lane change at a time; consecutive lane changes are not possible.
• During autonomous overtaking, the driver should always pay attention to surrounding conditions and keep hands on the wheel, maintaining vehicle control and intervening promptly.
During autonomous overtaking, the driver should always pay attention to surrounding conditions and keep hands on the wheel, maintaining vehicle control and intervening promptly.
• To ensure driving safety, Highway Autonomous Lane Change does not support lane changes on curves (radius <500 m), ramps, or deceleration lanes.
To ensure driving safety, Highway Autonomous Lane Change does not support lane changes on curves (radius <500 m), ramps, or deceleration lanes.

## Takeover Deceleration Assist

Go to Center Console > [Settings] > [AD Max] > [Smart Driving] > [Takeover Deceleration Assist] to enable or disable the function; it is enabled by default.
When Full-Scenario Assisted Driving is active and Takeover Deceleration Assist is enabled, after driver operations cause the system to exit (e.g., driver turns the steering wheel), if the driver does not control the vehicle, the vehicle will slowly decelerate with audio-visual alerts to remind the driver.
When Full-Scenario Assisted Driving is active and Takeover Deceleration Assist is disabled, after driver operations cause the system to exit, the vehicle will fully hand control to the driver with audio-visual alerts.

## Driver Attention Monitoring Alert

When Full-Scenario Assisted Driving is active, the driver should maintain full attention; otherwise alerts may be triggered due to hands-off detection or distraction. For details, see "Driver Attention Monitoring System."
If the driver's hands are still not on the steering wheel, the center console screen will display [Please Take Over Immediately] with an audible alert.
If the driver's hands remain off the steering wheel for an extended period, the system will activate the hazard warning lights and control the vehicle to decelerate comfortably to a stop within the lane. 3 seconds after stopping, the system will automatically call the Li Auto human customer service and attempt to wake the driver. Until the gear is shifted to Park (P), Full-Scenario Assisted Driving cannot be activated again.

## Seatbelt Use

Full-Scenario Assisted Driving can only be activated after the driver and all passengers have fastened their seatbelts.
When activating assisted driving, if the system detects an unfastened seatbelt, the center console screen prompts the corresponding position with an audible alert.
When assisted driving is active, if the driver or passenger unfastens their seatbelt, the center console screen prompts for the unfastened seatbelt with an audible alert. If the driver unfastens their seatbelt, the alert lasts approximately 10 seconds; if the front passenger or rear passenger unfastens, the alert lasts approximately 60 seconds. If the alert exceeds the above time and the seatbelt remains unfastened, the center console screen displays [Please Take Over Immediately] with an audible alert and assisted driving exits.
After installing a child safety seat, the driver must set the child safety seat placement position in Center Console > [Settings] > [Vehicle] > [Seats] > [Child Seat Link] to ensure assisted driving functions normally.
Set [Child Seat Link] correctly; after selection, the child seat will not affect assisted driving use.

## Functional Limitations

In the following situations, Full-Scenario Assisted Driving may be limited or unable to operate normally, including but not limited to:
• Vehicle speed is outside the normal operating range.
Vehicle speed is outside the normal operating range.
• When vehicle speed is too high, the system may not be able to brake and decelerate in time for stationary targets.
When vehicle speed is too high, the system may not be able to brake and decelerate in time for stationary targets.
• The system cannot brake and decelerate for: pedestrians or slow-moving vehicles such as bicycles; red light intersections; lateral traffic (e.g., crossing vehicles, crossing pedestrians); oncoming vehicles; road obstacles (e.g., traffic cones, guardrails, guide signs).
The system cannot brake and decelerate for:
• Pedestrians or slow-moving vehicles such as bicycles.
Pedestrians or slow-moving vehicles such as bicycles.
• Red light intersections.
Red light intersections.
• Lateral traffic (e.g., crossing vehicles, crossing pedestrians).
Lateral traffic (e.g., crossing vehicles, crossing pedestrians).
• Oncoming vehicles.
Oncoming vehicles.
• Road obstacles (e.g., traffic cones, guardrails, guide signs).
Road obstacles (e.g., traffic cones, guardrails, guide signs).
• Camera imaging capability is affected, including but not limited to: poor visibility due to nighttime; adverse weather (heavy rain, heavy snow, heavy fog, sandstorms); strong light, backlighting, water reflections, extreme light contrast; camera obstructed by mud, ice, snow; degraded camera performance due to extreme heat or cold.
Camera imaging capability is affected, including but not limited to:
• Poor visibility due to nighttime conditions.
Poor visibility due to nighttime conditions.
• Adverse weather (heavy rain, heavy snow, heavy fog, sandstorms).
Adverse weather (heavy rain, heavy snow, heavy fog, sandstorms).
• Strong light, backlighting, water reflections, extreme light contrast.
Strong light, backlighting, water reflections, extreme light contrast.
• Camera obstructed by mud, ice, snow, etc.
Camera obstructed by mud, ice, snow, etc.
• Degraded camera performance due to extreme heat or cold.
Degraded camera performance due to extreme heat or cold.
• Millimeter-wave radar detection capability is affected, including but not limited to: radar affected by surrounding environment (electromagnetic interference, underground parking, tunnels, railway tracks, construction zones, width/height restriction frames); radar obstructed by mud, ice, snow; degraded radar performance due to extreme heat or cold.
Millimeter-wave radar detection capability is affected, including but not limited to:
• Radar affected by surrounding environment (electromagnetic interference, underground parking, tunnels, railway tracks, construction zones, width/height restriction frames).
Radar affected by surrounding environment (electromagnetic interference, underground parking, tunnels, railway tracks, construction zones, width/height restriction frames).
• Radar obstructed by mud, ice, snow, etc.
Radar obstructed by mud, ice, snow, etc.
• Degraded radar performance due to extreme heat or cold.
Degraded radar performance due to extreme heat or cold.
• LiDAR detection capability is affected, including but not limited to: adverse weather such as rain, snow, haze, sandstorms; direct strong light, backlighting, or water reflections; exhaust, splashing water, snowflakes, or dust from vehicles ahead; extreme heat or cold; LiDAR transceiver window obstructed by rain, mud, ice, frost, snow, or window film; LiDAR transceiver window damaged by external force.
LiDAR detection capability is affected, including but not limited to:
• Adverse weather such as rain, snow, haze, sandstorms.
Adverse weather such as rain, snow, haze, sandstorms.
• Direct strong light, backlighting, or water reflections.
Direct strong light, backlighting, or water reflections.
• Exhaust, splashing water, snowflakes, or dust kicked up by vehicles ahead.
Exhaust, splashing water, snowflakes, or dust kicked up by vehicles ahead.
• Extreme heat or cold weather conditions.
Extreme heat or cold weather conditions.
• LiDAR transceiver window obstructed by rain, mud, ice, frost, snow, or window film.
LiDAR transceiver window obstructed by rain, mud, ice, frost, snow, or window film.
• LiDAR transceiver window damaged by external force, showing scratches or cracks.
LiDAR transceiver window damaged by external force, showing scratches or cracks.
• Full-Scenario Assisted Driving is a driving assistance function that cannot handle all traffic, weather, and road conditions. The driver should still monitor vehicles ahead in real time, maintain appropriate following distance, control speed, brake in time, keep hands on the wheel, and maintain vehicle control and intervene promptly.
Full-Scenario Assisted Driving is a driving assistance function that cannot handle all traffic, weather, and road conditions. The driver should still monitor vehicles ahead in real time, maintain appropriate following distance, control speed, brake in time, keep hands on the wheel, and maintain vehicle control and intervene promptly.
• Do not use Full-Scenario Assisted Driving at road forks, merges, or similar locations.
Do not use Full-Scenario Assisted Driving at road forks, merges, or similar locations.
• Do not use Full-Scenario Assisted Driving on roads other than main roads or highways.
Do not use Full-Scenario Assisted Driving on roads other than main roads or highways.
• Do not use Full-Scenario Assisted Driving when driving on roads with construction (e.g., construction signs, traffic cones).
Do not use Full-Scenario Assisted Driving when driving on roads with construction (e.g., construction signs, traffic cones).
• Do not use Full-Scenario Assisted Driving on sharp curves, steep grades, icy, or slippery roads, or in rain, snow, or fog conditions.
Do not use Full-Scenario Assisted Driving on sharp curves, steep grades, icy, or slippery roads, or in rain, snow, or fog conditions.
• When there are no lane markings, multiple lane markings, worn markings, faint markings, or markings covered by other objects, the system may not operate normally.
When there are no lane markings, multiple lane markings, worn markings, faint markings, or markings covered by other objects, the system may not operate normally.
• If the following distance is too close to detect lane markings, the system may not operate normally.
If the following distance is too close to detect lane markings, the system may not operate normally.""",
"Всесценарное вспомогательное вождение (LCC)",
"""Всесценарное вспомогательное вождение (LCC)

## Всесценарное вспомогательное вождение (LCC)

Функция всесценарного вспомогательного вождения активно управляет разгоном и торможением автомобиля, а через распознавание разметки полос и светофоров с помощью камер система управляет автомобилем для удержания в центре полосы, самостоятельно меняет полосы для обгона медленных автомобилей впереди и самостоятельно реагирует на сигналы светофоров для остановки или проезда на прямолинейных полосах.

## Настройки

Перейдите в Центральный экран > [Настройки] > [AD Max] > [Интеллектуальное вождение] > [Всесценарное вспомогательное вождение (LCC)] для включения или отключения функции.
После включения опции всесценарного вспомогательного вождения нажмите параметры в разделе [Автономная смена полос на шоссе] для включения или отключения этой функции.
Перед первым использованием этой функции пройдите видеообучение и тестирование по интеллектуальному вождению. При передаче автомобиля другому лицу выйдите из аккаунта и сообщите соответствующим лицам о необходимости пройти видеообучение и тестирование.

## Активация и выход

• Активация
Активация
Когда автомобиль находится в режиме движения вперёд (D), скорость от 0 до 130 км/ч и поворотник выключен, если система определяет, что текущие условия соответствуют условиям активации всесценарного вспомогательного вождения, на центральном экране отобразится серая иконка LCC. В этот момент дважды последовательно переведите рычаг переключения передач вниз для активации. После активации иконка LCC подсвечивается, центральный экран уведомляет об активации вспомогательного вождения со звуковым сигналом. Текущая крейсерская полоса отображается синим цветом.
Когда всесценарное вспомогательное вождение активно и автономная смена полос на шоссе включена, при движении по шоссе автономная смена полос на шоссе будет активирована.
Всесценарное вспомогательное вождение на городских дорогах:
• Перед перекрёстками меняет полосу на прямолинейную; если не удаётся вовремя перейти в прямолинейную полосу, продолжает движение прямо в полосе поворота налево/направо.
• При активации в непрямолинейной полосе (поворот налево, направо или разворот) самостоятельно меняет на прямолинейную полосу.
• На Т-образных перекрёстках без стрелки прямо, автомобиль повернёт направо.
• Выход
Выход
Водитель может выйти из всесценарного вспомогательного вождения, переведя рычаг переключения вверх, повернув руль или нажав педаль тормоза. Система издаёт звуковой сигнал выхода, центральный экран уведомляет о выходе из вспомогательного вождения, и подсвеченная иконка LCC исчезает.
В следующих ситуациях всесценарное вспомогательное вождение выйдет с уведомлением — водитель должен поддерживать контроль и своевременно вмешиваться:
• Длительное глубокое нажатие педали акселератора.
Длительное глубокое нажатие педали акселератора.
• Автомобиль не в режиме движения вперёд (D).
Автомобиль не в режиме движения вперёд (D).
• Дверь, дверь багажника или капот открыты.
Дверь, дверь багажника или капот открыты.
• Водитель или пассажир расстегнул или не пристегнул ремень безопасности.
Водитель или пассажир расстегнул или не пристегнул ремень безопасности.
• Автомобиль движется по дороге с крутым поворотом.
Автомобиль движется по дороге с крутым поворотом.
• Выход на шоссе
Выход на шоссе
При движении по шоссе, если система не может обнаружить разметку полос, колёса пересекают разметку или водитель поворачивает руль для управления автомобилем, всесценарное вспомогательное вождение выйдет. Если функция помощи при замедлении при перехвате управления в данный момент включена, автомобиль будет плавно замедляться до остановки. Если функция отключена, автомобиль немедленно передаст управление водителю.

## Регулировка крейсерской скорости

При активном вспомогательном вождении прокрутите правый колёсик руля вверх или вниз для регулировки крейсерской скорости от 5 км/ч до 130 км/ч. Прокрутка вверх увеличивает на 5 км/ч; прокрутка вниз уменьшает на 5 км/ч.
Установка на скоростной лимит одним нажатием: нажмите правый колёсик руля — система установит крейсерскую скорость на основе текущего дорожного ограничения скорости и настроенного водителем смещения.
При активном вспомогательном вождении крейсерскую скорость также можно регулировать нажатием иконки [Крейсерская скорость] в нижнем левом углу интерфейса восприятия окружающей среды на центральном экране.
Когда водитель активно ускоряется сверх установленной крейсерской скорости, переведите рычаг переключения вниз один раз для установки текущей скорости как крейсерской (например, если установленная крейсерская скорость 60 км/ч, а нажатием педали акселератора достигнута скорость 70 км/ч, перевод рычага вниз один раз изменит крейсерскую скорость на 70 км/ч).
• В условиях сильного тумана система автоматически регулирует крейсерскую скорость и дистанцию и автоматически включает аварийные огни и противотуманные фонари.
• В условиях сильного снегопада или ливня система автоматически регулирует крейсерскую скорость и дистанцию.
• Функция установки на скоростной лимит одним нажатием действует только один раз и не меняется при изменении дорожного ограничения.
• Информация об ограничении скорости и камерах является справочной; руководствуйтесь фактической дорожной информацией.
• В режиме без навигации информация об ограничении скорости является значением по умолчанию, только для справки.
После активации функции, при первой прокрутке правого колёсика руля, если текущая крейсерская скорость не кратна 5 км/ч, она сразу перейдёт к ближайшему кратному 5 значению (например, при текущей крейсерской скорости 43 км/ч прокрутка вверх или вниз увеличит до 45 км/ч или уменьшит до 40 км/ч).

## Регулировка дистанции

При активном вспомогательном вождении дистанцию также можно регулировать нажатием иконки [Дистанция] в нижнем левом углу интерфейса восприятия окружающей среды на центральном экране.
• Чем короче дистанция, тем меньше времени реакции остаётся водителю — водитель всегда несёт ответственность за выбор подходящей дистанции.
• Осторожно регулируйте скорость и дистанцию с учётом внешних факторов, таких как интенсивность движения впереди, погода и состояние дороги.

## Вспомогательная смена полос

При скорости от 0 до 130 км/ч и активном всесценарном вспомогательном вождении с соседней полосой, размеченной пунктирной линией, после включения водителем поворотника система оценит, соответствуют ли условия соседней полосы требованиям смены полосы. При выполнении условий она самостоятельно перестроится.
Водитель может выполнить вспомогательную смену полос по следующим шагам:
• Убедитесь, что условия целевой полосы соответствуют требованиям смены (например, нет быстро приближающегося транспортного средства).
Убедитесь, что условия целевой полосы соответствуют требованиям смены (например, нет быстро приближающегося транспортного средства).
• Включите поворотник соответствующей стороны; при обнаружении системой выполнения условий она самостоятельно выполнит смену полосы.
Включите поворотник соответствующей стороны; при обнаружении системой выполнения условий она самостоятельно выполнит смену полосы.
• Во время автономной смены полосы водитель должен всегда следить за движением в целевой полосе, поддерживать контроль и своевременно вмешиваться.
Во время автономной смены полосы водитель должен всегда следить за движением в целевой полосе, поддерживать контроль и своевременно вмешиваться.
• Вспомогательная смена полос позволяет менять только одну полосу за раз; последовательная смена требует повторения шагов.
• В состоянии подготовки к смене полосы её можно отменить выключением поворотника.
В следующих сценариях функция перейдёт в режим ожидания и выполнит смену после соответствия условий:
• Разметка полосы со стороны смены не соответствует требованиям.
Разметка полосы со стороны смены не соответствует требованиям.
• Транспортное средство в целевой полосе препятствует смене.
Транспортное средство в целевой полосе препятствует смене.
• Радиус кривизны слишком мал для смены полосы.
Радиус кривизны слишком мал для смены полосы.
• После нахождения в режиме ожидания около 30 секунд система отменит смену и продолжит движение в текущей полосе.
• При работе вспомогательная смена полос отображает соответствующие сообщения на центральном экране.
В процессе смены полосы:
• Автомобиль оценит риски сценария и решит продолжить или отменить смену.
Автомобиль оценит риски сценария и решит продолжить или отменить смену.
• При быстром приближении транспортного средства сзади, если центральная линия автомобиля уже пересекла разметку, продолжить смену.
При быстром приближении транспортного средства сзади, если центральная линия автомобиля уже пересекла разметку, продолжить смену.
• Вспомогательная смена полос — функция помощи при вождении; она никогда не должна заменять наблюдение и суждение водителя. Держите руль обеими руками, поддерживайте контроль и несите ответственность за безопасное вождение.
• При активной вспомогательной смене система может не реагировать на быстро приближающиеся транспортные средства сзади-сбоку — водитель должен отменить смену и вмешаться.
• При активной вспомогательной смене система не реагирует на одновременное перестроение других транспортных средств в ту же целевую полосу — водитель должен отменить и вмешаться.
• При отсутствии разметки, нескольких разметках, стёртой, нечёткой или перекрытой разметке система может не работать нормально.
• Не используйте вспомогательную смену полос при движении по дорогам со строительными работами.
• Не используйте вспомогательную смену полос на крутых поворотах, крутых подъёмах, обледеневших или скользких дорогах или в дождь, снег, туман.

## Реагирование на светофоры

При активном всесценарном вспомогательном вождении система использует информацию восприятия для самостоятельного реагирования на сигналы светофоров для остановки или проезда на прямолинейных полосах.
Когда система не может подтвердить состояние светофора, она предупредит через центральный экран и голосом, напоминая водителю подтвердить состояние. Водитель может подтвердить проезд через перекрёсток, кратко нажав вверх рычажок «OK» на правой стороне руля. Если подтверждение не получено, система остановит автомобиль перед стоп-линией.
• Нажмите кнопку «OK» для подтверждения состояния светофора на основе реальной ситуации. После подтверждения система проведёт автомобиль через перекрёсток, игнорируя светофор.
• Распознавание светофоров может ошибаться — всегда следите за дорогой и системой, поддерживайте контроль.
• Система может не распознавать временные светофоры, центральные светофоры или нестандартные светофоры.
• При наличии нескольких светофоров система может не правильно их идентифицировать.
• Всесценарное вспомогательное вождение не распознаёт жесты сотрудников ГИБДД — изучите правила самостоятельно.
• Всесценарное вспомогательное вождение не распознаёт динамические текстовые сообщения на электронных дорожных знаках — всегда наблюдайте за дорогой.
• Слишком близко расположенные, перекрытые или слишком высоко установленные светофоры влияют на распознавание — всегда следите за дорогой и системой.

## Автономная смена полос на шоссе

После включения автономной смены полос на шоссе и при активном всесценарном вспомогательном вождении на шоссе система активирует автономную смену полос и самостоятельно обгоняет медленные автомобили впереди в зависимости от окружающей обстановки.
В процессе смены полосы:
• Автомобиль оценит риски сценария и решит продолжить или отменить смену.
Автомобиль оценит риски сценария и решит продолжить или отменить смену.
• При быстром приближении транспортного средства сзади, если центральная линия уже пересекла разметку, продолжить смену.
При быстром приближении транспортного средства сзади, если центральная линия уже пересекла разметку, продолжить смену.
Автономная смена полос на шоссе позволяет менять только одну полосу за раз.
• При автономном обгоне водитель должен всегда следить за обстановкой и держать руль, поддерживая контроль.
При автономном обгоне водитель должен всегда следить за обстановкой и держать руль, поддерживая контроль.
• В целях безопасности вождения автономная смена полос на шоссе не поддерживается на поворотах (радиус <500 м), съездах и полосах замедления.
В целях безопасности вождения автономная смена полос на шоссе не поддерживается на поворотах (радиус <500 м), съездах и полосах замедления.

## Функция помощи при замедлении при перехвате управления

Перейдите в Центральный экран > [Настройки] > [AD Max] > [Интеллектуальное вождение] > [Помощь при замедлении при перехвате] для включения или отключения; по умолчанию включена.
При активном всесценарном вспомогательном вождении и включённой помощи при замедлении при перехвате, после выхода системы из-за действий водителя (например, поворот руля), если водитель не управляет автомобилем, автомобиль будет плавно замедляться с аудио-визуальными оповещениями.
При активном всесценарном вспомогательном вождении и отключённой помощи при замедлении при перехвате, после выхода из-за действий водителя, автомобиль полностью передаст управление водителю с аудио-визуальными оповещениями.

## Мониторинг внимательности водителя

При активном всесценарном вспомогательном вождении водитель должен поддерживать полное внимание; иначе могут срабатывать предупреждения из-за обнаружения отпускания руля или отвлечения. Подробнее см. «Система мониторинга внимательности водителя».
Если руки водителя всё ещё не на руле, центральный экран отобразит [Немедленно возьмите управление] со звуковым сигналом.
Если руки водителя длительное время не держат руль, система включит аварийные огни и остановит автомобиль плавным замедлением в полосе. Через 3 секунды после остановки система автоматически свяжется с живой службой поддержки Li Auto и попытается разбудить водителя. До переключения в режим парковки (P) активация всесценарного вспомогательного вождения будет невозможна.

## Использование ремней безопасности

Всесценарное вспомогательное вождение можно активировать только после того, как водитель и все пассажиры пристегнули ремни безопасности.
При активации вспомогательного вождения, если система обнаруживает непристёгнутый ремень, центральный экран уведомляет о соответствующем месте со звуковым сигналом.
При активном вспомогательном вождении, если водитель или пассажир расстёгивает ремень, центральный экран уведомляет о непристёгнутом ремне. Если водитель расстёгивает ремень, оповещение длится около 10 секунд; если пассажир — около 60 секунд. Если время оповещения превышает указанное и ремень не пристёгнут, центральный экран отображает [Немедленно возьмите управление] со звуковым сигналом и вспомогательное вождение выходит.
После установки детского кресла водитель должен настроить положение детского кресла в Центральный экран > [Настройки] > [Автомобиль] > [Сиденья] > [Синхронизация детского кресла] для нормальной активации вспомогательного вождения.
Правильно установите [Синхронизацию детского кресла]; после выбора детское кресло не будет влиять на использование вспомогательного вождения.

## Ограничения функции

В следующих ситуациях всесценарное вспомогательное вождение может быть ограничено или не работать нормально, включая, но не ограничиваясь:
• Скорость автомобиля вне нормального рабочего диапазона.
Скорость автомобиля вне нормального рабочего диапазона.
• При слишком высокой скорости система может не успеть затормозить и замедлиться для неподвижных объектов.
При слишком высокой скорости система может не успеть затормозить и замедлиться для неподвижных объектов.
• Система не может тормозить и замедляться для: пешеходов или медленных транспортных средств, таких как велосипеды; перекрёстков со светофором на красный; поперечного движения; встречных автомобилей; дорожных препятствий.
Система не может тормозить и замедляться для:
• Пешеходов или медленных транспортных средств, таких как велосипеды.
Пешеходов или медленных транспортных средств, таких как велосипеды.
• Перекрёстков со светофором на красный.
Перекрёстков со светофором на красный.
• Поперечного движения (например, поперечные автомобили, пешеходы).
Поперечного движения (например, поперечные автомобили, пешеходы).
• Встречных автомобилей.
Встречных автомобилей.
• Дорожных препятствий (например, конусы, ограждения, знаки).
Дорожных препятствий (например, конусы, ограждения, знаки).
• Нарушение работы камеры — аналогично описанному выше.
Нарушение работы камеры, включая, но не ограничиваясь:
• Плохая видимость из-за ночного времени.
Плохая видимость из-за ночного времени.
• Неблагоприятные погодные условия (сильный дождь, снег, туман, песчаные бури).
Неблагоприятные погодные условия (сильный дождь, снег, туман, песчаные бури).
• Яркий свет, контровой свет, отражения от воды, экстремальный световой контраст.
Яркий свет, контровой свет, отражения от воды, экстремальный световой контраст.
• Камера заблокирована грязью, льдом, снегом и т.д.
Камера заблокирована грязью, льдом, снегом и т.д.
• Снижение производительности камеры из-за экстремального тепла или холода.
Снижение производительности камеры из-за экстремального тепла или холода.
• Нарушение работы миллиметрового радара — аналогично описанному выше.
Нарушение работы миллиметрового радара, включая, но не ограничиваясь:
• Радар подвержен влиянию окружающей среды.
Радар подвержен влиянию окружающей среды.
• Радар заблокирован грязью, льдом, снегом и т.д.
Радар заблокирован грязью, льдом, снегом и т.д.
• Снижение производительности радара из-за экстремального тепла или холода.
Снижение производительности радара из-за экстремального тепла или холода.
• Нарушение работы лидара — аналогично описанному выше.
Нарушение работы лидара, включая, но не ограничиваясь:
• Неблагоприятные погодные условия: дождь, снег, смог, песчаные бури.
Неблагоприятные погодные условия: дождь, снег, смог, песчаные бури.
• Прямой яркий свет, контровой свет или отражения от воды.
Прямой яркий свет, контровой свет или отражения от воды.
• Выхлоп, брызги, снежинки или пыль от впередиидущих транспортных средств.
Выхлоп, брызги, снежинки или пыль от впередиидущих транспортных средств.
• Экстремальные погодные условия.
Экстремальные погодные условия.
• Приёмо-передающее окно лидара заблокировано.
Приёмо-передающее окно лидара заблокировано.
• Приёмо-передающее окно лидара повреждено внешней силой.
Приёмо-передающее окно лидара повреждено внешней силой.
• Всесценарное вспомогательное вождение — это функция помощи при вождении, которая не может справляться со всеми условиями движения, погоды и дороги. Водитель по-прежнему должен в реальном времени следить за автомобилями впереди, поддерживать дистанцию, контролировать скорость, своевременно тормозить, держать руль и поддерживать контроль.
Всесценарное вспомогательное вождение — это функция помощи при вождении, которая не может справляться со всеми условиями движения, погоды и дороги. Водитель по-прежнему должен в реальном времени следить за автомобилями впереди, поддерживать дистанцию, контролировать скорость, своевременно тормозить, держать руль и поддерживать контроль.
• Не используйте всесценарное вспомогательное вождение на развилках, слияниях и подобных местах.
Не используйте всесценарное вспомогательное вождение на развилках, слияниях и подобных местах.
• Не используйте на дорогах, кроме главных дорог или шоссе.
Не используйте на дорогах, кроме главных дорог или шоссе.
• Не используйте при движении по дорогам со строительными работами.
Не используйте при движении по дорогам со строительными работами.
• Не используйте на крутых поворотах, крутых подъёмах, обледеневших или скользких дорогах или в дождь, снег, туман.
Не используйте на крутых поворотах, крутых подъёмах, обледеневших или скользких дорогах или в дождь, снег, туман.
• При отсутствии разметки, нескольких разметках, стёртой, нечёткой или перекрытой разметке система может не работать нормально.
При отсутствии разметки, нескольких разметках, стёртой, нечёткой или перекрытой разметке система может не работать нормально.
• Если дистанция слишком мала для обнаружения разметки полос, система может не работать нормально.
Если дистанция слишком мала для обнаружения разметки полос, система может не работать нормально.""")

# ── CHUNK 41 ── li_auto_l7_zh_425de5eb  Smart key precautions + find vehicle
add("li_auto_l7_zh_425de5eb",
"www.carobook.com",
"""

Note
● When exiting the vehicle, always carry all smart keys to avoid them being locked inside.
● Smart keys are affected by electronic devices (e.g., phones, computers), magnetic materials, and the electromagnetic environment around the vehicle; key signals may be interfered with, causing temporary key malfunction or unstable operation.
● Do not place the smart key in the trunk — it may be accidentally locked inside.
● Do not place the smart key in the trunk — it may cause a "smart key not found" prompt preventing the vehicle from starting.
II. Find Vehicle Function
Within the effective range, press the key lock button twice within 1.5 seconds; the vehicle turn signals will flash 10 times and the horn will sound 2 times.
When the vehicle is in find-vehicle mode, pressing the key lock button twice again within 1.5 seconds restarts the next find-vehicle cycle.
Note
When unable to determine the vehicle's location in a parking lot, use this function to find the exact vehicle location.
Driving Scenario
2142""",
"www.carobook.com",
"""

Примечание
● При выходе из автомобиля всегда берите с собой все умные ключи во избежание их блокировки внутри.
● На умные ключи влияют электронные устройства (например, телефоны, компьютеры), магнитные материалы и электромагнитная среда вокруг автомобиля; сигналы ключей могут подвергаться помехам, вызывая временную неисправность или нестабильную работу.
● Не кладите умный ключ в багажник — он может быть случайно заблокирован внутри.
● Не кладите умный ключ в багажник — это может вызвать сообщение «умный ключ не найден», препятствующее запуску автомобиля.
II. Функция поиска автомобиля
В пределах эффективного диапазона нажмите кнопку блокировки ключа дважды в течение 1,5 секунды; поворотники автомобиля мигнут 10 раз и клаксон прозвучит 2 раза.
Когда автомобиль находится в режиме поиска, повторное двойное нажатие кнопки блокировки в течение 1,5 секунды запускает следующий цикл поиска.
Примечание
При невозможности определить местоположение автомобиля на парковке используйте эту функцию для точного поиска.
Сценарий использования
2142""")

# ── CHUNK 42 ── li_auto_l7_zh_425e6b97  LDA limitations
add("li_auto_l7_zh_425e6b97",
"www.carobook.com",
"""

III. Functional Limitations
In the following situations, the Lane Departure Assist function may be limited or unable to operate normally, including but not limited to:
● Outside the normal operating speed range.
● Vehicle is driving on a sharp curve such as a highway ramp.
● Following distance is too close to detect lane markings.
● Vehicle is driving on roads with many surface joints.
● Vehicle is driving on slopes, roads with large vertical undulations, or the vehicle is severely tilted due to heavy load or abnormal tire pressure.
● Vehicle is passing through road sections with special lane markings such as speed reduction markings, diversion lines, or variable guidance lane markings.
● Vehicle is driving on roads without lane markings, with unclear lane markings, or unclear road division, such as non-standard roads, intersections, construction zones, or areas where lane markings merge or split.
● Camera imaging capability is affected, including but not limited to:
◆ Poor visibility due to nighttime conditions.
◆ Poor visibility due to adverse weather (heavy rain, heavy snow, heavy fog, sandstorms).
◆ Strong light, backlighting, water reflections, extreme light contrast.
◆ Camera obstructed by mud, ice, snow, etc.
◆ Degraded camera performance due to extreme heat or cold.
Warning
● Lane Departure Assist is a driving assistance function and must never replace the driver's observation and judgment of traffic conditions, nor the driver's responsibility for safe vehicle operation.
● Drivers must not become overly reliant on Lane Departure Assist, must not intentionally test or wait for function triggering. Due to inherent system limitations, false triggers and missed triggers cannot be completely avoided.
● Do not use Lane Departure Assist at road forks, merges, or similar locations.
● Do not use Lane Departure Assist when the vehicle is using a spare tire or tire anti-skid chains.
● Do not use Lane Departure Assist when tires are excessively worn or tire pressure is too low.
● Do not use Lane Departure Assist when tires of different structures, manufacturers, brands, or tread patterns are mixed.
● Do not use Lane Departure Assist when driving on roads with construction (e.g., construction signs, traffic cones).
● Do not use Lane Departure Assist on sharp curves, steep grades, icy, or slippery roads, or in rain, snow, or fog conditions.
User Manual
817""",
"www.carobook.com",
"""

III. Ограничения функции
В следующих ситуациях функция помощи при отклонении от полосы может быть ограничена или не работать нормально, включая, но не ограничиваясь:
● Вне нормального рабочего диапазона скоростей.
● Автомобиль движется по дороге с крутыми поворотами, например, по съезду с шоссе.
● Дистанция слишком мала для обнаружения разметки полос.
● Автомобиль движется по дорогам с многочисленными стыками покрытия.
● Автомобиль движется по уклонам, дорогам с большими вертикальными неровностями или автомобиль сильно наклонён из-за тяжёлого груза или аномального давления в шинах.
● Автомобиль проезжает через участки с особой разметкой полос, такой как разметка снижения скорости, разделительные линии или разметка изменяемых полос.
● Автомобиль движется по дорогам без разметки полос, с нечёткой разметкой или нечётким разделением дороги, например, нестандартные дороги, перекрёстки, строительные зоны или зоны слияния/разделения полос.
● Нарушение работы камеры, включая, но не ограничиваясь:
◆ Плохая видимость из-за ночного времени.
◆ Плохая видимость из-за неблагоприятных погодных условий (сильный дождь, снег, туман, песчаные бури).
◆ Яркий свет, контровой свет, отражения от воды, экстремальный световой контраст.
◆ Камера заблокирована грязью, льдом, снегом и т.д.
◆ Снижение производительности камеры из-за экстремального тепла или холода.
Предупреждение
● Помощь при отклонении от полосы является функцией помощи при вождении и никогда не должна заменять наблюдение и суждение водителя о дорожной обстановке.
● Водители не должны чрезмерно полагаться на эту функцию, намеренно проверять или ожидать её срабатывания. Из-за неотъемлемых ограничений системы ложные и пропущенные срабатывания не могут быть полностью исключены.
● Не используйте помощь при отклонении от полосы на развилках, слияниях и подобных местах.
● Не используйте при использовании запасной шины или противоскользящих цепей.
● Не используйте при чрезмерном износе шин или слишком низком давлении.
● Не используйте при смешивании шин разных конструкций, производителей, марок или рисунков протектора.
● Не используйте при движении по дорогам со строительными работами.
● Не используйте на крутых поворотах, крутых подъёмах, обледеневших или скользких дорогах или в дождь, снег, туман.
Руководство пользователя
817""")

# ── CHUNK 43 ── li_auto_l7_zh_429805b9  Warning lights (seatbelt, range extender temp, etc.)
add("li_auto_l7_zh_429805b9",
"www.carobook.com",
"""

Icon | Name
Seatbelt unfastened warning light | If the warning light is lit, it indicates the driver, front passenger, or second-row passenger has not properly fastened their seatbelt. If the warning light remains lit after fastening the seatbelt, contact the Li Auto Customer Service Center.
Range extender high coolant temperature indicator | When the vehicle starts, this indicator illuminates for a few seconds then goes out, indicating the range extender cooling system is normal. If the indicator remains lit, the range extender coolant temperature is too high — park the vehicle in a safe location and contact the Li Auto Customer Service Center. Continuing to drive may be dangerous!
Low auxiliary battery / auxiliary battery system fault indicator | When the vehicle starts, this indicator illuminates for a few seconds then goes out, indicating the auxiliary battery system is normal. If the indicator remains lit, the auxiliary battery is low or there is an auxiliary battery system fault — contact the Li Auto Customer Service Center.
Exterior lighting fault indicator | If the indicator is lit, there is an exterior lighting fault — contact the Li Auto Customer Service Center.
Drive system power limited indicator | If the indicator is lit, the overall vehicle power is limited.
Brake pad wear indicator | If the indicator is lit, the vehicle brake pads have worn to the limit position — promptly go to a Li Auto Service Center for brake pad replacement.
Electronic suspension adjustment fault warning light | If the warning light is lit, there is a suspension height control system fault — suspension height cannot be adjusted — contact the Li Auto Customer Service Center.
Driving Scenario
1214""",
"www.carobook.com",
"""

Иконка | Название
Предупреждающий сигнал непристёгнутого ремня безопасности | Если предупреждающий сигнал горит, это означает, что водитель, передний пассажир или пассажир второго ряда не пристегнул ремень безопасности должным образом. Если после пристёгивания ремня предупреждающий сигнал всё ещё горит, свяжитесь с центром обслуживания клиентов Li Auto.
Индикатор высокой температуры охлаждающей жидкости увеличителя запаса хода | При запуске автомобиля этот индикатор горит несколько секунд, затем гаснет, что означает нормальную работу системы охлаждения увеличителя запаса хода. Если индикатор продолжает гореть, температура охлаждающей жидкости увеличителя запаса хода слишком высокая — припаркуйте автомобиль в безопасном месте и свяжитесь с центром обслуживания клиентов Li Auto. Продолжение движения может быть опасным!
Индикатор низкого заряда вспомогательной батареи / неисправности системы вспомогательной батареи | При запуске автомобиля этот индикатор горит несколько секунд, затем гаснет, что означает нормальную работу системы вспомогательной батареи. Если индикатор продолжает гореть, заряд вспомогательной батареи низкий или в системе вспомогательной батареи есть неисправность — свяжитесь с центром обслуживания клиентов Li Auto.
Индикатор неисправности внешнего освещения | Если индикатор горит, во внешнем освещении есть неисправность — свяжитесь с центром обслуживания клиентов Li Auto.
Индикатор ограничения мощности системы привода | Если индикатор горит, мощность всего автомобиля ограничена.
Индикатор износа тормозных колодок | Если индикатор горит, тормозные колодки автомобиля изношены до предельного положения — своевременно обратитесь в сервисный центр Li Auto для замены тормозных колодок.
Предупреждающий сигнал неисправности электронной регулировки подвески | Если предупреждающий сигнал горит, в системе управления высотой подвески есть неисправность — высота подвески не может регулироваться — свяжитесь с центром обслуживания клиентов Li Auto.
Сценарий использования
1214""")

# ── CHUNK 44 ── li_auto_l7_zh_42cee406  Glove box + storage compartments
add("li_auto_l7_zh_42cee406",
"www.carobook.com",
"""

Warning
● Do not forcefully pull on the open glove box to avoid damaging the glove box or injuring yourself.
● The glove box must be closed while driving to prevent items in the glove box from flying out and injuring occupants during emergency braking or an accident.
II. Glove Box Light
When the glove box is opened, the glove box light automatically illuminates; when closed, it automatically turns off.
Note
While the glove box light is on, the light will turn off after a 3-minute timer in the following situations:
● The vehicle power is switched from on to off and the vehicle is in an unarmed state.
● When the vehicle power is off and the vehicle is in an unarmed state, the vehicle transitions from sleep to wake mode.
Storage Compartments
I. Armrest Box
Press the armrest box switch to open the armrest box, which can hold items approximately the size of a wallet or tissue box.
User Manual
2777


II. Driver Underseat Storage Compartment
Press the storage compartment switch and open the compartment outward to hold items approximately the size of a driver's license or vehicle registration.
User Manual
2778


III. Center Console Upper Storage Tray
Can hold items approximately the size of a business card.
IV. Second-Row Storage Compartment
Can hold items approximately the size of a tissue box.
User Manual
2779


Warning
Do not place glasses, lighters, or aerosol cans in storage compartments to avoid item damage from vibration.
User Manual
2781


Cup Holders
I. Front-Row Cup Holders
II. Second-Row Cup Holders
The second-row cup holders are located inside the rear center armrest; open the rear center armrest to use them.
User Manual
2782""",
"www.carobook.com",
"""

Предупреждение
● Не тяните с силой открытый бардачок во избежание его повреждения или травмы.
● Бардачок должен быть закрыт во время движения, чтобы предметы в нём не вылетели и не причинили травму пассажирам при экстренном торможении или аварии.
II. Освещение бардачка
При открытии бардачка освещение автоматически включается; при закрытии — автоматически выключается.
Примечание
Пока освещение бардачка включено, оно выключится по истечении таймера 3 минуты в следующих ситуациях:
● Питание автомобиля переключается из включённого в выключенное состояние, и автомобиль находится в незащищённом состоянии.
● Когда питание автомобиля выключено и автомобиль находится в незащищённом состоянии, автомобиль переходит из спящего в активное состояние.
Отсеки для хранения
I. Ящик подлокотника
Нажмите переключатель ящика подлокотника для его открытия; в нём можно хранить предметы приблизительно размером с кошелёк или упаковку салфеток.
Руководство пользователя
2777


II. Нижний отсек под сиденьем водителя
Нажмите переключатель отсека и откройте его наружу; в нём можно хранить предметы приблизительно размером с водительское удостоверение или свидетельство о регистрации.
Руководство пользователя
2778


III. Верхний лоток центральной консоли
Может вместить предметы приблизительно размером с визитку.
IV. Отсек для хранения второго ряда
Может вместить предметы приблизительно размером с упаковку салфеток.
Руководство пользователя
2779


Предупреждение
Не кладите очки, зажигалки или аэрозольные баллончики в отсеки для хранения во избежание повреждения предметов от вибрации.
Руководство пользователя
2781


Подстаканники
I. Подстаканники переднего ряда
II. Подстаканники второго ряда
Подстаканники второго ряда расположены внутри заднего центрального подлокотника; откройте задний центральный подлокотник для использования.
Руководство пользователя
2782""")

# ── CHUNK 45 ── li_auto_l7_zh_430e198c  Mirror auto-tilt + driver assistance screen
add("li_auto_l7_zh_430e198c",
"www.carobook.com",
"""

When the switch is set to "Right Side", the right exterior rearview mirror will automatically tilt to the stored position when the gear is shifted to Reverse (R), for convenient reversing.
When the switch is set to "Both Sides", both left and right exterior rearview mirrors will automatically tilt to their stored positions when the gear is shifted to Reverse (R), for convenient reversing.
Warning
● Do not adjust the exterior rearview mirrors while driving to avoid loss of vehicle control causing injury or vehicle damage.
● Do not drive the vehicle with exterior rearview mirrors not adjusted to the proper position.
● Do not touch the exterior rearview mirrors while they are in motion to avoid injury from pinching.
Note
After manual folding, the mirrors will remain folded until vehicle speed reaches 40 km/h.
Note
If the mirror adjustment button is operated during the auto-tilt process, the auto-tilt action will stop, and the position at the end of the adjustment will be automatically saved as the tilt position.
Driver Assistance Interaction Screen
I. Home Screen
No. | Name | No. | Name
Energy Mode | Gear
Range Display Mode | READY indicator
Turn Signal | Remaining fuel range
Vehicle Speed | Battery percentage / remaining electric range
Drive power consumption / combined fuel consumption / time
Driving Scenario
1191""",
"www.carobook.com",
"""

При установке переключателя в «Правое», при переключении на заднюю передачу (R) правое наружное зеркало заднего вида автоматически наклонится до сохранённого положения для удобства движения задним ходом.
При установке переключателя в «Оба», при переключении на заднюю передачу (R) левое и правое наружные зеркала заднего вида автоматически наклонятся до сохранённых положений для удобства движения задним ходом.
Предупреждение
● Не регулируйте наружные зеркала заднего вида во время движения во избежание потери контроля над автомобилем с причинением травм или повреждением автомобиля.
● Не управляйте автомобилем с наружными зеркалами заднего вида, не отрегулированными до надлежащего положения.
● Не прикасайтесь к наружным зеркалам заднего вида в процессе их движения во избежание травмирования.
Примечание
После ручного складывания зеркала остаются в сложенном состоянии до достижения скорости 40 км/ч.
Примечание
Если кнопка регулировки зеркала нажата во время автоматического наклонения, оно прекратится, и конечное положение будет автоматически сохранено как положение наклона.
Экран взаимодействия безопасного вождения
I. Главный экран
№ | Наименование | № | Наименование
Режим энергии | Передача
Режим отображения запаса хода | Индикатор READY
Поворотник | Остаток пробега на топливе
Скорость | Процент заряда / остаток электрического пробега
Энергопотребление привода / комплексный расход топлива / время
Сценарий использования
1191""")

# ── CHUNK 46 ── li_auto_l7_zh_432068a1  Rear AC controls (full screen version)
add("li_auto_l7_zh_432068a1",
"www.carobook.com",
"""

Note
When the rear AC is turned on and the front AC is off, the front AC will also turn on simultaneously.
2. Auto Off
This function is disabled by default. Tap the "Auto Off" icon in the AC system control interface to enable the rear AC auto-off function. When enabled, if the system detects no one in the rear seats, the rear AC will automatically turn off after 10 minutes.
3. Temperature Setting
Tap the up/down arrow of the "Temperature" icon in the AC system control interface to set the rear temperature. Each tap increases or decreases the temperature by 0.5°C; long-press the up/down arrow to quickly adjust temperature.
The set temperature is adjustable within 16°C~28°C. When the set temperature is 16°C, the display shows "Low"; when 28°C, the display shows "High".
4. Fan Speed Setting
Tap the up/down arrow of the "Fan Speed" icon in the AC system control interface to adjust the fan speed level; each tap changes the level by one step. Long-press the up/down arrow to quickly adjust the fan speed level.
In manual mode, the rear AC has 9 fan speed levels; in auto mode, there are 5 automatic levels with the fan speed automatically adjusted within the selected level range.
5. Air Flow Mode Setting
Tap any one or more icons in the "Air Flow Mode" icon in the AC system control interface to combine air flow modes. There are three modes: face, feet, and face+feet.
6. AC Lock
This function is disabled by default. Tap the "AC Lock" icon in the AC system control interface to enable the AC lock function. When enabled, the rear AC control panel cannot be used.
7. Auto Mode
User Manual
705""",
"www.carobook.com",
"""

Примечание
При включении заднего кондиционера, если передний кондиционер выключен, передний кондиционер также включится одновременно.
2. Автоматическое выключение
Эта функция отключена по умолчанию. Нажмите иконку «Авт. выключение» в интерфейсе управления системой кондиционирования для включения функции автоматического выключения заднего кондиционера. При включении, если система не обнаруживает никого на задних сиденьях, задний кондиционер автоматически выключится через 10 минут.
3. Настройка температуры
Нажмите стрелку вверх/вниз иконки «Температура» в интерфейсе управления системой кондиционирования для установки температуры заднего ряда. Каждое нажатие повышает или понижает температуру на 0,5°C; длинное нажатие стрелки вверх/вниз позволяет быстро регулировать температуру.
Установленная температура регулируется в диапазоне 16°C~28°C. При температуре 16°C отображается «Низкая»; при 28°C — «Высокая».
4. Настройка скорости вентилятора
Нажмите стрелку вверх/вниз иконки «Скорость вентилятора» в интерфейсе управления для регулировки уровня скорости; каждое нажатие изменяет уровень на один шаг. Длинное нажатие позволяет быстро регулировать уровень.
В ручном режиме задний кондиционер имеет 9 уровней скорости вентилятора; в автоматическом режиме — 5 автоматических уровней с автоматической регулировкой скорости в выбранном диапазоне.
5. Настройка режима подачи воздуха
Нажмите одну или несколько иконок в «Режиме подачи воздуха» для комбинирования режимов. Доступны три режима: на лицо, на ноги, на лицо+ноги.
6. Блокировка кондиционера
Эта функция отключена по умолчанию. Нажмите иконку «Блокировка кондиционера» для включения функции блокировки. При включении панель управления задним кондиционером недоступна.
7. Автоматический режим
Руководство пользователя
705""")

# ── CHUNK 47 ── li_auto_l7_zh_43579d05  Rear wiper maintenance mode
add("li_auto_l7_zh_43579d05",
"www.carobook.com",
"""

II. Rear Wiper Maintenance Mode
When maintenance or replacement of the rear windshield wiper is required, activate the rear wiper maintenance mode. When the rear wiper maintenance mode is activated, the rear windshield wiper will automatically move to the center position of the windshield.
To enter rear wiper maintenance mode: In the center console screen settings, tap "Vehicle", select "Maintenance", tap the "Rear" option under "Wiper Maintenance" to enable or disable rear wiper maintenance mode.
Note
Before enabling rear wiper maintenance mode, shift to Park (P) gear and ensure the rear windshield wiper is in the off state.
Note
● Before turning on the windshield wipers, thoroughly defrost and clear snow from the windshield.
● Do not use the wipers when the windshield is dry or when the washer fluid is empty.
● Before washing the vehicle, ensure the windshield wipers are in the off position.
● Do not replace or perform maintenance on the wipers without activating wiper maintenance mode.
Driving Scenario
2297""",
"www.carobook.com",
"""

II. Режим технического обслуживания заднего стеклоочистителя
При необходимости технического обслуживания или замены заднего стеклоочистителя активируйте режим технического обслуживания. При активации задний стеклоочиститель автоматически переместится в центральное положение на ветровом стекле.
Для входа в режим технического обслуживания заднего стеклоочистителя: в настройках центрального экрана нажмите «Автомобиль», выберите «Обслуживание», нажмите параметр «Задний» в разделе «Обслуживание стеклоочистителей» для включения или отключения режима.
Примечание
Перед включением режима технического обслуживания заднего стеклоочистителя переключитесь в режим парковки (P) и убедитесь, что задний стеклоочиститель выключен.
Примечание
● Перед включением стеклоочистителей тщательно разморозьте и очистите лобовое стекло от снега.
● Не используйте стеклоочистители, когда лобовое стекло сухое или омывающая жидкость закончилась.
● Перед мойкой автомобиля убедитесь, что стеклоочистители в выключенном положении.
● Не заменяйте и не обслуживайте стеклоочистители без активации режима технического обслуживания.
Сценарий использования
2297""")

# ── CHUNK 48 ── li_auto_l7_zh_43ba404a  Straight-line summon limitations
add("li_auto_l7_zh_43ba404a",
"www.carobook.com",
"""

● Detection of a driver or passenger inside the vehicle.
● Manual takeover actions such as shifting gears, pressing the accelerator pedal, pressing the brake pedal, or turning the steering wheel.
Warning
● Straight-Line Summon is a driving assistance function. Do not use this function to replace the driver's observation and judgment of traffic conditions; before using this function, ensure the environment around the vehicle is safe.
● Ensure the vehicle is within your line of sight when using Straight-Line Summon.
● When Straight-Line Summon is activated, the steering wheel and wheels will automatically center — ensure the steering wheel can turn normally.
● After summon is complete, when unlocking the vehicle via the Li Auto App remote control, Bluetooth key, smart key, or exterior door handle, the exterior rearview mirrors will automatically unfold — before unlocking, ensure the surrounding environment is safe to avoid the mirrors scraping adjacent obstacles or vehicles.
IV. Functional Limitations
The smart parking system cannot fully replace the driver in assessing environmental information and cannot guarantee successful parking every time. The smart parking and Straight-Line Summon functions have the following limitations.
When the parking system operates under conditions where mechanical systems or external environment conditions are not met, parking space results may be affected or parking may fail, including but not limited to:
● The steering wheel has a heavy steering wheel cover installed that prevents precise steering control at the expected angle during the parking process.
● Non-original-size tires are used.
● Tire pressure is insufficient or uneven.
● Snow anti-skid chains are installed.
● The function can only be used on dry, flat, level, smooth, paved road surfaces without inclines, undulations, or uneven surfaces.
When the system is operating, due to ultrasonic radar characteristics, the following situations may cause reduced obstacle recognition or non-recognition, leading to vehicle damage or personal injury, including but not limited to:
● Very low objects, objects under the bumper, objects too close to or too far from the vehicle.
● Suspended objects that cannot be detected.
● Surrounding ultrasonic noise at the same frequency, such as metallic sounds, exhaust sounds, etc.
● Obstacles that are wire mesh, fences, poles, ropes, shopping carts, or other thin objects that cannot reflect effective sound waves.
● Obstacles that are snow, cotton, or surfaces that easily absorb sound waves.
Special Feature
1542""",
"www.carobook.com",
"""

● Обнаружение водителя или пассажира внутри автомобиля.
● Ручные действия по перехвату управления: переключение передачи, нажатие педали акселератора, нажатие педали тормоза или поворот рулевого колеса.
Предупреждение
● Прямолинейный вызов является функцией помощи при вождении. Не используйте эту функцию вместо наблюдения и суждения водителя о дорожной обстановке; перед использованием убедитесь, что окружающая среда безопасна.
● При использовании прямолинейного вызова убедитесь, что автомобиль находится в вашем поле зрения.
● При активации прямолинейного вызова руль и колёса автоматически выровняются — убедитесь, что руль может нормально поворачиваться.
● После завершения вызова при разблокировке автомобиля через дистанционное управление приложением Li Auto, Bluetooth-ключ, умный ключ или наружную ручку двери наружные зеркала заднего вида автоматически раскроются — перед разблокировкой убедитесь в безопасности окружающей среды во избежание царапания зеркалами соседних препятствий или транспортных средств.
IV. Ограничения функции
Система интеллектуальной парковки не может полностью заменить водителя в оценке информации об окружающей среде и не может гарантировать успешную парковку каждый раз. Функции интеллектуальной парковки и прямолинейного вызова имеют следующие ограничения.
Когда система парковки работает в условиях, когда требования к механическим системам или внешней среде не выполнены, это может влиять на результаты парковки или привести к невозможности въехать в место, включая, но не ограничиваясь:
● На рулевое колесо надет тяжёлый чехол, препятствующий точному управлению поворотом на ожидаемый угол в процессе парковки.
● Используются шины нестандартного размера.
● Давление в шинах недостаточное или неравномерное.
● Установлены снегозащитные цепи.
● Функция может использоваться только на сухих, ровных, горизонтальных, гладких асфальтированных поверхностях без уклонов, неровностей или выбоин.
Когда система работает, из-за характеристик ультразвукового радара следующие ситуации могут привести к снижению качества распознавания препятствий или их нераспознаванию, вызывая повреждение автомобиля или травму, включая, но не ограничиваясь:
● Очень низкие предметы, предметы под бампером, предметы слишком близко или далеко от автомобиля.
● Подвесные объекты, которые невозможно обнаружить.
● Окружающие ультразвуковые шумы на той же частоте, такие как металлические звуки, звуки выхлопа и т.д.
● Препятствия из сетки, заборов, столбов, верёвок, тележек или других тонких объектов, не способных отражать эффективные звуковые волны.
● Препятствия из снега, хлопка или поверхностей, легко поглощающих звуковые волны.
Особые функции
1542""")

# ── CHUNK 49 ── li_auto_l7_zh_43dab64d  External low-speed sound + special road modes
add("li_auto_l7_zh_43dab64d",
"www.carobook.com",
"""

Note
The exterior low-speed warning sound system pause switch should only be used in short-distance situations where there are no other road users and the surrounding environment clearly does not require a warning sound.
Special Road Conditions
Tap "Special Road Conditions" in the center console bottom function bar to select from three special road condition modes: "Hill Descent Control, Slippery Road, Off-Road Recovery".
● Hill Descent Control: The Hill Descent Control system applies a certain braking force to the wheels when descending a slope to maintain stable vehicle speed.
● Slippery Road: Enable Slippery Road mode when driving on easily slippery surfaces. In Slippery Road mode, the vehicle adjusts front and rear axle power output to prevent wheel slippage, facilitating smooth passage through icy/snowy or muddy road surfaces.
● Off-Road Recovery: Enable Off-Road Recovery mode during off-road driving. When Off-Road Recovery mode is activated, the system applies electronic traction control to the wheels to generate maximum traction force while automatically adjusting suspension height to improve vehicle mobility, helping the vehicle to escape difficult terrain.
Driving Scenario
189""",
"www.carobook.com",
"""

Примечание
Переключатель паузы системы внешнего предупреждающего звука при низкой скорости следует использовать только на короткие расстояния, когда нет других участников дорожного движения и окружающая среда явно не требует предупреждающего звука.
Особые дорожные условия
Нажмите «Особые дорожные условия» в нижней функциональной панели центрального экрана для выбора одного из трёх режимов особых дорожных условий: «Помощь при спуске, Скользкая дорога, Выход из бездорожья».
● Помощь при спуске: Система помощи при спуске применяет определённое тормозное усилие к колёсам при движении под уклон для поддержания стабильной скорости.
● Скользкая дорога: Включите режим скользкой дороги при движении по легко скользким поверхностям. В режиме скользкой дороги автомобиль регулирует мощность передней и задней осей, чтобы колёса не пробуксовывали, облегчая движение по обледеневшим, заснеженным или грязным дорогам.
● Выход из бездорожья: Включите режим выхода из бездорожья при движении по бездорожью. При активации режима система применяет электронную тягу к колёсам для создания максимальной тяговой силы, одновременно автоматически регулируя высоту подвески для улучшения проходимости, помогая автомобилю преодолеть сложные условия рельефа.
Сценарий использования
189""")

# Save final output
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"Final: {len(results)} entries (all 50 chunks translated)")

# Verify: should be exactly 100 entries (50 chunks x 2 languages)
assert len(results) == 100, f"Expected 100, got {len(results)}"

# Verify all chunk IDs are present
import json as _json
with open('C:/Diagnostica-KB-Package/knowledge-base/translate_batches/batch_005.json', 'r', encoding='utf-8') as f:
    source = _json.load(f)
source_ids = set(c['id'] for c in source)
result_ids = set(r['id'] for r in results)
missing = source_ids - result_ids
if missing:
    print(f"WARNING: Missing IDs: {missing}")
else:
    print("All 50 source IDs present in output.")

langs_per_id = {}
for r in results:
    langs_per_id.setdefault(r['id'], set()).add(r['lang'])
all_have_both = all(langs == {'en', 'ru'} for langs in langs_per_id.values())
print(f"All chunks have EN+RU: {all_have_both}")
print("DONE. Output: C:/Diagnostica-KB-Package/knowledge-base/translate_batches/batch_005_out.json")
