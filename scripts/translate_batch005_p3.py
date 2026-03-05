#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Translate batch_005.json chunks 24-37"""
import json

out_path = 'C:/Diagnostica-KB-Package/knowledge-base/translate_batches/batch_005_out.json'
with open(out_path, 'r', encoding='utf-8') as f:
    results = json.load(f)

def add(chunk_id, en_title, en_content, ru_title, ru_content):
    results.append({"id": chunk_id, "lang": "en", "title": en_title, "content": en_content})
    results.append({"id": chunk_id, "lang": "ru", "title": ru_title, "content": ru_content})

# ── CHUNK 24 ── li_auto_l7_zh_3f3ca248  Reading lights auto control
add("li_auto_l7_zh_3f3ca248",
"www.carobook.com",
"""

1. Interior Reading Light Auto On
Tap the "Auto" icon to switch the interior reading lights to auto mode.
When auto mode is enabled, the interior reading lights will illuminate automatically in the following situations:
● When any door (excluding the trunk door) is opened and the lighting condition is met.
● When the vehicle is unlocked and the lighting condition is met.
Note
After the reading lights are triggered by opening a door, if the door is not closed, the reading lights will remain on. When triggered by vehicle unlock, the reading lights will illuminate for a period then automatically turn off.
After the interior reading lights automatically illuminate, they will automatically turn off in the following situations:
● The gear is shifted to non-Park (P).
● The vehicle is locked.
● After all doors have been closed for a period of time.
2. Interior Reading Lights All On
Tap the "All On" icon to illuminate all interior reading lights.
3. Interior Reading Lights All Off
Tap the "All Off" icon to turn off all interior reading lights.
II. Manual Control
You can manually turn on a reading light by touching it to provide extended illumination, making it convenient for placing items or reading documents.
Touch once to turn on, touch again to turn off.
User Manual
2770


Note
● The second-row reading light manual operation method is the same as the front-row reading light operation method.
● When the vehicle is involved in a collision, all interior reading lights illuminate.
Vanity Light
Open the sun visor mirror cover to illuminate the vanity light.
Close the sun visor mirror cover to turn off the vanity light.
User Manual
2771""",
"www.carobook.com",
"""

1. Автоматическое включение внутренних ламп для чтения
Нажмите иконку «Авто», чтобы переключить внутренние лампы для чтения в автоматический режим.
В автоматическом режиме внутренние лампы для чтения включаются автоматически в следующих ситуациях:
● При открытии любой двери (кроме двери багажника) при выполнении условий освещённости.
● При разблокировке автомобиля при выполнении условий освещённости.
Примечание
После включения ламп для чтения при открытии двери, если дверь не закрыта, лампы для чтения будут оставаться включёнными. При включении при разблокировке автомобиля лампы включатся на некоторое время, а затем автоматически выключатся.
После автоматического включения внутренних ламп для чтения они автоматически выключатся в следующих ситуациях:
● Переключение передачи в положение, отличное от парковки (P).
● Блокировка автомобиля.
● Через некоторое время после закрытия всех дверей.
2. Все внутренние лампы для чтения включены
Нажмите иконку «Все вкл.», чтобы включить все внутренние лампы для чтения.
3. Все внутренние лампы для чтения выключены
Нажмите иконку «Все выкл.», чтобы выключить все внутренние лампы для чтения.
II. Ручное управление
Вы можете вручную включить лампу для чтения, прикоснувшись к ней, чтобы обеспечить длительное освещение для удобства размещения предметов или чтения документов.
Прикосновение один раз — включить, повторное прикосновение — выключить.
Руководство пользователя
2770


Примечание
● Способ ручного управления лампой для чтения второго ряда аналогичен способу управления лампой переднего ряда.
● При столкновении автомобиля все внутренние лампы для чтения включаются.
Лампа для макияжа
Откройте крышку зеркала козырька для включения лампы для макияжа.
Закройте крышку зеркала козырька для выключения лампы для макияжа.
Руководство пользователя
2771""")

# ── CHUNK 25 ── li_auto_l7_zh_3f551ffe  Seatbelts and pre-drive checks
add("li_auto_l7_zh_3f551ffe",
"www.carobook.com",
"""

II. Using Seat Belts
Before driving, ensure all occupants have properly fastened their seat belts.
When children are in the vehicle, use an appropriate child safety seat based on the child's age and body size, unless their body size is suitable for the vehicle seat belt.
III. Adjusting Rearview Mirrors
Correctly adjusting the interior and exterior rearview mirrors reduces blind spots and improves driving safety.
IV. Prohibited Items
To ensure vehicle and occupant safety, do not store flammable or explosive items such as lighters, perfume, hair spray, or alcohol inside the vehicle. Flammable or explosive items left in the vehicle may cause fire, especially in summer or other high-temperature environments.
Do not install suction cups or other decorations on the windshield or windows. Do not place objects on the dashboard; suction cups or other items with a lens effect may cause fire.
Do not place objects on the dashboard; objects on the dashboard not only obstruct the driver's view but also affect starting and safe driving.
User Manual
541""",
"www.carobook.com",
"""

II. Использование ремней безопасности
Перед началом движения убедитесь, что все пассажиры правильно пристёгнуты ремнями безопасности.
При наличии детей в автомобиле используйте подходящее детское кресло в соответствии с возрастом и телосложением ребёнка, если только его телосложение не позволяет использовать штатный ремень безопасности.
III. Регулировка зеркал заднего вида
Правильная регулировка внутреннего и наружных зеркал заднего вида уменьшает слепые зоны и повышает безопасность вождения.
IV. Запрещённые предметы
Для обеспечения безопасности автомобиля и пассажиров не храните в автомобиле легковоспламеняющиеся или взрывоопасные предметы, такие как зажигалки, духи, лак для волос или алкоголь. Легковоспламеняющиеся предметы в автомобиле могут вызвать пожар, особенно летом или в других условиях высоких температур.
Не устанавливайте присоски или другие украшения на ветровое стекло или окна. Не кладите предметы на приборную панель; присоски или другие предметы с эффектом линзы могут вызвать пожар.
Не кладите предметы на приборную панель; предметы на приборной панели не только загораживают обзор водителя, но и влияют на начало движения и безопасное вождение.
Руководство пользователя
541""")

