#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Translate batch_005.json: ZH -> EN + RU"""
import json

results = []

def add(chunk_id, en_title, en_content, ru_title, ru_content):
    results.append({"id": chunk_id, "lang": "en", "title": en_title, "content": en_content})
    results.append({"id": chunk_id, "lang": "ru", "title": ru_title, "content": ru_content})

# ── CHUNK 0 ── li_auto_l7_zh_39678bcb  交互方式
add("li_auto_l7_zh_39678bcb",
"Interaction Methods",
"""Interaction Methods

Interaction Methods
I. Free Conversation
1. Continuous Dialogue
After wake-up, multiple conversations can be held within a period of time without repeated wake-up.
Special Feature
1485

2. Say It Anytime
Interrupt at any time, say what you want — no need to wait for Li Xiang Classmate to finish speaking.
Special Feature
1486

3. See It, Say It
Supports directly saying the button text displayed on the screen — say what you see.
See It, Say It supports QQ Music, NetEase Cloud Music, iQIYI, National K Song, and many other apps with more continuously being added.
4. Semantic Rejection
Li Xiang Classmate effectively recognizes conversations directed at it and will not interrupt conversations between passengers, avoiding misoperations and protecting user privacy.
Special Feature
1487

5. Say It All at Once
You can say the wake word and command together without waiting for Li Xiang Classmate to respond.
Special Feature
1488

II. Spatial Interaction
Li Xiang Classmate wants to serve every member in the vehicle, going wherever needed.
When woken from the front passenger seat, it appears on the front passenger screen; when woken from other positions, it appears on the center console screen.
The spatial sound field also shifts with Li Xiang Classmate, creating the feeling of face-to-face conversation with the user.
Special Feature
1489

III. Voice-Visual Fusion Interaction
Li Xiang Classmate uses "deictic commands" combined with gestures to control objects in the cabin.
Currently supports control of sunshades and windows. Example commands:
Special Feature
1490

Point index finger up and say: "Open it" — opens the sunshade.
Point index finger left and say: "Open it halfway" — opens the left window halfway.
Point index finger right and say: "Close it" — closes the right window.
Special Feature
1491""",
"Режимы взаимодействия",
"""Режимы взаимодействия

Режимы взаимодействия
I. Свободный диалог
1. Непрерывный диалог
После активации можно вести несколько разговоров в течение определённого времени без повторной активации.
Особые функции
1485

2. Говорите когда хотите
Прерывайте в любой момент, говорите что хотите — не нужно ждать, пока Ли Сян Тунсюэ закончит говорить.
Особые функции
1486

3. Видите — говорите
Поддерживается прямое произнесение текста кнопок, отображённых на экране — говорите то, что видите.
Функция «Видите — говорите» поддерживает QQ Music, NetEase Cloud Music, iQIYI, National K Song и многие другие приложения; список постоянно расширяется.
4. Семантическое распознавание
Ли Сян Тунсюэ эффективно распознаёт обращённые к нему разговоры и не прерывает беседы пассажиров, исключая случайные срабатывания и защищая конфиденциальность пользователей.
Особые функции
1487

5. Скажите всё сразу
Можно произносить слово-активатор и команду подряд, не дожидаясь ответа Ли Сян Тунсюэ.
Особые функции
1488

II. Пространственное взаимодействие
Ли Сян Тунсюэ стремится обслуживать каждого члена экипажа, появляясь там, где нужно.
При активации с места переднего пассажира — появляется на экране переднего пассажира; при активации с других мест — появляется на центральном экране.
Пространственное звуковое поле также смещается вместе с Ли Сян Тунсюэ, создавая ощущение разговора лицом к лицу.
Особые функции
1489

III. Голосово-визуальное взаимодействие
Ли Сян Тунсюэ использует «указательные команды» в сочетании с жестами для управления объектами в салоне.
В настоящее время поддерживается управление шторками и окнами. Примеры команд:
Особые функции
1490

Укажите указательным пальцем вверх и скажите: «Открой его» — открывает шторку.
Укажите указательным пальцем влево и скажите: «Открой его наполовину» — открывает левое окно наполовину.
Укажите указательным пальцем вправо и скажите: «Закрой его» — закрывает правое окно.
Особые функции
1491""")

# ── CHUNK 1 ── li_auto_l7_zh_39866a1f  HUD height/angle (carobook version)
hud_en = """

IV. Height Adjustment
1. Adaptive Height Adjustment
In the center console screen settings, tap "Display", select "HUD", tap the "Adaptive" option to adaptively adjust the HUD interface height.
Adaptive height adjustment can also be performed via the driver assistance interaction screen.
2. Manual Height Adjustment
In the center console screen settings, tap "Display", select "HUD", tap the options under "Height Adjustment" to manually adjust the HUD interface height.
Driving Scenario
1219

The HUD interface height can also be manually adjusted via the driver assistance interaction screen.
V. Angle Adjustment
In the center console screen settings, tap "Display", select "HUD", tap the options under "Angle Adjustment" to adjust the HUD interface angle.
Driving Scenario
1220

Angle adjustment can also be performed via the driver assistance interaction screen.
VI. HUD Interface Mode
In the center console screen settings, tap "Display", select "HUD", tap the options under "HUD Mode" to configure the HUD display mode.
Driving Scenario
1221

● Select "Speed": HUD displays vehicle speed; when driving assistance is active, map and environment perception information is also displayed.
● Select "Map": HUD displays speed and map; when driving assistance is active, environment perception information is also displayed.
Driving Scenario
1222

● Select "Environment": HUD displays speed and environment perception information; when driving assistance is active, map information is also displayed.
● Select "All": HUD displays speed, environment perception information, and map information.
Driving Scenario
1223"""
hud_ru = """

IV. Регулировка высоты
1. Автоматическая регулировка высоты
В настройках центрального экрана нажмите «Дисплей», выберите «HUD», нажмите «Адаптивная» для автоматической регулировки высоты интерфейса HUD.
Автоматическую регулировку высоты также можно выполнить через экран безопасного вождения.
2. Ручная регулировка высоты
В настройках центрального экрана нажмите «Дисплей», выберите «HUD», нажмите параметры в разделе «Регулировка высоты» для ручной регулировки высоты интерфейса HUD.
Сценарий использования
1219

Ручную регулировку высоты также можно выполнить через экран безопасного вождения.
V. Регулировка угла
В настройках центрального экрана нажмите «Дисплей», выберите «HUD», нажмите параметры в разделе «Регулировка угла» для регулировки угла интерфейса HUD.
Сценарий использования
1220

Регулировку угла также можно выполнить через экран безопасного вождения.
VI. Режим интерфейса HUD
В настройках центрального экрана нажмите «Дисплей», выберите «HUD», нажмите параметры в разделе «Режим HUD» для настройки режима отображения HUD.
Сценарий использования
1221

● Выберите «Скорость»: HUD отображает скорость; при активном режиме помощи водителю также отображается карта и информация о восприятии окружающей среды.
● Выберите «Карта»: HUD отображает скорость и карту; при активном режиме помощи водителю также отображается информация о восприятии окружающей среды.
Сценарий использования
1222

● Выберите «Окружение»: HUD отображает скорость и информацию о восприятии окружающей среды; при активном режиме помощи водителю также отображается карта.
● Выберите «Всё»: HUD отображает скорость, информацию о восприятии окружающей среды и карту.
Сценарий использования
1223"""
add("li_auto_l7_zh_39866a1f", "www.carobook.com", hud_en, "www.carobook.com", hud_ru)

# ── CHUNK 2 ── li_auto_l7_zh_39a60833  same HUD content, user manual watermark
hud2_en = hud_en.replace("Driving Scenario\n1219","User Manual\n").replace("Driving Scenario\n1220","User Manual\n").replace("Driving Scenario\n1221","User Manual\n").replace("Driving Scenario\n1222","User Manual\n").replace("Driving Scenario\n1223","User Manual\n615")
hud2_ru = hud_ru.replace("Сценарий использования\n1219","Руководство пользователя\n").replace("Сценарий использования\n1220","Руководство пользователя\n").replace("Сценарий использования\n1221","Руководство пользователя\n").replace("Сценарий использования\n1222","Руководство пользователя\n").replace("Сценарий использования\n1223","Руководство пользователя\n615")
add("li_auto_l7_zh_39a60833", "www.carobook.com", hud2_en, "www.carobook.com", hud2_ru)

# ── CHUNK 3 ── li_auto_l7_zh_39d5e95f  Side blind zone limitations
add("li_auto_l7_zh_39d5e95f",
"www.carobook.com",
"""

III. Functional Limitations
In the following situations, the Side Blind Zone Assist function may be limited or unable to operate normally, including but not limited to:
● Side Blind Zone Assist cannot provide warning information when reversing.
● For vehicles rapidly approaching in adjacent lanes, the trigger may be delayed.
● For smaller targets such as bicycles and motorcycles, triggering may be delayed or may not occur.
● Drivers should make full use of interior and exterior rearview mirrors; Side Blind Zone Assist cannot replace rearview mirrors.
● Side Blind Zone Assist is primarily designed for normal weather in urban and highway conditions; in special conditions (e.g., heavy rain, snow, standing water, fog, nighttime, tunnels, sandy/dusty/grassy roads), warning accuracy cannot be guaranteed.
● Camera imaging capability is affected, including but not limited to:
◆ Poor visibility due to nighttime conditions.
◆ Poor visibility due to adverse weather (heavy rain, heavy snow, heavy fog, sandstorms).
◆ Strong light, backlighting, water reflections, extreme light contrast, or rapid changes in light/dark (e.g., entering/exiting tunnels).
◆ Camera detection range obstructed by mud, ice, snow, or other objects.
◆ Degraded camera performance due to extreme heat or cold.
Warning
● Side Blind Zone Assist is a driving assistance function and must never replace the driver's observation and judgment of traffic conditions, nor the driver's responsibility for safe vehicle operation.
● Drivers must not become overly reliant on Side Blind Zone Assist, must not intentionally test or wait for function triggering. Due to inherent system limitations, false triggers and missed triggers cannot be completely avoided.
Note
In strong sunlight, the indicator lights on the exterior rearview mirrors may be difficult to see.
Door Opening Collision Warning
When the vehicle is stationary and an approaching vehicle is detected from the rear-side, the system issues visual and audible warnings to alert the driver, reducing the risk of collision when exiting the vehicle.
User Manual
1891""",
"www.carobook.com",
"""

III. Ограничения функции
В следующих ситуациях функция помощи в боковых слепых зонах может быть ограничена или не работать нормально, включая, но не ограничиваясь:
● Помощь в боковых слепых зонах не может выдавать предупреждения при движении задним ходом.
● Для автомобилей, быстро приближающихся в соседних полосах, срабатывание может быть задержано.
● Для небольших объектов, таких как велосипеды и мотоциклы, срабатывание может быть задержано или не происходить вовсе.
● Водители должны в полной мере использовать зеркала заднего вида; функция не может заменить зеркала заднего вида.
● Помощь в боковых слепых зонах предназначена в первую очередь для нормальных погодных условий в городе и на шоссе; в особых условиях (сильный дождь, снег, лужи, туман, ночное время, тоннели, песчаные/пыльные/травяные покрытия) точность предупреждений не гарантируется.
● Нарушение работы камеры, включая, но не ограничиваясь:
◆ Плохая видимость из-за ночного времени.
◆ Плохая видимость из-за неблагоприятных погодных условий (сильный дождь, снег, туман, песчаные бури).
◆ Яркий свет, контровой свет, отражения от воды, экстремальный контраст или быстрые изменения освещённости (въезд/выезд из тоннеля).
◆ Зона обнаружения камеры заблокирована грязью, льдом, снегом или другими предметами.
◆ Снижение производительности камеры из-за экстремального тепла или холода.
Предупреждение
● Помощь в боковых слепых зонах является функцией помощи при вождении и никогда не должна заменять наблюдение и суждение водителя о дорожной обстановке.
● Водители не должны чрезмерно полагаться на эту функцию, намеренно проверять или ожидать её срабатывания. Из-за неотъемлемых ограничений системы ложные и пропущенные срабатывания не могут быть полностью исключены.
Примечание
При ярком солнечном свете сигнальные огни на наружных зеркалах заднего вида могут быть трудно различимы.
Предупреждение о столкновении при открытии двери
Когда автомобиль неподвижен и обнаружено приближающееся сзади-сбоку транспортное средство, система выдаёт визуальное и звуковое предупреждение для снижения риска столкновения при выходе из автомобиля.
Руководство пользователя
1891""")