# ── CHUNK 26 ── li_auto_l7_zh_3f7cf9e9  Rear AC (driving scenario version)
add("li_auto_l7_zh_3f7cf9e9",
"www.carobook.com",
"""

Short press up/down on the temperature adjustment button to set the rear temperature; each short press increases or decreases the temperature by 0.5°C. Long press up/down to quickly adjust the temperature.
The set temperature is adjustable within 16°C~28°C. When the set temperature is 16°C, the display shows "LO"; when 28°C, the display shows "HI".
2. Air Flow Mode Setting
Press up/down on the air flow mode switch button to cycle through three air flow modes: face, face+feet, and feet.
3. Air Conditioning System On/Off
Press the rear air conditioning on/off button to activate the rear AC. Press again to turn it off.
When the rear AC is off, the following operations can also turn it on:
● Short press or long press up/down on the temperature adjustment button.
● Press up/down on the auto mode button.
● Short press or long press up/down on the fan speed adjustment button.
● Press up/down on the air flow mode switch button.
Note
When the rear AC is turned on and the front AC is off, the front AC will also turn on simultaneously.
4. Auto Mode
Press up/down on the auto mode button to put the rear AC into auto mode. When enabled, the system automatically adjusts the outlet temperature, air flow mode, and fan speed.
After entering auto mode, the following operations will exit auto mode:
● Press up/down on the auto mode button.
● Press up/down on the air flow mode switch button.
5. Fan Speed Setting
Driving Scenario
1396""",
"www.carobook.com",
"""

Кратко нажмите вверх/вниз кнопку регулировки температуры для установки температуры заднего ряда; каждое короткое нажатие повышает или понижает температуру на 0,5°C. Длинное нажатие вверх/вниз позволяет быстро регулировать температуру.
Установленная температура регулируется в диапазоне 16°C~28°C. При температуре 16°C отображается «LO»; при 28°C — «HI».
2. Настройка режима подачи воздуха
Нажмите вверх/вниз кнопку переключения режима подачи воздуха для переключения между тремя режимами: на лицо, на лицо+ноги и на ноги.
3. Включение/выключение системы кондиционирования
Нажмите кнопку включения/выключения заднего кондиционера для активации. Нажмите ещё раз для выключения.
Когда задний кондиционер выключен, следующие действия также могут его включить:
● Краткое или длинное нажатие вверх/вниз кнопки регулировки температуры.
● Нажатие вверх/вниз кнопки автоматического режима.
● Краткое или длинное нажатие вверх/вниз кнопки регулировки скорости вентилятора.
● Нажатие вверх/вниз кнопки переключения режима подачи воздуха.
Примечание
При включении заднего кондиционера, если передний кондиционер выключен, передний кондиционер также включится одновременно.
4. Автоматический режим
Нажмите вверх/вниз кнопку автоматического режима для перевода заднего кондиционера в автоматический режим. При включении система автоматически регулирует температуру воздуха, режим подачи воздуха и скорость вентилятора.
После входа в автоматический режим следующие действия выведут из него:
● Нажатие вверх/вниз кнопки автоматического режима.
● Нажатие вверх/вниз кнопки переключения режима подачи воздуха.
5. Настройка скорости вентилятора
Сценарий использования
1396""")

# ── CHUNK 27 ── li_auto_l7_zh_3fa0ab12  Keys / anti-theft
add("li_auto_l7_zh_3fa0ab12",
"Keys",
"""Keys

II. Triggering the Alarm
When the anti-theft system is armed, any of the following will trigger the alarm:
● Using the mechanical key to unlock a door.
● Opening a door, trunk door, or front hood without carrying the smart key.
Note
When the vehicle is locked from inside, opening a door will not trigger the alarm.
III. Deactivating the Anti-Theft System
Any of the following will deactivate the anti-theft system:
● Unlocking the vehicle with the smart key.
● Opening the trunk door with the smart key.
● Turning on the vehicle power.
Warning
● Do not leave the smart key in the vehicle when leaving.
● Do not privately modify or dismantle the anti-theft system to avoid system malfunction.
Note
● Before locking the vehicle, ensure no one is inside and windows are closed.
● The anti-theft system helps prevent vehicle theft but cannot completely prevent it. To further secure the vehicle, park in a safe location and remove valuables and personal belongings before leaving.
Keys
This vehicle is equipped with the following keys:
Driving Scenario
2140""",
"Ключи",
"""Ключи

II. Срабатывание сигнализации
При активированной противоугонной системе любое из следующего вызовет срабатывание сигнализации:
● Использование механического ключа для разблокировки двери.
● Открытие двери, двери багажника или капота без наличия умного ключа.
Примечание
При блокировке автомобиля изнутри открытие двери не вызовет срабатывание сигнализации.
III. Деактивация противоугонной системы
Любое из следующего деактивирует противоугонную систему:
● Разблокировка автомобиля с умным ключом.
● Открытие двери багажника с умным ключом.
● Включение питания автомобиля.
Предупреждение
● Не оставляйте умный ключ в автомобиле при выходе.
● Не модифицируйте и не демонтируйте противоугонную систему самостоятельно во избежание неисправности системы.
Примечание
● Перед блокировкой автомобиля убедитесь, что внутри никого нет, а окна закрыты.
● Противоугонная система помогает предотвратить угон, но не может полностью исключить его. Для дополнительной защиты автомобиля паркуйтесь в безопасном месте и забирайте ценности и личные вещи перед выходом.
Ключи
Автомобиль оснащён следующими ключами:
Сценарий использования
2140""")