# ── CHUNK 4 ── li_auto_l7_zh_3a47687a  Airbag non-deployment (side)
add("li_auto_l7_zh_3a47687a",
"www.carobook.com",
"""

7. If the struck object deforms or moves, the impact force is reduced and the airbag may not deploy.
8. In a frontal collision with a stationary vehicle of equivalent weight, the airbag may not deploy.
However, regardless of collision type, the front airbags may deploy as long as sufficient forward deceleration is generated.
VI. Situations Where Side Airbags May Not Deploy
When the vehicle side is struck at an angle to the body, or when the struck area is the vehicle side but not the passenger compartment, the side airbags and side curtain airbags may not deploy, for example:
1. Side impact on body areas outside the passenger compartment.
2. Side impact at a certain angle to the vehicle body.
User Manual

3. Side airbags and side curtain airbags generally will not deploy during low-speed side or rear impacts.
4. When the collision area is small (column collision).
User Manual
555""",
"www.carobook.com",
"""

7. Если поражённый объект деформируется или перемещается, сила удара снижается, и подушка безопасности может не развернуться.
8. При лобовом столкновении со стоящим автомобилем аналогичной массы подушка безопасности может не развернуться.
Однако независимо от типа столкновения передние подушки безопасности могут развернуться, если возникает достаточное замедление вперёд.
VI. Ситуации, когда боковые подушки безопасности могут не развернуться
Когда боковая часть автомобиля испытывает удар под углом к кузову, или зона удара является боковой частью кузова вне пассажирского отсека, боковые подушки безопасности и боковые шторки безопасности могут не развернуться, например:
1. Боковой удар по части кузова вне пассажирского отсека.
2. Боковой удар под определённым углом к кузову автомобиля.
Руководство пользователя

3. Боковые подушки безопасности и боковые шторки безопасности, как правило, не разворачиваются при низкоскоростных боковых ударах или ударах сзади.
4. При небольшой площади столкновения (удар о столб).
Руководство пользователя
555""")

# ── CHUNK 5 ── li_auto_l7_zh_3a4bf05e  Screen mirroring cables
add("li_auto_l7_zh_3a4bf05e",
"www.carobook.com",
"""

V. Cables and External Devices Supporting Screen Mirroring
The following two direct-connect screen mirroring cables are available in the Li Auto Mall.
1. Direct-connect screen mirroring cable (Dual Type-C), supporting:
Gaming consoles: Nintendo Switch (standard), Nintendo Switch (enhanced battery), Nintendo Switch OLED.
Android phones: HUAWEI Mate40 Pro, HUAWEI Mate30 Pro, HUAWEI P40 Pro.
iPad: 12.9-inch iPad Pro (5th gen), 11-inch iPad Pro (3rd gen), iPad Air (5th gen), iPad Mini (6th gen).
Mac: MacBook Air (M1, 2020), MacBook Pro 16-inch (2021), MacBook Pro 14-inch (2021).
2. Direct-connect screen mirroring cable (HDMI to Type-C), supporting:
Gaming consoles: Nintendo Switch (standard), Nintendo Switch (enhanced battery), Nintendo Switch OLED, SONY PS4 Slim, SONY PS5, Microsoft Xbox Series S, Microsoft Xbox Series X.
Windows: Certain laptops with HDMI video output capability.
Special Feature
1478""",
"www.carobook.com",
"""

V. Кабели и внешние устройства для трансляции экрана
В магазине Li Auto доступны следующие два кабеля прямого подключения для трансляции экрана.
1. Кабель прямого подключения для трансляции экрана (двойной Type-C), поддерживаемые устройства:
Игровые консоли: Nintendo Switch (обычная версия), Nintendo Switch (версия с увеличенным аккумулятором), Nintendo Switch OLED.
Android-смартфоны: HUAWEI Mate40 Pro, HUAWEI Mate30 Pro, HUAWEI P40 Pro.
iPad: iPad Pro 12,9 дюйма (5-е поколение), iPad Pro 11 дюймов (3-е поколение), iPad Air (5-е поколение), iPad Mini (6-е поколение).
Mac: MacBook Air (M1, 2020), MacBook Pro 16 дюймов (2021), MacBook Pro 14 дюймов (2021).
2. Кабель прямого подключения для трансляции экрана (HDMI на Type-C), поддерживаемые устройства:
Игровые консоли: Nintendo Switch (обычная версия), Nintendo Switch (версия с увеличенным аккумулятором), Nintendo Switch OLED, SONY PS4 Slim, SONY PS5, Microsoft Xbox Series S, Microsoft Xbox Series X.
Windows: Отдельные ноутбуки с возможностью вывода видеосигнала через HDMI.
Особые функции
1478""")

# ── CHUNK 6 ── li_auto_l7_zh_3a95a527  Service Encyclopedia (voice commands)
add("li_auto_l7_zh_3a95a527",
"Service Encyclopedia",
"""Service Encyclopedia

II. Phone Number Lookup
Function | Voice Command
Look up #phone number# | Help me find Zhang San's phone number
Search contacts by #first letter# | Find contacts starting with Z
Search contacts by #last name# | Find contacts with surname Wang
Open recent calls page | Open call history
Open contacts page | Open contacts
Open dialpad page | Open dialpad
Open official customer service page | Open official customer service

Service Encyclopedia
I. Service Expert
Function | Voice Command
Feature introduction | What is the electric step
| Tell me about seat massage
| What is the convenient entry/exit function
| What is the difference between smart low-beam and regular low-beam
Information lookup | What is the vehicle length
| Does my car have an electric step
| What are common insurance company phone numbers
Special Feature

Function | Voice Command
Operation guidance | How do I turn on the wipers
| Where do I add washer fluid
| How do I open the trunk
| How do I turn on the reading light
| How do I switch sound modes
| How do I open the hood
| How do I connect a microphone
Fault handling | Why won't the electric step open
| Why isn't the seat massage working
| Why is there no power at the outlet

II. Weather
Function | Voice Command
Weather query | Is the weather nice today
| Weather forecast for Beijing for the next 3 days
| What is the temperature in Suzhou
Special Feature

Function | Voice Command
Index queries | Today's dressing index
| Is today good for washing the car
| Check air quality in Shenzhen
| PM2.5 in Suzhou today
| Humidity in Sanya
| What is the UV index
| Cold risk index in Chengdu
Weather queries | Will it rain today
| Is it windy outside
| What wind is blowing in Shenzhen
| What wind is blowing today

III. Jokes
Function | Voice Command
Play a joke | Play a joke
| Tell me a joke
Special Feature

IV. Life Services
Function | Voice Command
Poetry | Recite "Guan Ju"
| Who wrote "Quiet Night Thoughts"
| Which dynasty is "Quiet Night Thoughts" from
| Find a poem about plum blossoms
| What comes after "Moonlight before my bed"
Calculator | What is one plus one
Encyclopedia | Brief introduction to Bing Xin
Calendar | What day is Christmas
| What time is it now
| What is today's date
| What day of the week is today
| What is today's lunar date
| How many days until National Day
Translation | How do you say "Nice to meet you" in English
Special Feature

Function | Voice Command
Stocks | Stock market update for Kweichow Moutai
| Stock price of Kweichow Moutai
| Trading volume of Kweichow Moutai stock
| Trading value of Kweichow Moutai stock
| Check the Shanghai Composite Index
World records | What is the highest mountain in the world
Idioms | What does "Hua Hao Yue Yuan" mean
Horoscopes | What is today's horoscope for Gemini
| What sign is someone born on June 2
| What is Scorpio's most compatible sign
| What are the characteristics of Aquarius
| What dates are Aries born
Traffic restrictions | What are today's restricted license plate numbers
Fuel prices | Check fuel prices in Chengdu
Unit conversion | How many meters are in one kilometer
Exchange rates | How many yuan is one US dollar
Holidays | Check the holiday schedule for New Year's this year
Special Feature""",
"Сервисная энциклопедия",
"""Сервисная энциклопедия

II. Поиск номера телефона
Функция | Голосовая команда
Найти #номер телефона# | Помоги мне найти телефон Чжан Сана
Поиск в контактах по #первой букве# | Найди контакты на букву Z
Поиск в контактах по #фамилии# | Найди контакты с фамилией Ван
Открыть страницу недавних звонков | Открыть историю звонков
Открыть страницу контактов | Открыть контакты
Открыть страницу набора номера | Открыть клавиатуру набора
Открыть страницу официальной службы поддержки | Открыть официальную службу поддержки

Сервисная энциклопедия
I. Сервисный эксперт
Функция | Голосовая команда
Описание функции | Что такое электрическая подножка
| Расскажи о массаже сидений
| Что такое функция удобной посадки/высадки
| В чём разница между умным ближним светом и обычным ближним светом
Информационный запрос | Какова длина автомобиля
| Есть ли в моём автомобиле электрическая подножка
| Каковы телефоны распространённых страховых компаний
Особые функции

Функция | Голосовая команда
Руководство по эксплуатации | Как включить дворники
| Где добавить омывающую жидкость
| Как открыть багажник
| Как включить лампу для чтения
| Как переключить режим звука
| Как открыть капот
| Как подключить микрофон
Устранение неисправностей | Почему не открывается электрическая подножка
| Почему не работает массаж сидений
| Почему нет питания на розетке

II. Погода
Функция | Голосовая команда
Запрос погоды | Хорошая ли сегодня погода
| Прогноз погоды в Пекине на 3 дня
| Какая температура в Сучжоу
Особые функции

Функция | Голосовая команда
Индексные запросы | Индекс одежды на сегодня
| Сегодня подходящий день для мойки машины
| Качество воздуха в Шэньчжэне
| PM2.5 в Сучжоу сегодня
| Влажность в Санья
| Какой УФ-индекс
| Индекс риска простуды в Чэнду
Метеозапросы | Будет ли сегодня дождь
| Сильный ли ветер на улице
| Какой ветер в Шэньчжэне
| Какой ветер дует сегодня

III. Анекдоты
Функция | Голосовая команда
Рассказать анекдот | Расскажи анекдот
| Давай анекдот
Особые функции

IV. Бытовые услуги
Функция | Голосовая команда
Стихи | Прочитай «Гуань Цзюй»
| Кто написал «Тихую ночную думу»
| К какой династии относится «Тихая ночная дума»
| Найди стихотворение о цветении сливы
| Что следует после «Лунный свет перед моей кроватью»
Калькулятор | Сколько будет один плюс один
Энциклопедия | Краткое описание Бин Синь
Календарь | Какой день Рождества
| Который сейчас час
| Какое сегодня число
| Какой сегодня день недели
| Какое сегодня число по лунному календарю
| Сколько дней до Национального праздника
Перевод | Как сказать «Рад познакомиться» по-английски
Особые функции

Функция | Голосовая команда
Акции | Обновление рынка акций Kweichow Moutai
| Цена акций Kweichow Moutai
| Объём торгов акциями Kweichow Moutai
| Стоимость сделок акциями Kweichow Moutai
| Проверить индекс Шанхайской биржи
Мировые рекорды | Какая самая высокая гора в мире
Идиомы | Что означает «Хуа Хао Юэ Юань»
Гороскопы | Каков гороскоп Близнецов сегодня
| Какой знак у рождённых 2 июня
| Какой знак наиболее совместим со Скорпионом
| Какие черты у Водолея
| В какие даты рождаются Овны
Дорожные ограничения | Какие номера сегодня в ограничении
Цены на топливо | Проверить цены на топливо в Чэнду
Единицы измерения | Сколько метров в одном километре
Обменные курсы | Сколько юаней за один доллар США
Праздники | Проверить график выходных на Новый год
Особые функции""")

# ── CHUNK 7 ── li_auto_l7_zh_3ad06f94  Parking space dimensions
add("li_auto_l7_zh_3ad06f94",
"www.carobook.com",
"""

Marked vertical and dual-boundary horizontal parking spaces:
● Horizontal parking space: bay length 5.5m~7m, bay width 2.5m~3m, space length 6.5m~8m, space width 2.5m~3m.
● Vertical parking space: bay width ≥2.2m, space width 2.8m~4m.
Dual-boundary unmarked vertical and horizontal parking spaces:
● Vertical parking space: space width 2.8m~4m.
● Horizontal parking space: space length 6.5m~8m, space width 2.5m~3m.
Single-boundary unmarked horizontal parking space:
● Horizontal parking space: space width 2.5m~3m.
Note
● If vehicle speed exceeds 25 km/h during parking space search, the space search function will automatically exit.
● During the search, keep the vehicle's travel direction as parallel as possible to the entry edge of the parking space; excessive angle will cause space recognition deviation and affect parking performance.
● During the search, maintain a distance greater than 2.5m between the vehicle and obstacles on the opposite side of the parking space.
2. Parking Space Found
When the system detects a parking space, the center console screen will display available space information with an audible prompt.
● White-outlined spaces indicate available spaces. When only one available space exists, the target space shows "P"; when multiple available spaces exist, the target and selectable spaces show corresponding numbers.
● Blue highlighted spaces indicate recommended spaces.
User Manual
1897""",
"www.carobook.com",
"""

Размеченные вертикальные и горизонтальные парковочные места с двойной границей:
● Горизонтальное парковочное место: длина разметки 5,5 м~7 м, ширина разметки 2,5 м~3 м, длина пространства 6,5 м~8 м, ширина пространства 2,5 м~3 м.
● Вертикальное парковочное место: ширина разметки ≥2,2 м, ширина пространства 2,8 м~4 м.
Неразмеченные вертикальные и горизонтальные места с двойной границей:
● Вертикальное парковочное место: ширина пространства 2,8 м~4 м.
● Горизонтальное парковочное место: длина пространства 6,5 м~8 м, ширина пространства 2,5 м~3 м.
Неразмеченные горизонтальные места с одной границей:
● Горизонтальное парковочное место: ширина пространства 2,5 м~3 м.
Примечание
● Если скорость автомобиля превысит 25 км/ч во время поиска парковочного места, функция поиска автоматически выйдет.
● Во время поиска держите направление движения автомобиля максимально параллельным краю въезда в парковочное место; слишком большой угол вызовет отклонение при распознавании места и повлияет на качество парковки.
● Во время поиска поддерживайте расстояние более 2,5 м между автомобилем и препятствиями с противоположной стороны парковочного места.
2. Парковочное место найдено
Когда система обнаруживает парковочное место, центральный экран отобразит информацию о доступном месте со звуковым сигналом.
● Места с белым контуром обозначают доступные места. Когда доступно только одно место, в целевом месте отображается «P»; при наличии нескольких доступных мест на целевом и выбираемых местах отображаются соответствующие номера.
● Места с синей подсветкой обозначают рекомендуемые места.
Руководство пользователя
1897""")