# ── CHUNK 28 ── li_auto_l7_zh_3fc647a4  Exterior rearview mirrors
add("li_auto_l7_zh_3fc647a4",
"Exterior Rearview Mirrors",
"""Exterior Rearview Mirrors

## Exterior Rearview Mirrors

The exterior rearview mirrors allow observation of the area behind the vehicle. Proper adjustment reduces blind spots and improves driving safety.
• Left exterior rearview mirror select button
Left exterior rearview mirror select button
• Right exterior rearview mirror select button
Right exterior rearview mirror select button
• Exterior rearview mirror fold button
Exterior rearview mirror fold button
• Exterior rearview mirror adjustment button
Exterior rearview mirror adjustment button

## Adjusting the Mirror Surface

For safety, adjust the exterior rearview mirrors while stationary using the following method:
• Press the mirror select button to select the mirror to be adjusted. The button indicator illuminates to indicate the selected state.
• Press the up, down, left, or right buttons on the mirror adjustment button to adjust the angle of the selected mirror.
• After adjustment, press the mirror select button again; the button indicator turns off, exiting the selected state.
Do not adjust the rearview mirrors while driving, as improper control may cause an accident resulting in serious injury or death.

## Manual Folding and Unfolding Exterior Rearview Mirrors

Press the exterior rearview mirror fold button to electrically fold both exterior rearview mirrors. Press the fold button again to electrically unfold both mirrors.

## Automatic Folding and Unfolding Exterior Rearview Mirrors

Go to Center Console > [Settings] > [Vehicle] > [Mirrors] > [Auto-fold Exterior Mirrors on Lock] to enable or disable the auto-fold function.
When enabled, the exterior mirrors automatically fold when the vehicle is locked.
When auto-fold on lock is enabled, the auto-unfold setting becomes available; you can set the mirrors to unfold automatically [on unlock] or [on door open].
If the exterior mirrors were manually folded, they will not automatically unfold when the vehicle is unlocked.

## Auto Anti-Glare

When the vehicle gear is in any position other than Reverse (R), the driver-side exterior rearview mirror automatically adjusts its reflective effect based on the intensity of headlights from vehicles behind, dimming and softening the headlight glare.

## Exterior Rearview Mirror Auto-Tilt

• Enabling and Disabling Auto-Tilt
Go to Center Console > [Settings] > [Vehicle] > [Mirrors] > [Auto-tilt Exterior Mirrors on Reverse] to configure the auto-tilt function: [Off], [Right Side], or [Both Sides].
• Storing the Tilt Position
When set to [Right Side], shift to Reverse (R) and manually adjust the right exterior mirror; when done, the system automatically saves that position as the right mirror tilt position.
When set to [Both Sides], shift to Reverse (R) and manually adjust left/right exterior mirrors; when done, the system automatically saves those positions as the left/right mirror tilt positions.
When set to [Right Side] and adjusting the left exterior mirror, that position will not be saved as the left mirror tilt position.
• Auto-Tilt Activation
When set to [Right Side], the right exterior mirror automatically tilts to the stored position when Reverse (R) is engaged, for convenient reversing.
When set to [Both Sides], both left and right exterior mirrors automatically tilt to stored positions when Reverse (R) is engaged.
• Do not adjust the exterior rearview mirrors while driving to avoid loss of vehicle control causing injury or vehicle damage.
Do not adjust the exterior rearview mirrors while driving to avoid loss of vehicle control causing injury or vehicle damage.
• Do not drive the vehicle with exterior rearview mirrors not adjusted to the proper position.
Do not drive the vehicle with exterior rearview mirrors not adjusted to the proper position.
• Do not touch the exterior rearview mirrors while they are in motion to avoid injury from pinching.
Do not touch the exterior rearview mirrors while they are in motion to avoid injury from pinching.
After manual folding, the mirrors will remain folded until vehicle speed reaches 40 km/h.
If the mirror adjustment button is operated during the auto-tilt process, the auto-tilt action will stop, and the position at the end of the adjustment will be automatically saved as the tilt position.

## Front Passenger Exit Guard

Go to Center Console > [Settings] > [Vehicle] > [Mirrors] > [Front Passenger Exit Guard] to enable or disable the function.
When enabled and the vehicle speed is below approximately 10 km/h, when the front passenger unbuckles their seatbelt while seated, the front passenger entertainment screen automatically displays the right rear camera view.""",
"Наружные зеркала заднего вида",
"""Наружные зеркала заднего вида

## Наружные зеркала заднего вида

Наружные зеркала заднего вида позволяют наблюдать за областью позади автомобиля. Правильная регулировка уменьшает слепые зоны и повышает безопасность вождения.
• Кнопка выбора левого наружного зеркала заднего вида
Кнопка выбора левого наружного зеркала заднего вида
• Кнопка выбора правого наружного зеркала заднего вида
Кнопка выбора правого наружного зеркала заднего вида
• Кнопка складывания наружных зеркал заднего вида
Кнопка складывания наружных зеркал заднего вида
• Кнопка регулировки наружных зеркал заднего вида
Кнопка регулировки наружных зеркал заднего вида

## Регулировка поверхности зеркала

В целях безопасности регулируйте наружные зеркала заднего вида в неподвижном состоянии следующим способом:
• Нажмите кнопку выбора зеркала, чтобы выбрать зеркало для регулировки. Индикатор кнопки загорается, указывая на выбранное состояние.
• Нажмите кнопки вверх, вниз, влево или вправо на кнопке регулировки зеркала для настройки угла выбранного зеркала.
• После регулировки снова нажмите кнопку выбора зеркала; индикатор кнопки погаснет, выходя из выбранного состояния.
Не регулируйте зеркала заднего вида во время движения, так как неправильное управление может привести к аварии с серьёзными травмами или смертью.

## Ручное складывание и разворачивание наружных зеркал заднего вида

Нажмите кнопку складывания наружных зеркал для электрического складывания обоих зеркал. Нажмите кнопку складывания ещё раз для электрического разворачивания обоих зеркал.

## Автоматическое складывание и разворачивание наружных зеркал заднего вида

Перейдите в Центральный экран > [Настройки] > [Автомобиль] > [Зеркала] > [Автоскладывание зеркал при блокировке] для включения или отключения функции автоскладывания.
При включении функции наружные зеркала автоматически складываются при блокировке автомобиля.
При включении автоскладывания при блокировке становится доступна настройка автоматического разворачивания: можно установить разворачивание зеркал [при разблокировке] или [при открытии двери].
Если наружные зеркала были сложены вручную, они не будут автоматически разворачиваться при разблокировке автомобиля.

## Автоматическая защита от ослепления

Когда автомобиль находится в любом положении, кроме задней передачи (R), наружное зеркало заднего вида со стороны водителя автоматически регулирует отражающий эффект в зависимости от интенсивности фар задних автомобилей, делая свет фар более тусклым и мягким.

## Автоматическое наклонение наружных зеркал заднего вида

• Включение и отключение автоматического наклонения
Перейдите в Центральный экран > [Настройки] > [Автомобиль] > [Зеркала] > [Автонаклон зеркал при задней передаче] для настройки функции: [Выкл.], [Правое] или [Оба].
• Сохранение положения наклона
При установке [Правое], переключитесь на заднюю передачу (R) и вручную отрегулируйте правое наружное зеркало; после завершения система автоматически сохранит это положение как положение наклона правого зеркала.
При установке [Оба], переключитесь на заднюю передачу (R) и вручную отрегулируйте левое/правое наружное зеркало; после завершения система автоматически сохранит эти положения.
При установке [Правое] и регулировке левого наружного зеркала это положение не сохранится как положение наклона левого зеркала.
• Активация автоматического наклонения
При установке [Правое], при переключении на заднюю передачу (R) правое наружное зеркало автоматически наклоняется до сохранённого положения для удобства движения задним ходом.
При установке [Оба], при переключении на заднюю передачу оба зеркала автоматически наклоняются до сохранённых положений.
• Не регулируйте наружные зеркала заднего вида во время движения во избежание потери контроля над автомобилем с причинением травм или повреждением автомобиля.
Не регулируйте наружные зеркала заднего вида во время движения во избежание потери контроля над автомобилем с причинением травм или повреждением автомобиля.
• Не управляйте автомобилем с наружными зеркалами заднего вида, не отрегулированными до надлежащего положения.
Не управляйте автомобилем с наружными зеркалами заднего вида, не отрегулированными до надлежащего положения.
• Не прикасайтесь к наружным зеркалам заднего вида в процессе их движения во избежание травмирования.
Не прикасайтесь к наружным зеркалам заднего вида в процессе их движения во избежание травмирования.
После ручного складывания зеркала остаются в сложенном состоянии до достижения скорости 40 км/ч.
Если кнопка регулировки зеркала нажата во время процесса автоматического наклонения, действие автоматического наклонения прекратится, и положение после окончания регулировки будет автоматически сохранено как положение наклона.

## Функция защиты при выходе переднего пассажира

Перейдите в Центральный экран > [Настройки] > [Автомобиль] > [Зеркала] > [Защита при выходе переднего пассажира] для включения или отключения функции.
При включении и скорости автомобиля ниже примерно 10 км/ч, когда передний пассажир отстёгивает ремень безопасности находясь на месте, экран развлечений переднего пассажира автоматически отображает вид камеры правого заднего ряда.""")