# ── CHUNK 8 ── li_auto_l7_zh_3b3761ad  Warning/indicator lights table
add("li_auto_l7_zh_3b3761ad",
"www.carobook.com",
"""

Icon | Name
Automatic Emergency Braking suppression indicator | If the indicator is lit, it indicates that Automatic Emergency Braking is enabled but temporarily suppressed because an occupant is not seated or has not fastened their seatbelt.
Low-beam indicator | If the indicator is lit, it indicates that the low-beam headlights are on.
High-beam indicator | If the indicator is lit, it indicates that the high-beam headlights are on.
Rear fog light indicator | If the indicator is lit, it indicates that the rear fog lights are on.
Smart low-beam indicator | If the indicator is lit, it indicates that the Smart Low-Beam function is enabled.
Smart high-beam activation indicator | Smart High-Beam is enabled and the system has not activated the high beams — this indicator is lit.
Smart high-beam active indicator | Smart High-Beam is enabled and the system has activated the high beams — this indicator is lit.
Anti-theft authentication failure indicator | If the indicator is lit, it indicates that vehicle anti-theft system authentication has failed. Please contact the Li Auto Customer Service Center.
Electronic parking brake indicator | When the vehicle starts, this indicator lights for a few seconds then goes out, indicating the system is normal. If the indicator remains lit, the electronic parking brake is engaged.
Driving Scenario
162""",
"www.carobook.com",
"""

Иконка | Название
Индикатор подавления автоматического экстренного торможения | Если индикатор горит, это означает, что функция автоматического экстренного торможения включена, но временно подавлена, так как пассажир не сидит или не пристёгнут ремнём безопасности.
Индикатор ближнего света | Если индикатор горит, это означает, что включён ближний свет фар.
Индикатор дальнего света | Если индикатор горит, это означает, что включён дальний свет фар.
Индикатор заднего противотуманного фонаря | Если индикатор горит, это означает, что задние противотуманные фонари включены.
Индикатор интеллектуального ближнего света | Если индикатор горит, это означает, что функция интеллектуального ближнего света включена.
Индикатор готовности интеллектуального дальнего света | Функция интеллектуального дальнего света включена, но система не активировала дальний свет — этот индикатор горит.
Индикатор активации интеллектуального дальнего света | Функция интеллектуального дальнего света включена и система активировала дальний свет — этот индикатор горит.
Индикатор сбоя аутентификации противоугонной системы | Если индикатор горит, это означает, что аутентификация противоугонной системы автомобиля не прошла. Пожалуйста, свяжитесь с центром обслуживания клиентов Li Auto.
Индикатор электрического стояночного тормоза | При запуске автомобиля этот индикатор горит несколько секунд, затем гаснет, что означает нормальную работу системы. Если индикатор продолжает гореть, электрический ручной тормоз активирован.
Сценарий использования
162""")

# ── CHUNK 9 ── li_auto_l7_zh_3b5dbe47  Screen mirroring cables (duplicate, different number)
add("li_auto_l7_zh_3b5dbe47",
"www.carobook.com",
"""

V. Cables and External Devices Supporting Screen Mirroring
The following two direct-connect screen mirroring cables are available in the Li Auto Mall.
1. Direct-connect screen mirroring cable (Dual Type-C), supporting:
Gaming consoles: Nintendo Switch (standard), Nintendo Switch (enhanced battery), Nintendo Switch OLED.
Android phones: HUAWEI Mate40 Pro, HUAWEI Mate30 Pro, HUAWEI P40 Pro.
iPad: 12.9-inch iPad Pro (5th gen), 11-inch iPad Pro (3rd gen), iPad Air (5th gen), iPad Mini (6th gen).
Mac: MacBook Air (M1, 2020), MacBook Pro 16-inch (2021), MacBook Pro 14-inch (2021).
2. Direct-connect screen mirroring cable (HDMI to Type-C), supporting:
Gaming consoles: Nintendo Switch (standard), Nintendo Switch (enhanced battery), Nintendo Switch OLED, SONY PS4 Slim, SONY PS5, Microsoft Xbox Series S, Microsoft Xbox Series X.
Windows: Certain laptops with HDMI video output capability.
Special Feature
2498""",
"www.carobook.com",
"""

V. Кабели и внешние устройства для трансляции экрана
В магазине Li Auto доступны следующие два кабеля прямого подключения для трансляции экрана.
1. Кабель прямого подключения для трансляции экрана (двойной Type-C), поддерживаемые устройства:
Игровые консоли: Nintendo Switch (обычная версия), Nintendo Switch (версия с увеличенным аккумулятором), Nintendo Switch OLED.
Android-смартфоны: HUAWEI Mate40 Pro, HUAWEI Mate30 Pro, HUAWEI P40 Pro.
iPad: iPad Pro 12,9 дюйма (5-е поколение), iPad Pro 11 дюймов (3-е поколение), iPad Air (5-е поколение), iPad Mini (6-е поколение).
Mac: MacBook Air (M1, 2020), MacBook Pro 16 дюймов (2021), MacBook Pro 14 дюймов (2021).
2. Кабель прямого подключения для трансляции экрана (HDMI на Type-C), поддерживаемые устройства:
Игровые консоли: Nintendo Switch (обычная версия), Nintendo Switch (версия с увеличенным аккумулятором), Nintendo Switch OLED, SONY PS4 Slim, SONY PS5, Microsoft Xbox Series S, Microsoft Xbox Series X.
Windows: Отдельные ноутбуки с возможностью вывода видеосигнала через HDMI.
Особые функции
2498""")

# ── CHUNK 10 ── li_auto_l7_zh_3bd8f837  Driving warnings + cargo
add("li_auto_l7_zh_3bd8f837",
"www.carobook.com",
"""

Warning
● Do not park the vehicle on or near flammable or explosive materials to avoid fire.
● Do not place glasses, lighters, or aerosol cans in storage compartments to avoid damage from vibration.
● Do not apply emergency braking, accelerate sharply, or turn the steering wheel sharply on slippery roads to avoid reducing or losing vehicle control.
● Do not drive over flammable materials to avoid vehicle damage or fire.
● Do not press the accelerator pedal without reason to avoid sudden acceleration and accidents.
● Do not use the accelerator pedal or press both accelerator and brake pedals simultaneously to park on a slope.
Note
● When going down a steep slope, use the Hill Descent Control function to maintain stable speed.
● When driving on rough roads, drive slowly to avoid damage to wheels or the vehicle underside.
● When the vehicle needs to ford water, check the water depth first to ensure safe passage.
● After driving through puddles, lightly press the brake pedal to keep the brakes dry and ensure proper braking system operation.
● After driving through flooded sections and if water has entered the vehicle, drive to a Li Auto Service Center for inspection.
● Tire deflation or damage may cause abnormal noises, vibration, difficulty controlling the vehicle, or abnormal tilting. In case of tire deflation or damage, grip the steering wheel firmly and slowly apply the brake pedal.
Cargo and Luggage
Items placed in the trunk can be secured using luggage hooks to prevent luggage movement from affecting driving safety.
Warning
● Do not store fragile, flammable, or explosive hazardous items in the trunk to avoid fire, explosion, or item damage.
● Do not drive the vehicle when overloaded to avoid excessive inertia causing extended braking distances and accidents.
● Do not drive with unevenly distributed loads to avoid losing vehicle balance when cornering.
● Items in the trunk must be secured; otherwise during emergency braking or an accident, items may fly forward and injure vehicle occupants.
Driving Scenario
64""",
"www.carobook.com",
"""

Предупреждение
● Не паркуйте автомобиль на или вблизи легковоспламеняющихся или взрывоопасных материалов во избежание пожара.
● Не помещайте очки, зажигалки или аэрозольные баллончики в отсеки для хранения во избежание повреждения от вибрации.
● Не выполняйте экстренное торможение, резкое ускорение или резкий поворот руля на скользких дорогах во избежание снижения или потери контроля над автомобилем.
● Не проезжайте над легковоспламеняющимися материалами во избежание повреждения автомобиля или пожара.
● Не нажимайте педаль акселератора без причины во избежание внезапного ускорения и аварии.
● Не используйте педаль акселератора или не нажимайте одновременно педали акселератора и тормоза для парковки на уклоне.
Примечание
● При спуске с крутого склона используйте функцию помощи при спуске для поддержания стабильной скорости.
● При движении по неровным дорогам езжайте как можно медленнее, чтобы избежать повреждения колёс или нижней части автомобиля.
● При необходимости переезда через воду предварительно проверьте глубину воды, чтобы обеспечить безопасный проезд.
● После проезда через лужи слегка нажмите педаль тормоза, чтобы тормоза оставались сухими и тормозная система работала нормально.
● После движения через затопленные участки и при попадании воды в автомобиль, отвезите автомобиль в сервисный центр Li Auto для проверки.
● Спущенная или повреждённая шина может вызывать аномальные шумы, вибрацию, трудности с управлением или аномальный крен автомобиля. При спущенной или повреждённой шине крепко держите руль и медленно нажимайте педаль тормоза.
Грузы и багаж
Предметы, помещённые в багажник, можно закрепить с помощью крюков для багажа, чтобы предотвратить смещение багажа и влияние на безопасность вождения.
Предупреждение
● Не храните хрупкие, легковоспламеняющиеся или взрывоопасные опасные предметы в багажнике во избежание пожара, взрыва или повреждения предметов.
● Не управляйте перегруженным автомобилем во избежание чрезмерной инерции, которая приводит к увеличению тормозного пути и авариям.
● Не управляйте автомобилем с неравномерно распределённой нагрузкой во избежание потери равновесия при поворотах.
● Предметы в багажнике должны быть закреплены; в противном случае при экстренном торможении или аварии предметы могут вылететь вперёд и причинить травму пассажирам.
Сценарий использования
64""")

# ── CHUNK 11 ── li_auto_l7_zh_3bd964d7  Trunk anti-pinch and signals
add("li_auto_l7_zh_3bd964d7",
"www.carobook.com",
"""

V. Trunk Door Anti-Pinch
If anti-pinch is triggered while the trunk door is opening/closing, it will reverse a certain distance and the buzzer will sound 3 times.
Warning
Do not use any part of your body to test the anti-pinch function.
VI. Operation Signals
When the trunk door is controlled to open/close via the local switch and the operation is effective, the buzzer sounds 1 time.
When the trunk door cannot open or close, the buzzer sounds 4 times.
When the trunk door is remotely controlled to open or close, the buzzer continuously sounds until the trunk door stops moving.
When the trunk door opening height setting is successfully stored, the buzzer sounds 2 times.
When the trunk door is abnormally stopped during movement (e.g., encountering an obstacle), the buzzer sounds 3 times.
VII. Trunk and Trunk Door Interior Lighting
When the trunk door is opened, the trunk interior light and trunk door interior light illuminate.
VIII. Thermal Protection
Repeatedly opening and closing the trunk door in quick succession will cause the trunk door to enter a thermal protection state. In this state, operations will not be executed. After the motor thermal protection is released, operations can resume.
Warning
● Do not drive the vehicle with the trunk door not properly locked to avoid the trunk door suddenly opening, causing items to fall or an accident.
● Do not operate the trunk door while the vehicle is in motion.
● Do not open the trunk door when there is a heavy load on it (e.g., snow, ice) to avoid vehicle damage or a safety accident.
● Do not allow children to play in the trunk while the vehicle is in motion.
Driving Scenario
92""",
"www.carobook.com",
"""

V. Защита от защемления двери багажника
При срабатывании защиты от защемления во время открытия/закрытия двери багажника дверь совершит обратное движение на определённое расстояние, и зуммер прозвучит 3 раза.
Предупреждение
Не используйте никакую часть тела для проверки функции защиты от защемления.
VI. Сигналы управления
При управлении открытием/закрытием двери багажника через местный переключатель при эффективном управлении зуммер звучит 1 раз.
Если дверь багажника не может открыться или закрыться, зуммер звучит 4 раза.
При дистанционном управлении открытием или закрытием двери багажника зуммер непрерывно звучит до остановки двери багажника.
После успешного сохранения высоты открытия двери багажника зуммер звучит 2 раза.
При аварийной остановке двери багажника во время движения (например, при встрече с препятствием) зуммер звучит 3 раза.
VII. Освещение багажника и внутренней стороны двери багажника
При открытии двери багажника освещение багажника и освещение внутренней стороны двери багажника включается.
VIII. Тепловая защита
При многократном последовательном открытии и закрытии двери багажника она перейдёт в режим тепловой защиты. В этом состоянии операции не будут выполняться. После снятия тепловой защиты двигателя можно продолжить операции.
Предупреждение
● Не управляйте автомобилем с незапертой дверью багажника во избежание внезапного открытия двери, падения предметов или аварии.
● Не управляйте дверью багажника во время движения автомобиля.
● Не открывайте дверь багажника при наличии на ней тяжёлой нагрузки (например, снег, лёд) во избежание повреждения автомобиля или несчастного случая.
● Не позволяйте детям играть в багажнике во время движения автомобиля.
Сценарий использования
92""")