# ── CHUNK 29 ── li_auto_l7_zh_400fd7d1  Seat heating/ventilation controls
add("li_auto_l7_zh_400fd7d1",
"www.carobook.com",
"""

Off: While the seat is in heating or ventilation mode, tap the "Seat Heating" or "Seat Ventilation" icon until it turns off, or long-press the icon to turn it off.
The seat heating function has three levels: High, Medium, and Low. High is the highest temperature, Low is the lowest.
The seat ventilation function has three levels: High, Medium, and Low. High is the strongest airflow, Low is the weakest.
3. Second-Row Seat Heating/Ventilation Control (via rear AC control panel)
● Seat Heating
Seat heating has three levels: High, Medium, and Low. Short press up on the left/right "Seat Heating/Ventilation" button on the AC control panel to cycle through levels to off; long press up on the left/right "Seat Heating/Ventilation" button to turn off seat heating.
Note
When the seat ventilation/heating button on the rear AC control panel is used to enable left or right seat heating, the center seat heating will also be enabled simultaneously.
● Seat Ventilation
Seat ventilation has three levels: High, Medium, and Low. Press down on the left/right "Seat Heating/Ventilation" button on the AC control panel to cycle through levels to off; long press down on the left/right "Seat Heating/Ventilation" button to turn off seat ventilation.
Driving Scenario
2421""",
"www.carobook.com",
"""

Выкл.: При работе сиденья в режиме обогрева или вентиляции нажмите иконку «Обогрев сиденья» или «Вентиляция сиденья» до выключения или удержите иконку для выключения.
Функция обогрева сиденья имеет три уровня: Высокий, Средний, Низкий. Высокий — наибольшая температура, Низкий — наименьшая.
Функция вентиляции сиденья имеет три уровня: Высокий, Средний, Низкий. Высокий — наибольшая скорость воздушного потока, Низкий — наименьшая.
3. Управление обогревом/вентиляцией сидений второго ряда (через панель управления задним кондиционером)
● Обогрев сиденья
Обогрев сиденья имеет три уровня: Высокий, Средний, Низкий. Короткое нажатие вверх на левую/правую кнопку «Обогрев/вентиляция сиденья» на панели управления кондиционером переключает уровни до выключения; длинное нажатие вверх на левую/правую кнопку выключает обогрев сиденья.
Примечание
При использовании кнопки вентиляции/обогрева сиденья на панели управления задним кондиционером для включения левого или правого обогрева сиденья одновременно включится обогрев центрального сиденья.
● Вентиляция сиденья
Вентиляция сиденья имеет три уровня: Высокий, Средний, Низкий. Нажатие вниз на левую/правую кнопку «Обогрев/вентиляция сиденья» на панели управления переключает уровни до выключения; длинное нажатие вниз выключает вентиляцию сиденья.
Сценарий использования
2421""")

# ── CHUNK 30 ── li_auto_l7_zh_4047a9a5  Warning lights table (EPB, TPMS, etc.)
add("li_auto_l7_zh_4047a9a5",
"www.carobook.com",
"""

Icon | Name
Electronic Parking System fault warning light | When the vehicle starts, this warning light illuminates for a few seconds then goes out, indicating the electronic parking system is normal. If the warning light remains lit, there is an electronic parking system fault — drive carefully and immediately contact the Li Auto Customer Service Center or go to a Li Auto Service Center to avoid vehicle damage or an accident.
i-Booster warning light | There is a fault with the i-Booster (electromechanical booster) or ESP system — drive carefully and immediately contact the Li Auto Customer Service Center or go to a Li Auto Service Center to avoid vehicle damage or an accident.
Abnormal tire pressure/temperature, TPMS fault warning light | When the vehicle starts, this warning light illuminates for a few seconds then goes out, indicating the TPMS is normal. If the warning light remains lit, tire pressure is low, tire pressure is high, tire temperature is high, or there is a TPMS fault — check the tire condition and if necessary contact the Li Auto Customer Service Center or go to a Li Auto Service Center. If the warning light flashes, the TPMS control module is not powered — contact the Li Auto Customer Service Center or go to a Li Auto Service Center.
Drive system fault warning light | When the vehicle starts, this warning light illuminates for a few seconds then goes out, indicating the drive system is normal. If the fault light remains lit, there is a drive system fault — park the vehicle in a safe location and contact the Li Auto Customer Service Center. Continuing to drive may be dangerous!
User Manual
1640""",
"www.carobook.com",
"""

Иконка | Название
Предупреждающий сигнал неисправности электронной системы стояночного тормоза | При запуске автомобиля этот предупреждающий сигнал горит несколько секунд, затем гаснет, что означает нормальную работу электронной системы стояночного тормоза. Если предупреждающий сигнал продолжает гореть, в электронной системе стояночного тормоза есть неисправность — ездите осторожно и немедленно свяжитесь с центром обслуживания клиентов Li Auto или обратитесь в сервисный центр Li Auto.
Предупреждающий сигнал i-Booster | В системе i-Booster (электромеханическом усилителе) или системе ESP есть неисправность — ездите осторожно и немедленно свяжитесь с центром обслуживания клиентов Li Auto или обратитесь в сервисный центр.
Предупреждающий сигнал аномального давления/температуры шин, неисправности TPMS | При запуске автомобиля этот предупреждающий сигнал горит несколько секунд, затем гаснет, что означает нормальную работу TPMS. Если предупреждающий сигнал продолжает гореть, давление в шинах низкое, высокое, температура шин высокая или есть неисправность TPMS — проверьте состояние шин и при необходимости свяжитесь с центром обслуживания клиентов Li Auto или обратитесь в сервисный центр. Если предупреждающий сигнал мигает, блок управления TPMS не получает питание — свяжитесь с центром обслуживания клиентов Li Auto или обратитесь в сервисный центр.
Предупреждающий сигнал неисправности системы привода | При запуске автомобиля этот предупреждающий сигнал горит несколько секунд, затем гаснет, что означает нормальную работу системы привода. Если индикатор неисправности продолжает гореть, в системе привода есть неисправность — припаркуйте автомобиль в безопасном месте и свяжитесь с центром обслуживания клиентов Li Auto. Продолжение движения может быть опасным!
Руководство пользователя
1640""")

# ── CHUNK 31 ── li_auto_l7_zh_405218b4  HBA and CDP
add("li_auto_l7_zh_405218b4",
"HBA Hydraulic Brake Assist",
"""HBA Hydraulic Brake Assist

HBA Hydraulic Brake Assist
When the driver rapidly presses the brake pedal, HBA can recognize that the vehicle is in an emergency state and quickly increases brake pressure to the maximum value, allowing ABS to intervene more quickly and effectively shortening the braking distance.
Warning
HBA can improve driving safety but cannot eliminate hazards caused by following too closely, vehicle skidding, speeding, or taking corners too fast — drive with caution.
CDP Dynamic Park Brake
When driving and a sudden emergency occurs (e.g., brake failure), long-press the Park (P) button to activate the Dynamic Park Brake (CDP) function. The vehicle will decelerate at a certain deceleration range until it stops. If the P button is released before the vehicle stops, this function will immediately exit.
R
N
A
D
P
R
N
A
D
P
Warning
● Do not operate this function in non-emergency situations to avoid causing traffic accidents or casualties while driving.
Driving Scenario
1251""",
"HBA Гидравлическая тормозная поддержка",
"""HBA Гидравлическая тормозная поддержка

HBA Гидравлическая тормозная поддержка
При быстром нажатии водителем педали тормоза HBA распознаёт аварийное состояние автомобиля и быстро увеличивает тормозное давление до максимального значения, позволяя ABS вмешаться быстрее и эффективно сокращая тормозной путь.
Предупреждение
HBA повышает безопасность вождения, но не может устранить опасности, вызванные слишком близкой дистанцией, скольжением автомобиля, превышением скорости или слишком быстрым прохождением поворотов — ездите осторожно.
CDP Динамический стояночный тормоз
При возникновении внезапной экстренной ситуации во время движения (например, отказ тормозов) удержите кнопку парковки (P) для активации функции динамического стояночного тормоза (CDP). Автомобиль будет замедляться с определённым замедлением до полной остановки. Если кнопка P отпущена до остановки автомобиля, функция немедленно выйдет.
R
N
A
D
P
R
N
A
D
P
Предупреждение
● Не используйте эту функцию в неаварийных ситуациях во избежание дорожно-транспортных происшествий или жертв во время движения.
Сценарий использования
1251""")

# ── CHUNK 32 ── li_auto_l7_zh_405b0469  Parking sensor limitations (camera)
add("li_auto_l7_zh_405b0469",
"www.carobook.com",
"""

● Ditches, ditch covers, or manhole covers inside or beside the parking space.
● Very low objects, objects under the bumper, objects too close to or too far from the vehicle.
● Suspended objects that cannot be detected.
● Surrounding ultrasonic noise at the same frequency, such as metallic sounds, exhaust sounds, etc.
● Obstacles that are wire mesh, fences, poles, ropes, shopping carts, or other thin objects that cannot reflect effective sound waves.
● Obstacles that are snow, cotton, or surfaces that easily absorb sound waves.
● The system will not always detect pedestrians, children, or animals near the vehicle.
● Obstacles that are cone-shaped or have angled surfaces.
● Obstacles that are right-angle objects such as wall corners or vehicle rear ends.
● On grass or rough, uneven road surfaces.
● When a temperature inversion occurs near the radar.
● Ultrasonic radar is damaged, misaligned, or obstructed by foreign objects.
Cameras also have certain limitations; the following situations may affect the normal operation of the exit system, including but not limited to:
● Left/right exterior rearview mirrors or front/rear cameras are damaged, causing cameras to malfunction or become misaligned.
● Cameras are dirty or obstructed.
● Ambient brightness is too high, e.g., cameras are hit by direct sunlight.
Driving Scenario
2459""",
"www.carobook.com",
"""

● Канавы, крышки канав или люки внутри или рядом с парковочным местом.
● Очень низкие предметы, предметы под бампером, предметы слишком близко или далеко от автомобиля.
● Подвесные объекты, которые невозможно обнаружить.
● Окружающие ультразвуковые шумы на той же частоте, такие как металлические звуки, звуки выхлопа и т.д.
● Препятствия из сетки, заборов, столбов, верёвок, тележек или других тонких объектов, не способных отражать эффективные звуковые волны.
● Препятствия из снега, хлопка или поверхностей, легко поглощающих звуковые волны.
● Система не всегда обнаруживает пешеходов, детей или животных вблизи автомобиля.
● Препятствия конической формы или с наклонными поверхностями.
● Препятствия с прямыми углами, такие как углы стен или задние части автомобилей.
● На траве или неровных дорожных покрытиях.
● При возникновении температурной инверсии вблизи радара.
● Ультразвуковой радар повреждён, смещён или заблокирован посторонними предметами.
Камеры также имеют определённые ограничения; следующие ситуации могут влиять на нормальную работу системы выезда, включая, но не ограничиваясь:
● Левое/правое наружное зеркало заднего вида или камеры спереди/сзади повреждены, что приводит к неисправности или смещению камер.
● Камеры загрязнены или заблокированы.
● Яркость окружающей среды слишком высока, например, камеры под прямыми солнечными лучами.
Сценарий использования
2459""")

# ── CHUNK 33 ── li_auto_l7_zh_4095fa12  Indicator lights table (HDC, auto hold, etc.)
add("li_auto_l7_zh_4095fa12",
"www.carobook.com",
"""

Icon | Name
Hill Descent Control indicator | When the vehicle starts, this indicator illuminates for a few seconds then goes out, indicating the system is normal. If the indicator remains lit, the Hill Descent Control function is enabled. If the indicator flashes, the Hill Descent Control function is active.
Auto Hold indicator | If the indicator is lit, it indicates that the Auto Hold function is active.
Charging gun connection status indicator | When the vehicle is connected to a charging gun or discharge gun, the indicator illuminates.
READY indicator | When the vehicle starts, the READY indicator illuminates.
Charging status indicator | If the indicator is lit, the vehicle is being charged with a charging gun.
Charging complete indicator | If the indicator is lit, vehicle charging is complete.
Low fuel indicator | If the indicator is lit, the remaining fuel in the tank is insufficient — refuel promptly.
Low traction battery indicator | If the indicator is lit, the traction battery is low — charge the vehicle promptly.
Washer fluid level indicator | If the indicator is lit, the washer fluid level is abnormal — check the washer fluid level promptly.
Driving Scenario
1210""",
"www.carobook.com",
"""

Иконка | Название
Индикатор системы помощи при спуске | При запуске автомобиля этот индикатор горит несколько секунд, затем гаснет, что означает нормальную работу системы. Если индикатор продолжает гореть, функция помощи при спуске включена. Если индикатор мигает, функция помощи при спуске активна.
Индикатор автоматического удержания | Если индикатор горит, функция автоматического удержания активна.
Индикатор состояния подключения зарядного пистолета | При подключении зарядного или разрядного пистолета к автомобилю индикатор включается.
Индикатор READY | При запуске автомобиля индикатор READY включается.
Индикатор состояния зарядки | Если индикатор горит, автомобиль заряжается с помощью зарядного пистолета.
Индикатор завершения зарядки | Если индикатор горит, зарядка автомобиля завершена.
Индикатор низкого уровня топлива | Если индикатор горит, остаток топлива в баке недостаточен — своевременно заправьтесь.
Индикатор низкого заряда тяговой батареи | Если индикатор горит, заряд тяговой батареи низкий — своевременно зарядите автомобиль.
Индикатор уровня омывающей жидкости | Если индикатор горит, уровень омывающей жидкости аномален — своевременно проверьте уровень омывающей жидкости.
Сценарий использования
1210""")

# ── CHUNK 34 ── li_auto_l7_zh_410e9f4f  Front/rear defrost and defroster
add("li_auto_l7_zh_410e9f4f",
"www.carobook.com",
"""

● Tap the "Interior Defogging" icon.
Note
When the front AC is off, tapping the "Auto" icon will also turn on the front AC system.
IX. Front Windshield Defrost and Defogging Mode
In the AC system control interface, tap the "Interior Defogging" icon to enable front windshield defrosting and defogging to reduce moisture, fog, or frost on the front windshield and front window glass surfaces, improving forward and side-forward visibility. Tap "Interior Defogging", "Auto", or "Air Flow Mode" icon to disable this function.
Note
In special circumstances (e.g., cold and humid environments), the heating elements in the front camera area will automatically operate to defog and ensure normal camera operation.
X. Rear Windshield Defrost and Defogging Mode
In the AC system control interface, tap the "Rear Window Heating" icon to enable rear windshield defrosting and defogging to reduce moisture, fog, and frost on the rear windshield surface, improving rearward visibility. Tap again to disable.
XI. Exterior Rearview Mirror Heating Mode
In the AC system control interface, tap the "Mirror Heating" icon to enable exterior rearview mirror heating to reduce moisture, fog, and frost on the mirror surfaces, improving rearward visibility. Tap again to disable.
Setting Temperature and Fan Speed in the Center Console Bottom Function Bar
Tap/long-press the left/right arrow of the driver-side or passenger-side "Temperature" icon in the center console bottom function bar to pop up the temperature control interface. After 5 seconds of inactivity or tapping another area, the temperature control interface will collapse.
Driving Scenario
342""",
"www.carobook.com",
"""

● Нажмите иконку «Запотевание салона».
Примечание
Когда передний кондиционер выключен, нажатие иконки «Авто» также включит систему переднего кондиционера.
IX. Режим разморозки и обдува переднего ветрового стекла
В интерфейсе управления системой кондиционирования нажмите иконку «Запотевание салона» для включения разморозки и обдува переднего ветрового стекла с целью снижения влажности, тумана или инея на поверхности переднего ветрового и боковых стёкол, улучшая обзор вперёд и вбок. Нажмите иконку «Запотевание салона», «Авто» или «Режим подачи воздуха» для отключения этой функции.
Примечание
В особых обстоятельствах (например, в холодной и влажной среде) нагревательные элементы в зоне передней камеры будут автоматически работать для обдува и обеспечения нормальной работы камеры.
X. Режим разморозки и обдува заднего ветрового стекла
В интерфейсе управления системой кондиционирования нажмите иконку «Обогрев заднего стекла» для включения разморозки и обдува заднего ветрового стекла с целью снижения влажности, тумана и инея на поверхности заднего ветрового стекла, улучшая задний обзор. Нажмите ещё раз для отключения.
XI. Режим обогрева наружных зеркал заднего вида
В интерфейсе управления системой кондиционирования нажмите иконку «Обогрев зеркал» для включения обогрева наружных зеркал заднего вида с целью снижения влажности, тумана и инея на поверхностях зеркал, улучшая задний обзор. Нажмите ещё раз для отключения.
Настройка температуры и скорости вентилятора в нижней функциональной панели центрального экрана
Нажмите/удержите левую/правую стрелку иконки «Температура» со стороны водителя или пассажира в нижней функциональной панели центрального экрана для вызова интерфейса управления температурой. После 5 секунд бездействия или нажатия другой области интерфейс управления температурой свернётся.
Сценарий использования
342""")