# ── CHUNK 12 ── li_auto_l7_zh_3c07a583  Image quality / Dolby Vision
add("li_auto_l7_zh_3c07a583",
"Image Quality",
"""Image Quality

## Image Quality

## Dolby Vision

• Introduction
Introduction
Supports Dolby Vision video playback, providing an outstanding in-vehicle viewing experience with intelligent display adjustment based on the in-vehicle ambient light.
• Supported Apps
Supported Apps
iQIYI Video, Tencent Video, etc.
• How to Use
How to Use
• In the app category page's Dolby section, select videos marked "Dolby VISION" or "Dolby VISION·ATMOS" to play in Dolby Vision.
In the app category page's Dolby section, select videos marked "Dolby VISION" or "Dolby VISION·ATMOS" to play in Dolby Vision.
• The clarity options on the playback page allow switching to Dolby Vision.
The clarity options on the playback page allow switching to Dolby Vision.
• Dolby Vision is a VIP membership benefit; a VIP account login is required.
• Dolby Vision is only supported when playing through the vehicle amplifier; it cannot be played when headphones are connected.

## Video Quality Enhancement

• Introduction
Introduction
Enhances video playback quality under different lighting conditions.
• Supported Apps
Supported Apps
iQIYI Video, Tencent Video, Youku Video, Huanxi First Release, Bilibili, Migu Video, National K Song, Leishen KTV, browser full-screen video, etc.
• How to Use
How to Use
• The "Video Quality Enhancement" option can be toggled in System Settings > Display > Screen. When enabled, supported apps will automatically enable video quality enhancement during video playback; when disabled, video quality enhancement will be automatically turned off.
The "Video Quality Enhancement" option can be toggled in System Settings > Display > Screen. When enabled, supported apps will automatically enable video quality enhancement during video playback; when disabled, video quality enhancement will be automatically turned off.
• When the playing video is in Dolby Vision, Video Quality Enhancement will be automatically disabled; when the video switches to non-Dolby Vision content, Video Quality Enhancement will be automatically enabled.
When the playing video is in Dolby Vision, Video Quality Enhancement will be automatically disabled; when the video switches to non-Dolby Vision content, Video Quality Enhancement will be automatically enabled.""",
"Качество изображения",
"""Качество изображения

## Качество изображения

## Dolby Vision

• Основное описание
Основное описание
Поддерживает воспроизведение видео в формате Dolby Vision, обеспечивая превосходное качество изображения в салоне с интеллектуальной регулировкой дисплея в зависимости от окружающего освещения в салоне.
• Поддерживаемые приложения
Поддерживаемые приложения
iQIYI Video, Tencent Video и др.
• Как использовать
Как использовать
• В разделе Dolby на странице категорий приложений выберите видео с пометкой "Dolby VISION" или "Dolby VISION·ATMOS" для воспроизведения в Dolby Vision.
В разделе Dolby на странице категорий приложений выберите видео с пометкой "Dolby VISION" или "Dolby VISION·ATMOS" для воспроизведения в Dolby Vision.
• В параметрах чёткости на странице воспроизведения можно переключиться на Dolby Vision.
В параметрах чёткости на странице воспроизведения можно переключиться на Dolby Vision.
• Dolby Vision является привилегией VIP-участника; требуется вход в VIP-аккаунт.
• Dolby Vision поддерживается только при воспроизведении через усилитель автомобиля; при подключении наушников воспроизведение в Dolby Vision недоступно.

## Улучшение качества видео

• Основное описание
Основное описание
Улучшает качество воспроизведения видео при различных условиях освещения.
• Поддерживаемые приложения
Поддерживаемые приложения
iQIYI Video, Tencent Video, Youku Video, Huanxi First Release, Bilibili, Migu Video, National K Song, Leishen KTV, полноэкранное видео в браузере и др.
• Как использовать
Как использовать
• Параметр «Улучшение качества видео» можно переключить в Системных настройках > Дисплей > Экран. При включении поддерживаемые приложения будут автоматически включать улучшение качества видео при воспроизведении; при отключении улучшение качества видео будет автоматически отключено.
Параметр «Улучшение качества видео» можно переключить в Системных настройках > Дисплей > Экран. При включении поддерживаемые приложения будут автоматически включать улучшение качества видео при воспроизведении; при отключении улучшение качества видео будет автоматически отключено.
• При воспроизведении видео в формате Dolby Vision улучшение качества видео будет автоматически отключено; при переключении на контент не в формате Dolby Vision улучшение качества видео будет автоматически включено.
При воспроизведении видео в формате Dolby Vision улучшение качества видео будет автоматически отключено; при переключении на контент не в формате Dolby Vision улучшение качества видео будет автоматически включено.""")

# ── CHUNK 13 ── li_auto_l7_zh_3c2eddbb  Lane departure assist activation
add("li_auto_l7_zh_3c2eddbb",
"www.carobook.com",
"""

II. Function Activation
Lane Departure Assist activates when all of the following conditions are simultaneously met:
● Vehicle speed is between 60 km/h and 135 km/h.
● The vehicle is within the current lane and has been travelling for more than 5 seconds.
● The driver's wheels cross a lane marking without the turn signal activated.
If the following conditions are met, the correction function will be forcibly activated even without the Lane Departure Assist switch being on:
● Vehicle speed is between 45 km/h and 135 km/h.
● The vehicle is in Adaptive Cruise / Lane Keeping Assist / Navigation Assisted Driving mode.
● The driver's wheels cross a lane marking without the turn signal activated.
The following driver control actions may suppress Lane Departure Assist activation:
● Pressing the accelerator pedal.
● Pressing the brake pedal.
● Turning the steering wheel.
● Activating the turn signal or hazard warning lights.
Driving Scenario
1297""",
"www.carobook.com",
"""

II. Активация функции
Помощь при отклонении от полосы движения активируется при одновременном выполнении всех следующих условий:
● Скорость автомобиля от 60 км/ч до 135 км/ч.
● Автомобиль находится в текущей полосе движения и движется более 5 секунд.
● Колёса водителя пересекают разметку полосы без включённого поворотника.
Если выполнены следующие условия, функция коррекции будет принудительно активирована даже без включения переключателя помощи при отклонении от полосы:
● Скорость автомобиля от 45 км/ч до 135 км/ч.
● Автомобиль находится в режиме адаптивного круиз-контроля / помощи при удержании в полосе / навигационного помощника при вождении.
● Колёса водителя пересекают разметку полосы без включённого поворотника.
Следующие действия водителя по управлению автомобилем могут подавлять активацию помощи при отклонении от полосы:
● Нажатие педали акселератора.
● Нажатие педали тормоза.
● Поворот рулевого колеса.
● Включение поворотника или аварийной сигнализации.
Сценарий использования
1297""")