# ── CHUNK 35 ── li_auto_l7_zh_412265a0  RCW Rear Collision Warning
add("li_auto_l7_zh_412265a0",
"Rear Collision Warning (RCW)",
"""Rear Collision Warning (RCW)

## Rear Collision Warning (RCW)

When driving forward, the system issues a warning and flashes the hazard warning lights when it detects the possibility of being rear-ended by a following vehicle, alerting the driver to seek evasive space at the appropriate time and warning the following vehicle to slow down and maintain a safe following distance.
• Rear Collision Warning is a driving assistance function; its warning timing is affected by many factors such as the ego vehicle speed, following vehicle speed, following vehicle overlap ratio with the ego vehicle, following vehicle type, and system reaction delay. It may fail to issue a timely warning, miss warnings, or issue false warnings. This function must never replace the driver's observation and judgment of traffic conditions, nor the driver's responsibility for safe vehicle operation. Keep both hands on the steering wheel and maintain vehicle control at all times.
Rear Collision Warning is a driving assistance function; its warning timing is affected by many factors such as the ego vehicle speed, following vehicle speed, following vehicle overlap ratio with the ego vehicle, following vehicle type, and system reaction delay. It may fail to issue a timely warning, miss warnings, or issue false warnings. This function must never replace the driver's observation and judgment of traffic conditions, nor the driver's responsibility for safe vehicle operation. Keep both hands on the steering wheel and maintain vehicle control at all times.
• Rear Collision Warning is only activated when the ego vehicle speed is between 0 km/h and 135 km/h and the following vehicle is faster than the ego vehicle by a certain margin.
Rear Collision Warning is only activated when the ego vehicle speed is between 0 km/h and 135 km/h and the following vehicle is faster than the ego vehicle by a certain margin.

## Settings

This function's control switch is shared with the Automatic Emergency Braking (AEB) function. Go to Center Console > [Settings] > [AD Max] > [Active Safety] > [Automatic Emergency Braking (AEB)] to configure or temporarily disable the function.
• The AEB function switch simultaneously controls AEB, Forward Collision Warning (FCW), Forward Blind Zone Collision Prevention (F-CTA/F-CTB), Rear Collision Warning (RCW), Rear Blind Zone Collision Prevention (R-CTA/R-CTB), and other functions.
• Disabling the AEB switch only takes effect for the current trip. Each time the vehicle starts, the Rear Collision Warning function will automatically be enabled by default.
• Setting to reminder or braking enables the Rear Collision Warning function.

## Alert Information

When the system identifies that a following vehicle may rear-end the ego vehicle, the center console screen displays rear collision risk information, rearview mirror indicator lights and hazard warning lights flash, accompanied by an audible alert.

## Functional Limitations

In the following situations, Rear Collision Warning may be limited or unable to operate normally, including but not limited to:
• When vehicle speed exceeds 120 km/h.
When vehicle speed exceeds 120 km/h.
• When the rear risk vehicle is not in the same lane as the ego vehicle.
When the rear risk vehicle is not in the same lane as the ego vehicle.
• When the overlap ratio of the approaching rear vehicle with this vehicle is low.
When the overlap ratio of the approaching rear vehicle with this vehicle is low.
• A motorcycle approaching from the rear with a rear-end risk.
A motorcycle approaching from the rear with a rear-end risk.
• When the reverse light, turn signal, hazard warning light, or emergency brake signal light is active.
When the reverse light, turn signal, hazard warning light, or emergency brake signal light is active.
• When the system identifies that two warning cycles are too close together or the previous warning has not been completed.
When the system identifies that two warning cycles are too close together or the previous warning has not been completed.
• Targets only detectable after this vehicle changes lanes.
Targets only detectable after this vehicle changes lanes.
• Targets in curves.
Targets in curves.
• Camera imaging capability is affected, including but not limited to: poor visibility due to nighttime; poor visibility due to adverse weather (heavy rain, heavy snow, heavy fog, sandstorms); strong light, backlighting, water reflections, extreme light contrast; camera obstructed by mud, ice, snow; degraded camera performance due to extreme heat or cold.
Camera imaging capability is affected, including but not limited to:
• Poor visibility due to nighttime conditions.
Poor visibility due to nighttime conditions.
• Poor visibility due to adverse weather (heavy rain, heavy snow, heavy fog, sandstorms).
Poor visibility due to adverse weather (heavy rain, heavy snow, heavy fog, sandstorms).
• Strong light, backlighting, water reflections, extreme light contrast.
Strong light, backlighting, water reflections, extreme light contrast.
• Camera obstructed by mud, ice, snow, etc.
Camera obstructed by mud, ice, snow, etc.
• Degraded camera performance due to extreme heat or cold.
Degraded camera performance due to extreme heat or cold.
• Rear Collision Warning is a driving assistance function and must never replace the driver's observation and judgment of traffic conditions, nor the driver's responsibility for safe vehicle operation. Keep both hands on the steering wheel and maintain vehicle control at all times.
• Drivers must not become overly reliant on Rear Collision Warning, must not intentionally test or wait for function triggering. Due to external environment, equipment performance, and other factors, the system may not accurately identify all hazardous scenarios — drivers must maintain vehicle control at all times.
• When Rear Collision Warning is triggered, the driver must immediately take corrective action based on the current road situation to prevent the vehicle from falling into further danger.
• Rear Collision Warning is only active when the ego vehicle is stationary or moving forward. When reversing, the ego vehicle will not warn of rear collision risks directly behind.""",
"Предупреждение о столкновении сзади (RCW)",
"""Предупреждение о столкновении сзади (RCW)

## Предупреждение о столкновении сзади (RCW)

При движении вперёд система выдаёт предупреждение и мигает аварийными огнями при обнаружении возможности наезда сзади следующего транспортного средства, предупреждая водителя о необходимости найти пространство для манёвра в подходящее время и предупреждая следующее транспортное средство о необходимости снизить скорость и соблюдать безопасную дистанцию.
• Предупреждение о столкновении сзади является функцией помощи при вождении; время предупреждения зависит от многих факторов, таких как скорость собственного автомобиля, скорость следующего транспортного средства, степень перекрытия следующего транспортного средства с собственным, тип следующего транспортного средства и задержка реакции системы. Возможна несвоевременная, пропущенная или ложная выдача предупреждений. Эта функция никогда не должна заменять наблюдение и суждение водителя о дорожной обстановке. Держите руль обеими руками и сохраняйте контроль над автомобилем в любое время.
Предупреждение о столкновении сзади является функцией помощи при вождении; время предупреждения зависит от многих факторов, таких как скорость собственного автомобиля, скорость следующего транспортного средства, степень перекрытия следующего транспортного средства с собственным, тип следующего транспортного средства и задержка реакции системы. Возможна несвоевременная, пропущенная или ложная выдача предупреждений. Эта функция никогда не должна заменять наблюдение и суждение водителя о дорожной обстановке. Держите руль обеими руками и сохраняйте контроль над автомобилем в любое время.
• Предупреждение о столкновении сзади активируется только при скорости собственного автомобиля от 0 км/ч до 135 км/ч и при скорости следующего транспортного средства, превышающей скорость собственного на определённое значение.
Предупреждение о столкновении сзади активируется только при скорости собственного автомобиля от 0 км/ч до 135 км/ч и при скорости следующего транспортного средства, превышающей скорость собственного на определённое значение.

## Настройки

Управляющий переключатель этой функции совпадает с функцией автоматического экстренного торможения (AEB). Перейдите в Центральный экран > [Настройки] > [AD Max] > [Активная безопасность] > [Автоматическое экстренное торможение (AEB)] для настройки или временного отключения функции.
• Переключатель функции AEB одновременно управляет AEB, предупреждением о лобовом столкновении (FCW), предотвращением столкновения в лобовой слепой зоне (F-CTA/F-CTB), предупреждением о столкновении сзади (RCW), предотвращением столкновения в задней слепой зоне (R-CTA/R-CTB) и другими функциями.
• Отключение переключателя AEB действует только для текущей поездки. При каждом запуске автомобиля функция предупреждения о столкновении сзади будет автоматически включаться по умолчанию.
• При установке напоминания или торможения функция предупреждения о столкновении сзади включается.

## Информация об оповещении

Когда система определяет, что следующее транспортное средство может врезаться в данный автомобиль, центральный экран отображает информацию о риске столкновения сзади, мигают индикаторы зеркал заднего вида и аварийные огни, сопровождаемые звуковым предупреждением.

## Ограничения функции

В следующих ситуациях функция предупреждения о столкновении сзади может быть ограничена или не работать нормально, включая, но не ограничиваясь:
• Когда скорость автомобиля превышает 120 км/ч.
Когда скорость автомобиля превышает 120 км/ч.
• Когда транспортное средство с риском сзади не находится в той же полосе, что и данный автомобиль.
Когда транспортное средство с риском сзади не находится в той же полосе, что и данный автомобиль.
• Когда степень перекрытия приближающегося сзади транспортного средства с данным автомобилем мала.
Когда степень перекрытия приближающегося сзади транспортного средства с данным автомобилем мала.
• Мотоцикл приближается сзади с риском наезда.
Мотоцикл приближается сзади с риском наезда.
• Когда включён фонарь заднего хода, поворотник, аварийная сигнализация или сигнал экстренного торможения.
Когда включён фонарь заднего хода, поворотник, аварийная сигнализация или сигнал экстренного торможения.
• Когда система определяет, что два цикла предупреждения слишком близко друг к другу или предыдущее предупреждение не завершено.
Когда система определяет, что два цикла предупреждения слишком близко друг к другу или предыдущее предупреждение не завершено.
• Объекты, обнаруживаемые только после смены полосы данным автомобилем.
Объекты, обнаруживаемые только после смены полосы данным автомобилем.
• Объекты на изогнутых дорогах.
Объекты на изогнутых дорогах.
• Нарушение работы камеры, включая, но не ограничиваясь: плохая видимость из-за ночного времени; плохая видимость из-за неблагоприятных погодных условий (сильный дождь, снег, туман, песчаные бури); яркий свет, контровой свет, отражения от воды, экстремальный световой контраст; камера заблокирована грязью, льдом, снегом; снижение производительности камеры из-за экстремального тепла или холода.
Нарушение работы камеры, включая, но не ограничиваясь:
• Плохая видимость из-за ночного времени.
Плохая видимость из-за ночного времени.
• Плохая видимость из-за неблагоприятных погодных условий (сильный дождь, снег, туман, песчаные бури).
Плохая видимость из-за неблагоприятных погодных условий (сильный дождь, снег, туман, песчаные бури).
• Яркий свет, контровой свет, отражения от воды, экстремальный световой контраст.
Яркий свет, контровой свет, отражения от воды, экстремальный световой контраст.
• Камера заблокирована грязью, льдом, снегом и т.д.
Камера заблокирована грязью, льдом, снегом и т.д.
• Снижение производительности камеры из-за экстремального тепла или холода.
Снижение производительности камеры из-за экстремального тепла или холода.
• Предупреждение о столкновении сзади является функцией помощи при вождении и никогда не должно заменять наблюдение и суждение водителя о дорожной обстановке. Держите руль обеими руками и сохраняйте контроль над автомобилем в любое время.
• Водители не должны чрезмерно полагаться на предупреждение о столкновении сзади, намеренно проверять или ожидать его срабатывания. Из-за внешней среды, производительности оборудования и других факторов система может не точно идентифицировать все опасные ситуации — водители должны поддерживать контроль над автомобилем в любое время.
• При срабатывании предупреждения водитель должен немедленно принять корректирующие меры в соответствии с текущей дорожной ситуацией во избежание дальнейшей опасности.
• Предупреждение о столкновении сзади активно только когда данный автомобиль неподвижен или движется вперёд. При движении задним ходом предупреждения о рисках столкновения непосредственно сзади не выдаются.""")

# ── CHUNK 36 ── li_auto_l7_zh_4126ac6b  App remote control + straight-line summon
add("li_auto_l7_zh_4126ac6b",
"www.carobook.com",
"""

● Lock/Unlock: When all four doors are locked, tap the "Lock" button for one-tap unlock; when any door is unlocked, tap the "Lock" button for one-tap full lock.
● Windows: Tap the "Window" button to open all windows; when any window is open, tap the "Window" button to close all windows.
● Trunk Control: Tap the "Trunk" button to control trunk opening or closing (remote angle adjustment is not currently supported).
● Find Vehicle: Tap the "Find Vehicle" button — the turn signals will flash 10 times and the horn will sound 2 times.
● Authorized Driving: Use this function to grant another person a one-time vehicle start authorization. Tap the "Authorize" button — the vehicle enters the unlocked state; within 2 minutes, pressing the brake pedal puts the vehicle into a startable state until this driving cycle ends. Reauthorization is required for subsequent drives.
Note
● When far from the vehicle, ensure the vehicle has cellular network connectivity; within 10 meters of the vehicle, the vehicle can be connected and controlled via Bluetooth.
● When using the trunk control function, ensure the vehicle is parked with sufficient clearance behind to avoid the trunk door hitting obstacles.
● Remote control is not allowed when the vehicle is running.
Straight-Line Summon
Straight-Line Summon is a supplementary function to the Smart Parking function. When the vehicle is in a tight parking space making it difficult for the driver to enter or exit, the Li Auto App can be used to activate Straight-Line Summon to control the vehicle to move straight forward and backward, making parking or retrieving the vehicle more convenient.
I. Entering Summon
Open the "Li Auto" interface in the Li Auto App, tap the "Straight-Line Summon" button to summon the vehicle.
Special Feature
1537""",
"www.carobook.com",
"""

● Блокировка/разблокировка: Когда все четыре двери заблокированы, нажмите кнопку «Замок» для разблокировки одним нажатием; когда любая дверь разблокирована, нажмите кнопку «Замок» для полной блокировки одним нажатием.
● Окна: Нажмите кнопку «Окна» для открытия всех окон; когда любое окно открыто, нажмите кнопку «Окна» для закрытия всех окон.
● Управление багажником: Нажмите кнопку «Багажник» для управления открытием или закрытием багажника (дистанционное управление углом открытия в настоящее время не поддерживается).
● Поиск автомобиля: Нажмите кнопку «Поиск автомобиля» — поворотники мигнут 10 раз и клаксон прозвучит 2 раза.
● Авторизованное вождение: Используйте эту функцию для предоставления другому лицу разового права запуска автомобиля. Нажмите кнопку «Авторизация» — автомобиль перейдёт в разблокированное состояние; в течение 2 минут нажатие педали тормоза переведёт автомобиль в состояние готовности к запуску до завершения текущего цикла вождения. Для следующей поездки потребуется повторная авторизация.
Примечание
● При нахождении вдали от автомобиля убедитесь в наличии сотовой сети; в радиусе 10 метров от автомобиля можно подключиться и управлять через Bluetooth.
● При использовании функции управления багажником убедитесь, что автомобиль припаркован с достаточным зазором сзади во избежание удара двери багажника о препятствия.
● Дистанционное управление недоступно при работающем автомобиле.
Прямолинейный вызов
Прямолинейный вызов является дополнительной функцией к функции интеллектуальной парковки. Когда автомобиль находится на тесном парковочном месте, затрудняя посадку или высадку водителя, приложение Li Auto можно использовать для активации прямолинейного вызова с целью управления прямолинейным движением автомобиля вперёд и назад, что делает парковку или выезд более удобными.
I. Вход в режим вызова
Откройте интерфейс «Li Auto» в приложении Li Auto, нажмите кнопку «Прямолинейный вызов» для вызова автомобиля.
Особые функции
1537""")