# ── CHUNK 14 ── li_auto_l7_zh_3c337df8  Start reminder
add("li_auto_l7_zh_3c337df8",
"Start Reminder",
"""Start Reminder

Note
This function needs to be enabled in "Settings > Voice".
3. Incoming Call Recognition
The system will proactively identify unknown incoming calls and display spam call information.
Start Reminder
When the driver is operating the vehicle in Drive (D) gear and not in assisted driving mode, and the vehicle has been stopped for a period, when the vehicle ahead moves a certain distance away, the system will emit a prompt tone to remind the driver to start moving.
I. Alert Information
When there is a vehicle ahead and the vehicle ahead has moved a certain distance away, the system will display the message "Vehicle ahead has moved, please press the accelerator pedal" on the center console screen along with a prompt tone.
Driving Scenario
1282


II. Functional Limitations
In the following situations, the start reminder may not be triggered, including but not limited to:
● There are pedestrians, bicycles, motorcycles, etc. ahead.
● There is no vehicle ahead.
● The vehicle gear is not in Drive (D).
● Vehicle speed > 0 km/h.
● The distance between the vehicle ahead and this vehicle is large.
● The vehicle ahead and this vehicle have been stationary for a short time.
● Camera imaging capability is affected, including but not limited to:
◆ Poor visibility due to nighttime conditions.
◆ Poor visibility due to adverse weather (e.g., heavy rain, heavy snow, heavy fog, sandstorms).
◆ Strong light, backlighting, water reflections, extreme light contrast.
◆ Camera obstructed by mud, ice, snow, etc.
◆ Degraded camera performance due to extreme heat or cold.
● Millimeter-wave radar detection capability is affected, including but not limited to:
Driving Scenario
1283""",
"Напоминание о начале движения",
"""Напоминание о начале движения

Примечание
Эту функцию необходимо включить в разделе «Настройки > Голос».
3. Распознавание входящих звонков
Система будет активно распознавать информацию о неизвестных входящих звонках и отображать информацию о спам-звонках.
Напоминание о начале движения
Когда водитель управляет автомобилем в режиме движения вперёд (D) и не в режиме помощи при вождении, и автомобиль был остановлен на определённый период, когда транспортное средство впереди отъехало на определённое расстояние, система выдаёт звуковой сигнал, напоминая водителю начать движение.
I. Информация об оповещении
Когда впереди есть автомобиль и он отъехал на определённое расстояние, система отобразит на центральном экране сообщение «Автомобиль впереди уехал, нажмите педаль акселератора» вместе со звуковым сигналом.
Сценарий использования
1282


II. Ограничения функции
В следующих ситуациях напоминание о начале движения может не срабатывать, включая, но не ограничиваясь:
● Впереди есть пешеходы, велосипеды, мотоциклы и т.д.
● Впереди нет автомобилей.
● Автомобиль не находится в режиме движения вперёд (D).
● Скорость автомобиля > 0 км/ч.
● Расстояние между впереди идущим автомобилем и данным автомобилем велико.
● Автомобиль впереди и данный автомобиль стояли неподвижно короткое время.
● Нарушение работы камеры, включая, но не ограничиваясь:
◆ Плохая видимость из-за ночного времени.
◆ Плохая видимость из-за неблагоприятных погодных условий (сильный дождь, снег, туман, песчаные бури).
◆ Яркий свет, контровой свет, отражения от воды, экстремальный световой контраст.
◆ Камера заблокирована грязью, льдом, снегом и т.д.
◆ Снижение производительности камеры из-за экстремального тепла или холода.
● Нарушение работы миллиметрового радара, включая, но не ограничиваясь:
Сценарий использования
1283""")

# ── CHUNK 15 ── li_auto_l7_zh_3c3af64d  Emergency fuel cap unlock
add("li_auto_l7_zh_3c3af64d",
"www.carobook.com",
"""

IV. Emergency Fuel Cap Unlock
Long-press (10 seconds) the hazard warning light switch to unlock the fuel cap.
Warning
● Do not open the fuel cap when your body carries static electricity. Do not allow personnel who have not discharged static electricity to approach an open fuel tank. Do not return to the vehicle or touch any person or object carrying static electricity, as this may cause static charge buildup that could ignite the fuel.
● Do not smoke, make phone calls, etc. while refueling to avoid fire.
● Do not continue adding fuel to the fuel tank after the fuel nozzle automatically shuts off.
● Do not inhale excessive fuel vapors as fuel contains substances harmful to the body.
● Do not use a fuel cap other than the one specified for this vehicle to avoid fuel leakage due to improper sealing.
Note
● Do not fill the fuel tank too full — stop at the first automatic shutoff. Overfilling can easily cause fuel to enter the charcoal canister, greatly reducing its service life.
User Manual
1953""",
"www.carobook.com",
"""

IV. Аварийная разблокировка крышки топливного бака
Нажмите и удерживайте (10 секунд) переключатель аварийной сигнализации для разблокировки крышки топливного бака.
Предупреждение
● Не открывайте крышку топливного бака, если на вашем теле есть статическое электричество. Не допускайте приближения людей, не снявших статическое электричество, к открытому топливному баку. Не возвращайтесь в салон и не прикасайтесь к людям или предметам, несущим статическое электричество, так как это может вызвать накопление статического заряда, способного воспламенить топливо.
● Не курите и не разговаривайте по телефону во время заправки во избежание пожара.
● Не продолжайте заправку после автоматического отключения пистолета.
● Не вдыхайте избыточные пары топлива, так как топливо содержит вредные для здоровья вещества.
● Не используйте крышку топливного бака, не предназначенную для данного автомобиля, во избежание утечки топлива из-за ненадлежащего уплотнения.
Примечание
● Не заправляйте бак до краёв — остановитесь при первом автоматическом отключении пистолета. Переполнение может привести к попаданию топлива в угольный фильтр, значительно сокращая его срок службы.
Руководство пользователя
1953""")

# Write partial results so far
out_path = 'C:/Diagnostica-KB-Package/knowledge-base/translate_batches/batch_005_out.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"Saved {len(results)} entries (chunks 0-15 translated)")