# ── CHUNK 37 ── li_auto_l7_zh_4139fbbb  Adjacent vehicle avoidance + AEB warning
add("li_auto_l7_zh_4139fbbb",
"Adjacent Vehicle Avoidance",
"""Adjacent Vehicle Avoidance

Warning
● Automatic Emergency Braking is a driving assistance function that provides physical deceleration when relevant collision risks are detected, but cannot completely prevent the vehicle from stopping or a collision. This function must never replace the driver's observation and judgment of traffic conditions, nor the driver's responsibility for safe vehicle operation.
● The driver has the highest priority for vehicle control. AEB may not operate when the driver performs active evasive actions such as rapidly turning the steering wheel or fully pressing the brake pedal, to avoid interfering with driver operations.
● Drivers must not become overly reliant on AEB, must not intentionally test or wait for function triggering. Due to inherent system limitations, false triggers and missed triggers cannot be completely avoided.
● Due to complex real-time traffic, road, and weather conditions, radar and cameras cannot ensure correct detection under all conditions. If radar or cameras fail to detect a forward obstacle, AEB will not be triggered.
● When AEB is triggered, the brake pedal will move downward quickly — ensure there are no obstacles below the brake pedal, such as floor mats.
Adjacent Vehicle Avoidance
When Lane Keeping Assist is active and vehicle speed is between 60 km/h and 130 km/h, if the system detects a vehicle in an adjacent lane that is to be overtaken and that vehicle is drifting toward or straddling this lane, this vehicle will laterally shift toward the opposite side within its own lane for safe avoidance. After overtaking the avoidance vehicle, it will return to the center of the lane and continue driving.
I. Settings
In the center console screen settings, tap "Smart Driving", select "Safety Preferences", tap the options under "Adjacent Vehicle Avoidance" to enable or disable the function.
Driving Scenario
2356


II. Function Trigger
When Lane Keeping Assist is active and vehicle speed is above 60 km/h, if a vehicle encroaching from one adjacent lane is detected, this vehicle will laterally avoid toward the other side; the corresponding encroaching vehicle will appear red on the center console screen.
Driving Scenario
2357""",
"Уклонение от приближающегося соседнего транспортного средства",
"""Уклонение от приближающегося соседнего транспортного средства

Предупреждение
● Автоматическое экстренное торможение является функцией помощи при вождении, обеспечивающей физическое замедление при обнаружении соответствующих рисков столкновения, но не может полностью предотвратить остановку автомобиля или столкновение. Эта функция никогда не должна заменять наблюдение и суждение водителя о дорожной обстановке.
● Водитель имеет наивысший приоритет управления автомобилем. AEB может не работать при выполнении водителем активных уклоняющих действий, таких как быстрый поворот руля или полное нажатие педали тормоза, чтобы не мешать действиям водителя.
● Водители не должны чрезмерно полагаться на AEB, намеренно проверять или ожидать его срабатывания. Из-за неотъемлемых ограничений системы ложные и пропущенные срабатывания не могут быть полностью исключены.
● Из-за сложных условий реального дорожного движения, дороги и погоды радар и камеры не могут гарантировать правильное обнаружение во всех условиях. Если радар или камеры не обнаруживают препятствие впереди, AEB не будет срабатывать.
● При срабатывании AEB педаль тормоза быстро опускается вниз — убедитесь, что под педалью тормоза нет препятствий, таких как коврики.
Уклонение от приближающегося соседнего транспортного средства
Когда помощь при удержании в полосе активна и скорость автомобиля составляет от 60 км/ч до 130 км/ч, если система обнаруживает транспортное средство в соседней полосе, которое нужно обогнать, и это транспортное средство смещается в сторону данной полосы или прижимается к ней, данный автомобиль боком сместится к противоположной стороне в своей полосе для безопасного уклонения. После обгона автомобиля, от которого уклонялись, данный автомобиль вернётся в центр полосы и продолжит движение.
I. Настройки
В настройках центрального экрана нажмите «Интеллектуальное вождение», выберите «Настройки безопасности», нажмите параметры в разделе «Уклонение от соседнего транспортного средства» для включения или отключения функции.
Сценарий использования
2356


II. Активация функции
Когда помощь при удержании в полосе активна и скорость автомобиля превышает 60 км/ч, при обнаружении транспортного средства, прижимающегося из одной соседней полосы, данный автомобиль боком уклоняется к другой стороне; соответствующее транспортное средство выделится красным на центральном экране.
Сценарий использования
2357""")

with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"Saved {len(results)} entries (chunks 0-37 translated)")
