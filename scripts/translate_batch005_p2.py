#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Translate batch_005.json chunks 16-32"""
import json

out_path = 'C:/Diagnostica-KB-Package/knowledge-base/translate_batches/batch_005_out.json'
with open(out_path, 'r', encoding='utf-8') as f:
    results = json.load(f)

def add(chunk_id, en_title, en_content, ru_title, ru_content):
    results.append({"id": chunk_id, "lang": "en", "title": en_title, "content": en_content})
    results.append({"id": chunk_id, "lang": "ru", "title": ru_title, "content": ru_content})

# ── CHUNK 16 ── li_auto_l7_zh_3c4a7057  Airbags full section
add("li_auto_l7_zh_3c4a7057",
"Airbags",
"""Airbags

## Airbags

The Li Auto L7 is equipped with 9 airbags to protect occupants.
The airbags are located at the following positions:
Side curtain airbags: Protect the heads of occupants in outboard seats.
Front airbags: Protect the heads and chests of the driver and front passenger from impact with interior components during a collision.
Side airbags: Protect the torsos of the driver, front seat occupants, and second-row outboard seat occupants. The far-side airbag on the inside of the driver's seat protects the shoulders and heads of both the driver and front passenger to minimize injury.

## Effects of Airbag Deployment

• When an airbag deploys, it may cause abrasions, burns, and bruises to occupants.
When an airbag deploys, it may cause abrasions, burns, and bruises to occupants.
• When an airbag deploys, it will produce a loud sound and emit white powder.
When an airbag deploys, it will produce a loud sound and emit white powder.
• Within a few minutes after airbag deployment, the airbag and seat components may be very hot.
Within a few minutes after airbag deployment, the airbag and seat components may be very hot.
• The windshield may crack.
The windshield may crack.

## Front Airbag Deployment Conditions

When a collision reaches a certain level of severity or exceeds a set threshold, the front airbags will deploy.

## Side Airbag and Side Curtain Airbag Deployment Conditions

• If a side collision occurs and sensors detect a sudden change in lateral acceleration, and the system determines airbag deployment conditions are met, the side airbags and side curtain airbags will deploy.
If a side collision occurs and sensors detect a sudden change in lateral acceleration, and the system determines airbag deployment conditions are met, the side airbags and side curtain airbags will deploy.
• In the event of a severe frontal collision or rollover, the side airbags and side curtain airbags may also deploy.
In the event of a severe frontal collision or rollover, the side airbags and side curtain airbags may also deploy.

## Non-Collision Situations Where Airbags May Deploy

If the vehicle underside suffers a severe impact, the front airbags, side airbags, and side curtain airbags may also deploy, for example:
• Hitting a road curb, sidewalk edge, or hard surface.
Hitting a road curb, sidewalk edge, or hard surface.
• Falling into or jumping over a deep pit.
Falling into or jumping over a deep pit.
• Hard landing on wheels or vehicle drop.
Hard landing on wheels or vehicle drop.

## Situations Where Front Airbags May Not Deploy

During low-speed frontal collisions, side collisions, rear collisions, or rollovers, front airbags generally will not deploy, for example:
• Side collision.
Side collision.
• Rear collision or being rear-ended.
Rear collision or being rear-ended.
• Impact while vehicle is in sleep mode.
Impact while vehicle is in sleep mode.
• Rollover.
Rollover.
• Frontal center impact with a stationary small-area object such as a utility pole or tree at speeds below 35 km/h.
Frontal center impact with a stationary small-area object such as a utility pole or tree at speeds below 35 km/h.
• Rear-ending the underside of a large truck or similar vehicle.
Rear-ending the underside of a large truck or similar vehicle.
• The struck object deforms or moves.
The struck object deforms or moves.
• Frontal collision with a stationary vehicle of equivalent weight.
Frontal collision with a stationary vehicle of equivalent weight.

## Situations Where Side Airbags May Not Deploy

When the vehicle side is struck at an angle to the body, or when the struck area is the vehicle side but not the passenger compartment, the side airbags and side curtain airbags may not deploy, for example:
• Side impact on body areas outside the passenger compartment.
Side impact on body areas outside the passenger compartment.
• Side impact at a certain angle to the vehicle body.
Side impact at a certain angle to the vehicle body.
• Low-speed side impact or rear impact.
• Small-area collision such as a column collision.
Small-area collision such as a column collision.

## When to Contact the Li Auto Customer Service Center

In the following situations, the vehicle needs inspection or repair — please contact the Li Auto Customer Service Center as soon as possible:
• Any airbag has deployed.
• The front of the vehicle is damaged or deformed, or the vehicle has been in a collision not severe enough to deploy the front airbags.
• A vehicle door area is damaged or deformed, or the vehicle has been in a collision not severe enough to deploy the side curtain airbags and side airbags.
A vehicle door area is damaged or deformed, or the vehicle has been in a collision not severe enough to deploy the side curtain airbags and side airbags.
• There are scratches, cracks, or other damage on the steering wheel decorative cover or the dashboard near the front passenger airbag.
There are scratches, cracks, or other damage on the steering wheel decorative cover or the dashboard near the front passenger airbag.
• There are scratches, cracks, or other damage on the seat surface in the area where side airbags are installed.
There are scratches, cracks, or other damage on the seat surface in the area where side airbags are installed.
• There are scratches, cracks, or other damage at the side curtain airbag installation location.
There are scratches, cracks, or other damage at the side curtain airbag installation location.

## Regarding Added Seat Covers, Etc.

Seat covers, pads, or other accessories added to the seat may affect the normal deployment of side airbags, preventing effective occupant protection.
• Do not touch airbag components after deployment to avoid burns.
Do not touch airbag components after deployment to avoid burns.
• Do not drive the vehicle if any airbag components (e.g., steering wheel decorative cover) are damaged or cracked, to avoid sudden airbag deployment or non-deployment in an accident causing serious injury.
Do not drive the vehicle if any airbag components (e.g., steering wheel decorative cover) are damaged or cracked, to avoid sudden airbag deployment or non-deployment in an accident causing serious injury.
• Do not place or affix any objects in the airbag deployment area (e.g., hooks or decorations on pillars near side curtain airbags); these objects can cause secondary injury to passengers during deployment.
Do not place or affix any objects in the airbag deployment area (e.g., hooks or decorations on pillars near side curtain airbags); these objects can cause secondary injury to passengers during deployment.
• It is strictly prohibited to install a child safety seat in the front seat.
It is strictly prohibited to install a child safety seat in the front seat.
• Do not hold infants or children on your lap. A deploying airbag can cause serious injury to a held infant or child. All infants and children should be properly restrained in the rear seats.
Do not hold infants or children on your lap. A deploying airbag can cause serious injury to a held infant or child. All infants and children should be properly restrained in the rear seats.
• Do not strike airbag components to avoid accidental deployment.
Do not strike airbag components to avoid accidental deployment.
• Do not tamper with or disconnect wiring or other components of the supplemental restraint system; improper operation can cause the airbag to malfunction or deploy unexpectedly, causing serious injury or death.
Do not tamper with or disconnect wiring or other components of the supplemental restraint system; improper operation can cause the airbag to malfunction or deploy unexpectedly, causing serious injury or death.
If airbags do not activate during a collision, it does not necessarily indicate a malfunction. It typically means the collision's intensity or type was insufficient to activate them.
Airbags are supplemental devices and must be used together with seatbelts to effectively protect occupants and reduce casualties.

No. | Name | No. | Name
1 | Side curtain airbag ×2 | 3 | Side airbag ×5
2 | Front airbag ×2 |  |""",
"Подушки безопасности",
"""Подушки безопасности

## Подушки безопасности

Автомобиль Li Auto L7 оснащён 9 подушками безопасности для защиты водителя и пассажиров.
Подушки безопасности расположены в следующих местах:
Боковые шторки безопасности: Защищают головы пассажиров на крайних сиденьях.
Передние подушки безопасности: Защищают голову и грудь водителя и переднего пассажира от ударов о внутренние компоненты при столкновении.
Боковые подушки безопасности: Защищают туловище водителя, пассажиров на передних сиденьях и пассажиров на крайних сиденьях второго ряда. Дальняя боковая подушка безопасности с внутренней стороны сиденья водителя защищает плечи и голову как водителя, так и переднего пассажира, минимизируя травмы.

## Последствия срабатывания подушек безопасности

• При срабатывании подушки безопасности возможны ссадины, ожоги и синяки у пассажиров.
При срабатывании подушки безопасности возможны ссадины, ожоги и синяки у пассажиров.
• При срабатывании подушки безопасности раздаётся громкий звук и выбрасывается белый порошок.
При срабатывании подушки безопасности раздаётся громкий звук и выбрасывается белый порошок.
• В течение нескольких минут после срабатывания подушки безопасности сама подушка и компоненты сидений могут быть очень горячими.
В течение нескольких минут после срабатывания подушки безопасности сама подушка и компоненты сидений могут быть очень горячими.
• Ветровое стекло может треснуть.
Ветровое стекло может треснуть.

## Условия срабатывания передних подушек безопасности

Когда столкновение достигает определённого уровня интенсивности или превышает установленное пороговое значение, передние подушки безопасности срабатывают.

## Условия срабатывания боковых подушек безопасности и боковых шторок безопасности

• При боковом столкновении, когда датчики обнаруживают резкое изменение бокового ускорения, и система определяет, что условия срабатывания выполнены, боковые подушки безопасности и боковые шторки безопасности срабатывают.
При боковом столкновении, когда датчики обнаруживают резкое изменение бокового ускорения, и система определяет, что условия срабатывания выполнены, боковые подушки безопасности и боковые шторки безопасности срабатывают.
• При серьёзном лобовом столкновении или опрокидывании боковые подушки безопасности и боковые шторки безопасности также могут сработать.
При серьёзном лобовом столкновении или опрокидывании боковые подушки безопасности и боковые шторки безопасности также могут сработать.

## Ситуации несанкционированного срабатывания подушек безопасности

При сильном ударе по днищу автомобиля передние подушки безопасности, боковые подушки безопасности и боковые шторки безопасности также могут сработать, например:
• Удар о бордюр, край тротуара или твёрдую поверхность.
Удар о бордюр, край тротуара или твёрдую поверхность.
• Падение в или прыжок через глубокую яму.
Падение в или прыжок через глубокую яму.
• Жёсткое приземление на колёса или падение автомобиля.
Жёсткое приземление на колёса или падение автомобиля.

## Ситуации, когда передние подушки безопасности могут не сработать

При низкоскоростном лобовом столкновении, боковом столкновении, ударе сзади или опрокидывании передние подушки безопасности, как правило, не срабатывают, например:
• Боковое столкновение.
Боковое столкновение.
• Удар сзади или наезд сзади.
Удар сзади или наезд сзади.
• Удар при автомобиле в спящем режиме.
Удар при автомобиле в спящем режиме.
• Опрокидывание.
Опрокидывание.
• Центральный лобовой удар о неподвижный малогабаритный объект, такой как столб или дерево, на скорости ниже 35 км/ч.
Центральный лобовой удар о неподвижный малогабаритный объект, такой как столб или дерево, на скорости ниже 35 км/ч.
• Наезд сзади под кузов большого грузовика или аналогичного транспортного средства.
Наезд сзади под кузов большого грузовика или аналогичного транспортного средства.
• Поражённый объект деформируется или перемещается.
Поражённый объект деформируется или перемещается.
• Лобовое столкновение со стоящим автомобилем аналогичной массы.
Лобовое столкновение со стоящим автомобилем аналогичной массы.

## Ситуации, когда боковые подушки безопасности могут не сработать

Когда боковая часть автомобиля испытывает удар под углом к кузову, или зона удара является боковой частью кузова вне пассажирского отсека, боковые подушки безопасности и боковые шторки безопасности могут не сработать, например:
• Боковой удар по части кузова вне пассажирского отсека.
Боковой удар по части кузова вне пассажирского отсека.
• Боковой удар под определённым углом к кузову автомобиля.
Боковой удар под определённым углом к кузову автомобиля.
• Низкоскоростной боковой удар или удар сзади.
• Малогабаритное столкновение, например удар о столб.
Малогабаритное столкновение, например удар о столб.

## Когда следует обратиться в центр обслуживания клиентов Li Auto

В следующих ситуациях автомобиль нуждается в проверке или ремонте — обратитесь в центр обслуживания клиентов Li Auto как можно скорее:
• Сработала любая подушка безопасности.
• Передняя часть автомобиля повреждена или деформирована, или автомобиль побывал в столкновении, недостаточно сильном для срабатывания передних подушек безопасности.
• Область двери автомобиля повреждена или деформирована, или автомобиль побывал в столкновении, недостаточно сильном для срабатывания боковых шторок и боковых подушек безопасности.
Область двери автомобиля повреждена или деформирована, или автомобиль побывал в столкновении, недостаточно сильном для срабатывания боковых шторок и боковых подушек безопасности.
• На декоративной крышке руля или приборной панели вблизи подушки безопасности переднего пассажира есть царапины, трещины или другие повреждения.
На декоративной крышке руля или приборной панели вблизи подушки безопасности переднего пассажира есть царапины, трещины или другие повреждения.
• На поверхности сиденья в зоне установки боковых подушек безопасности есть царапины, трещины или другие повреждения.
На поверхности сиденья в зоне установки боковых подушек безопасности есть царапины, трещины или другие повреждения.
• В месте установки боковых шторок безопасности есть царапины, трещины или другие повреждения.
В месте установки боковых шторок безопасности есть царапины, трещины или другие повреждения.

## Относительно установки чехлов для сидений и т.п.

Чехлы, подушки и другие аксессуары, установленные на сиденье, могут помешать нормальному срабатыванию боковых подушек безопасности и не обеспечат эффективную защиту пассажиров.
• Не прикасайтесь к компонентам подушки безопасности после срабатывания во избежание ожогов.
Не прикасайтесь к компонентам подушки безопасности после срабатывания во избежание ожогов.
• Не управляйте автомобилем при наличии повреждений или трещин на компонентах подушки безопасности (например, декоративной крышке руля) во избежание внезапного срабатывания или несрабатывания подушки безопасности в аварии, что может привести к серьёзным травмам.
Не управляйте автомобилем при наличии повреждений или трещин на компонентах подушки безопасности (например, декоративной крышке руля) во избежание внезапного срабатывания или несрабатывания подушки безопасности в аварии, что может привести к серьёзным травмам.
• Не помещайте и не прикрепляйте никакие предметы в зоне срабатывания подушки безопасности (например, крючки или украшения на стойках рядом с боковыми шторками безопасности); эти предметы могут причинить вторичные травмы пассажирам при срабатывании.
Не помещайте и не прикрепляйте никакие предметы в зоне срабатывания подушки безопасности (например, крючки или украшения на стойках рядом с боковыми шторками безопасности); эти предметы могут причинить вторичные травмы пассажирам при срабатывании.
• Категорически запрещается устанавливать детское кресло на переднем сиденье.
Категорически запрещается устанавливать детское кресло на переднем сиденье.
• Не держите младенцев или детей на коленях. Срабатывающая подушка безопасности может серьёзно травмировать ребёнка. Все младенцы и дети должны быть правильно пристёгнуты на задних сиденьях.
Не держите младенцев или детей на коленях. Срабатывающая подушка безопасности может серьёзно травмировать ребёнка. Все младенцы и дети должны быть правильно пристёгнуты на задних сиденьях.
• Не ударяйте по компонентам подушки безопасности во избежание случайного срабатывания.
Не ударяйте по компонентам подушки безопасности во избежание случайного срабатывания.
• Не вмешивайтесь и не отсоединяйте проводку или другие компоненты системы дополнительной защиты; ненадлежащие действия могут привести к неисправности подушки безопасности или случайному срабатыванию, вызывающему серьёзные травмы или смерть.
Не вмешивайтесь и не отсоединяйте проводку или другие компоненты системы дополнительной защиты; ненадлежащие действия могут привести к неисправности подушки безопасности или случайному срабатыванию, вызывающему серьёзные травмы или смерть.
Если подушки безопасности не срабатывают при столкновении, это не обязательно означает неисправность. Как правило, это означает, что интенсивность или тип столкновения оказались недостаточными для их активации.
Подушки безопасности являются дополнительными устройствами и должны использоваться совместно с ремнями безопасности для эффективной защиты пассажиров и снижения травматизма.

№ | Наименование | № | Наименование
1 | Боковые шторки безопасности ×2 | 3 | Боковые подушки безопасности ×5
2 | Передние подушки безопасности ×2 |  |""")

# ── CHUNK 17 ── li_auto_l7_zh_3cf0aabe  Navigation voice commands
add("li_auto_l7_zh_3cf0aabe",
"Navigation",
"""Navigation

Function | Voice Command
Window/sunshade control (point finger toward window/sunshade while speaking) | Open it
| Close it
| Open it halfway
| Open it a little more
Navigation
I. Start Navigation
Function | Voice Command
Navigate to a place | I want to go to Tiananmen
| Navigate to a gas station
| Navigate home / to the office
| Navigate home
| Navigate to the office
Set home/office address | Set ** as home
| Set ** as the office (** represents building name)
Navigate to a frequent address | Navigate to frequent address
Set a frequent address | Set as frequent address
| Set this as a frequent address
| ** is my frequent address
Navigate to a saved address | Navigate to saved address
Special Feature
1495


Function | Voice Command
Save an address | Save ** Building
| Save this location
Restaurant search | What's good to eat nearby
| Nearby hot pot restaurants
| I'm hungry
| I'm thirsty
Start navigation | Start navigation
Exit navigation | Exit navigation
| Cancel navigation
Continue navigation | Continue navigation
Close map | Exit map
Add waypoint | Stop by a convenience store on the way
Delete waypoint | Delete waypoint
| Delete the 3rd waypoint
| Delete all waypoints
Start navigation with waypoints | Go to the Summer Palace first then the Forbidden City
| Go home first then to the office
Cancel | Never mind (non-navigation: cancel; navigation: cancel navigation)
Special Feature
1496


Function | Voice Command
Change destination | Change destination
| Change the destination to Tiananmen
II. Navigation Search
Function | Voice Command
Locate current position | Where am I
Search for a specific place | Where is Xidan Joy City
Search by place type | Find restaurants
Search by place alias | Where is the "Big Pants" building
Search for a specific road | Where is Happiness Avenue
Search by street number | Where is 10 Wangjing Street
Search for a city | Where is Nanjing
Nearby search | Nearby parking lots
| The car is out of fuel
| The car is out of charge
| Are there gas stations near the zoo
Along-route search | Check for supermarkets along the route
III. Navigation Information
Function | Voice Command
Remaining distance in navigation | How far is it
Remaining time in navigation | How long until we arrive
Special Feature
1497


Function | Voice Command
Estimated arrival time | What time will we arrive approximately
Highway service area query | How far am I from a service area
| What service area is ahead
| Are there service areas on this road
Highway toll station query | How far to the toll station
| Which toll station is ahead
Road condition query ahead | Is there traffic ahead
| How long is the traffic jam ahead
| How long will the traffic jam last
Open place details card | Check the introduction for McDonald's
Query destination | Where is the destination
Query POI information | What is the average cost at Quanjude
| What is the rating of Haidilao
IV. Navigation Map View
Function | Voice Command
Open a specific map page | Open map search
| Open navigation settings
| View overview
View overview | View overview
Exit overview | Exit overview
Special Feature
1498


Function | Voice Command
Switch route | Take a different route
| Switch to the first route
Main/service road switch | Switch to the main road
| Take the service road
Elevated road switch | Take the elevated road
| Go down from elevated road
| Take the elevated road
Refresh route | Refresh route
Map zoom | Zoom in map
| Zoom out map
View direction switch | North up
| Heading up
Cruise broadcast settings | Enable cruise broadcast
| Disable cruise broadcast
Cruise speed camera settings | Enable cruise speed camera
| Disable cruise speed camera
Safety reminder settings | Enable safety reminder
| Disable safety reminder
Special Feature
1499


Function | Voice Command
Upcoming road condition broadcast settings | Enable upcoming road condition broadcast
| Disable upcoming road condition broadcast
License plate number settings | Enter license plate number
| My license plate number is 京A12345
| Change license plate number
| Change license plate to 京A54321
Navigation playback mode switch | Simple navigation
| Detailed navigation broadcast
Avoid traffic restriction settings | Enable avoid traffic restrictions
| Disable avoid traffic restrictions
Real-time traffic settings | Enable/disable real-time traffic
Auto scale settings | Enable/disable auto scale
Lane-level navigation switch settings | Enable/disable lane-level navigation
Special Feature
1500""",
"Навигация",
"""Навигация

Функция | Голосовая команда
Управление окном/шторкой (укажите пальцем в направлении окна/шторки) | Открой это
| Закрой это
| Открой наполовину
| Открой ещё немного
Навигация
I. Запуск навигации
Функция | Голосовая команда
Проложить маршрут к месту | Хочу поехать на площадь Тяньаньмэнь
| Проложить маршрут к заправке
| Проложить маршрут домой / в офис
| Проложить маршрут домой
| Проложить маршрут в офис
Задать адрес дома/офиса | Задать ** как дом
| Задать ** как офис (** — название здания)
Проложить маршрут по частому адресу | Проложить маршрут к частому адресу
Задать частый адрес | Задать как частый адрес
| Задать это место как частый адрес
| ** — мой частый адрес
Проложить маршрут по сохранённому адресу | Проложить маршрут к сохранённому адресу
Особые функции
1495


Функция | Голосовая команда
Сохранить адрес | Сохранить здание **
| Сохранить это место
Поиск ресторана | Что поесть поблизости
| Ближайшие рестораны с хот-потом
| Я голоден
| Я хочу пить
Начать навигацию | Начать навигацию
Выйти из навигации | Выйти из навигации
| Отменить навигацию
Продолжить навигацию | Продолжить навигацию
Закрыть карту | Выйти из карты
Добавить промежуточную точку | Заехать в магазин по пути
Удалить промежуточную точку | Удалить промежуточную точку
| Удалить 3-ю промежуточную точку
| Удалить все промежуточные точки
Начать навигацию с промежуточными точками | Сначала в Парк Ихэюань, потом в Запретный город
| Сначала домой, потом в офис
Отменить | Не поеду (не в режиме навигации: отмена; в режиме навигации: отмена навигации)
Особые функции
1496


Функция | Голосовая команда
Изменить пункт назначения | Изменить пункт назначения
| Изменить конечную точку на площадь Тяньаньмэнь
II. Поиск в навигации
Функция | Голосовая команда
Определить текущее местоположение | Где я нахожусь
Поиск конкретного места | Где находится торговый центр Xidan Joy City
Поиск по типу места | Найти рестораны
Поиск по псевдониму места | Где находятся «Большие штаны»
Поиск конкретной дороги | Где находится улица Счастья
Поиск по номеру дома | Где находится дом 10 по улице Ванцзин
Поиск города | Где находится Нанкин
Поиск поблизости | Ближайшие парковки
| В машине закончилось топливо
| В машине разрядился аккумулятор
| Есть ли заправки рядом с зоопарком
Поиск по маршруту | Найти супермаркеты по дороге
III. Информация о навигации
Функция | Голосовая команда
Оставшееся расстояние в навигации | Сколько ещё ехать
Оставшееся время в навигации | Когда мы приедем
Особые функции
1497


Функция | Голосовая команда
Расчётное время прибытия | Примерно в котором часу приедем
Запрос зон отдыха на шоссе | Как далеко до ближайшей зоны отдыха
| Что за зона отдыха впереди
| Есть ли зоны отдыха на этой дороге
Запрос пунктов оплаты на шоссе | Как далеко до пункта оплаты
| Какой пункт оплаты впереди
Запрос о дорожной обстановке | Есть ли пробки впереди
| Какова длина пробки впереди
| Сколько времени займёт преодоление пробки
Открыть карточку с подробностями о месте | Посмотреть описание McDonald's
Запрос пункта назначения | Где находится пункт назначения
Запрос информации о POI | Какова средняя стоимость в Quanjude
| Какой рейтинг у Haidilao
IV. Вид карты навигации
Функция | Голосовая команда
Открыть определённую страницу карты | Открыть поиск на карте
| Открыть настройки навигации
| Просмотреть обзор
Просмотреть обзор | Просмотреть обзор
Выйти из обзора | Выйти из обзора
Особые функции
1498


Функция | Голосовая команда
Переключить маршрут | Выбрать другой маршрут
| Переключиться на первый маршрут
Переключение главной/служебной дороги | Переключиться на главную дорогу
| Поехать по служебной дороге
Переключение эстакады | Подняться на эстакаду
| Спуститься с эстакады
| Ехать по эстакаде
Обновить маршрут | Обновить маршрут
Масштабирование карты | Увеличить карту
| Уменьшить карту
Переключение направления просмотра | Север вверху
| Направление движения вверху
Настройки крейсерского вещания | Включить крейсерское вещание
| Отключить крейсерское вещание
Настройки камер на крейсерском режиме | Включить камеры на крейсерском режиме
| Отключить камеры на крейсерском режиме
Настройки предупреждений безопасности | Включить предупреждения безопасности
| Отключить предупреждения безопасности
Особые функции
1499


Функция | Голосовая команда
Настройки вещания о дорожной обстановке впереди | Включить вещание о дорожной обстановке
| Отключить вещание о дорожной обстановке
Настройки номерного знака | Ввести номерной знак
| Мой номерной знак 京A12345
| Изменить номерной знак
| Изменить номерной знак на 京A54321
Переключение режима воспроизведения навигации | Упрощённая навигация
| Детальное навигационное вещание
Настройки обхода ограничений движения | Включить обход ограничений движения
| Отключить обход ограничений движения
Настройки дорожной обстановки в реальном времени | Включить/отключить дорожную обстановку в реальном времени
Настройки автомасштаба | Включить/отключить автомасштаб
Настройки навигации по полосам | Включить/отключить навигацию по полосам
Особые функции
1500""")

# ── CHUNK 18 ── li_auto_l7_zh_3d317952  Dolby Atmos copyright note
add("li_auto_l7_zh_3d317952",
"www.carobook.com",
"""

Method 2: Sound effect options on the app playback page.
4. Copyright Notice
This product is manufactured under license from Dolby Laboratories. Dolby, Dolby Atmos, and the double-D symbol are registered trademarks of Dolby Laboratories Licensing Corporation. Unpublished confidential work. Copyright 2012-2021 Dolby Laboratories. All rights reserved.
Note
● When watching Atmos and surround sound content, it is recommended to use the full-vehicle mode rather than switching to front-row or rear-row mode for a better Dolby Atmos experience.
● A highlighted Dolby Atmos option indicates that the content supports Dolby Atmos audio; a greyed-out Dolby Atmos option indicates the content does not support Dolby Atmos audio.
● Due to varying source content, some content supports Dolby Atmos while others support Dolby Surround Sound.
● Dolby Atmos audio is a VIP membership benefit; a VIP account login is required.
● Dolby Atmos audio only supports 1.0x playback speed; non-1.0x speed does not support Dolby Atmos audio.
● Dolby Atmos is only supported by the vehicle amplifier; it cannot be played when headphones are connected.
Special Feature
2477""",
"www.carobook.com",
"""

Способ 2: Параметры звукового эффекта на странице воспроизведения приложения.
4. Уведомление об авторских правах
Этот продукт изготовлен по лицензии Dolby Laboratories. Dolby, Dolby Atmos и символ двойной D являются зарегистрированными товарными знаками Dolby Laboratories Licensing Corporation. Неопубликованная конфиденциальная работа. Авторское право 2012-2021 Dolby Laboratories. Все права защищены.
Примечание
● При просмотре контента в формате Atmos и объёмного звука рекомендуется использовать режим всего автомобиля, а не переключаться на режим переднего или заднего ряда для лучшего опыта Dolby Atmos.
● Выделенный параметр Dolby Atmos означает, что контент поддерживает Dolby Atmos; затемнённый параметр означает, что контент не поддерживает Dolby Atmos.
● В зависимости от источника контента, некоторые материалы поддерживают Dolby Atmos, другие — объёмный звук Dolby.
● Звук Dolby Atmos является привилегией VIP-участника; требуется вход в VIP-аккаунт.
● Звук Dolby Atmos поддерживает только воспроизведение со скоростью 1,0x; скорость, отличная от 1,0x, не поддерживает Dolby Atmos.
● Dolby Atmos поддерживается только усилителем автомобиля; при подключении наушников воспроизведение недоступно.
Особые функции
2477""")

# ── CHUNK 19 ── li_auto_l7_zh_3d6e18a9  Rear AC controls (carobook)
rear_ac_en = """

Short press up/down on the temperature adjustment button to set the rear temperature; each short press increases or decreases the temperature by 0.5°C. Long press up/down on the temperature adjustment button to quickly adjust the temperature.
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
User Manual
2760"""
rear_ac_ru = """

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
Руководство пользователя
2760"""
add("li_auto_l7_zh_3d6e18a9", "www.carobook.com", rear_ac_en, "www.carobook.com", rear_ac_ru)

# ── CHUNK 20 ── li_auto_l7_zh_3ddfcd58  Smart child seat warning
add("li_auto_l7_zh_3ddfcd58",
"www.carobook.com",
"""

III. Smart Child Safety Seat Warning
Li Auto's service partners or other authorized service partners can provide smart child safety seats with a child left-behind reminder function.
Li Auto recommended smart child safety seat model: Goodbaby CONVY-FIX-L.
Note
● The smart child safety seat must maintain a Bluetooth connection when in use; always confirm this each time you travel with a child.
● Because the smart child safety seat uses biosensor technology, it may produce some false recognition for objects with physical properties similar to those of the human body. Objects with capacitance similar to the human body and of sufficient weight (e.g., liquids, meat, fruit) placed in the smart child safety seat may be misidentified as a child and trigger the child left-behind reminder. When the vehicle issues a child left-behind reminder, the user must make further verification.
In the center console screen settings, tap "Accessories", select "Child Seat", tap the options under "Child Left-Behind Reminder" to enable or disable the child left-behind reminder function.
When the child left-behind reminder is enabled, within 1 minute of the driver locking the vehicle, if the child safety seat sensor detects a child is seated, the vehicle will sound the horn and simultaneously send a reminder via the Li Auto App and phone call to notify the user.
User Manual
1604""",
"www.carobook.com",
"""

III. Предупреждение интеллектуального детского кресла
Сервисные партнёры Li Auto или другие авторизованные сервисные партнёры могут предоставить интеллектуальные детские кресла с функцией напоминания об оставленном ребёнке.
Рекомендуемая модель интеллектуального детского кресла Li Auto: Goodbaby CONVY-FIX-L.
Примечание
● При использовании интеллектуальное детское кресло должно поддерживать соединение Bluetooth; всегда проверяйте это при каждой поездке с ребёнком.
● Поскольку интеллектуальное детское кресло использует биосенсорную технологию, оно может давать ложные срабатывания для объектов с физическими свойствами, схожими с человеческим телом. Объекты с ёмкостью, близкой к человеческому телу, и достаточной массой (например, жидкости, мясо, фрукты), помещённые в интеллектуальное детское кресло, могут быть ошибочно идентифицированы как ребёнок и вызвать напоминание об оставленном ребёнке. При получении автомобилем напоминания об оставленном ребёнке пользователь должен провести дополнительную проверку.
В настройках центрального экрана нажмите «Аксессуары», выберите «Детское кресло», нажмите параметры в разделе «Напоминание об оставленном ребёнке» для включения или отключения функции.
При включённой функции напоминания об оставленном ребёнке в течение 1 минуты после блокировки автомобиля водителем, если датчик детского кресла обнаруживает сидящего ребёнка, автомобиль подаст звуковой сигнал и одновременно отправит уведомление через приложение Li Auto и позвонит пользователю.
Руководство пользователя
1604""")

# ── CHUNK 21 ── li_auto_l7_zh_3ea4b66a  Off-road damage / emergency braking
add("li_auto_l7_zh_3ea4b66a",
"www.carobook.com",
"""

● Vehicle becomes stuck, e.g., on a high curb or unpaved road.
● Driving over obstacles at excessive speed, e.g., curbs, speed bumps, or potholes.
● Heavy objects striking the undercarriage or chassis components.
In such situations, the body, undercarriage, chassis components, wheels, or tires may suffer invisible damage. Components that have suffered such damage may fail unexpectedly or fail to withstand expected stress in an accident.
If the underbody protection panel is damaged, leaves, grass, or twigs may accumulate between the vehicle underside and the panel. If these materials come into contact with the hot exhaust system components, a fire may result.
In such situations, immediately go to a Li Auto Service Center for vehicle inspection and repair. If you notice compromised driving safety while continuing to drive, immediately find a safe location to stop, paying attention to road and traffic conditions. In such cases, consult the Li Auto Customer Service Center.
When driving off-road, sand, mud, water, or oil-water mixtures may enter the brakes. This may cause reduced braking effectiveness or complete brake failure due to increased wear. Braking characteristics will vary depending on the substances that have entered the brakes. Clean the brakes after off-road driving. If you notice reduced braking effectiveness or hear harsh noises, immediately go to a Li Auto Service Center for brake system inspection. Adjust driving style according to the different braking characteristics.
Off-road driving increases the likelihood of vehicle damage, which may lead to component or system failure. Immediately go to a Li Auto Service Center to repair the damaged areas. Adjust driving style according to the terrain. Drive with caution.
IV. Safe Braking
When emergency braking is needed, firmly press and hold the brake pedal.
V. Long Downhill Grades
Holding the brake pedal for an extended period, even with light pressure, will cause the braking device to overheat and wear, and may even result in failure leading to an accident.
Do not drive in Neutral (N) or with the powertrain off and rely on vehicle momentum, as this will result in no brake assist or steering assist and increases the risk of accidents.
VI. Driving in Rain
Driving in rain frequently involves poor visibility, fogged glass, and slippery road surfaces — drive with caution.
Driving Scenario
2202""",
"www.carobook.com",
"""

● Автомобиль застрял, например, на высоком бордюре или грунтовой дороге.
● Проезд через препятствия на чрезмерной скорости, например бордюры, лежачие полицейские или ямы.
● Тяжёлые предметы, ударяющие в днище или компоненты шасси.
В таких ситуациях кузов, днище, компоненты шасси, колёса или шины могут получить невидимые повреждения. Компоненты, получившие такие повреждения, могут неожиданно выйти из строя или не выдержать ожидаемой нагрузки в аварии.
Если защитная панель днища повреждена, листья, трава или ветки могут накапливаться между днищем автомобиля и панелью. Если эти материалы соприкоснутся с горячими компонентами системы выпуска, может возникнуть пожар.
В таких ситуациях немедленно обратитесь в сервисный центр Li Auto для проверки и ремонта. Если при продолжении движения вы замечаете нарушение безопасности вождения, немедленно найдите безопасное место для остановки, обращая внимание на дорожные условия и движение. В таких случаях обратитесь в центр обслуживания клиентов Li Auto.
При движении по бездорожью песок, грязь, вода или смеси масла с водой могут попасть в тормоза. Это может привести к снижению эффективности торможения или полному отказу тормозов из-за усиленного износа. Тормозные характеристики будут варьироваться в зависимости от попавшего в тормоза вещества. После езды по бездорожью очистите тормоза. Если вы замечаете снижение эффективности торможения или слышите резкий шум, немедленно обратитесь в сервисный центр Li Auto. Скорректируйте стиль вождения в соответствии с различными тормозными характеристиками.
Движение по бездорожью увеличивает вероятность повреждения автомобиля, что может привести к отказу агрегатов или систем. Немедленно обратитесь в сервисный центр Li Auto для ремонта повреждённых частей. Скорректируйте стиль вождения в соответствии с условиями рельефа. Соблюдайте осторожность.
IV. Безопасное торможение
При необходимости экстренного торможения крепко нажмите и удерживайте педаль тормоза.
V. Длинные спуски
Длительное удерживание педали тормоза, даже с лёгким давлением, вызовет перегрев, износ и возможный отказ тормозного устройства, что может привести к аварии.
Не движитесь в режиме нейтраль (N) или с выключенной силовой установкой, полагаясь на инерцию автомобиля, так как это исключает усилитель тормозов и рулевого управления и повышает риск аварии.
VI. Вождение в дождь
Вождение в дождь часто сопровождается плохой видимостью, запотеванием стёкол и скользкими дорогами — соблюдайте осторожность.
Сценарий использования
2202""")

# ── CHUNK 22 ── li_auto_l7_zh_3ee9b34b  CRBS / HHC / energy recovery
add("li_auto_l7_zh_3ee9b34b",
"CRBS Coordinated Regenerative Braking System",
"""CRBS Coordinated Regenerative Braking System

Note
During Hill Descent Control activation, the braking system temperature continuously rises due to friction. When the temperature reaches a certain value, the function will temporarily lose effectiveness and the vehicle may show signs of acceleration. At this point, the driver should pull over to a safe area. The Hill Descent Control system will reactivate once the braking system temperature decreases.
HHC Hill Start Assist
When the vehicle is on a slope (D gear when facing uphill; R gear when facing downhill) and the Auto Hold function is not activated, after pressing the brake pedal to stop the vehicle and releasing it, the braking system will automatically maintain braking force for 1.5 seconds; when the accelerator pedal is pressed, the braking force decreases accordingly to provide sufficient time for a smooth start.
Warning
The Hill Start Assist system can only prevent the vehicle from rolling for a short time; the driver should drive carefully to avoid prolonged situations causing the vehicle to roll.
CRBS Coordinated Regenerative Braking System
When the vehicle brakes, the Coordinated Regenerative Braking System (CRBS) automatically controls the front and rear motors to perform energy recovery. CRBS achieves both energy recovery and provides a certain amount of electric braking force.
When the vehicle is in Adaptive Cruise mode: when the vehicle stability system determines braking is needed, the CRBS is activated first to provide electric braking; if electric braking is insufficient, hydraulic braking is added.
Energy Recovery
In the center console screen settings, tap "Vehicle", select "Driving", tap the options under "Energy Recovery" to set the energy recovery level.
This vehicle provides three energy recovery levels — "Comfort, Standard, Strong" — which can be switched according to your driving habits.
Driving Scenario""",
"CRBS Координируемая рекуперативная тормозная система",
"""CRBS Координируемая рекуперативная тормозная система

Примечание
Во время работы системы помощи при спуске температура тормозной системы постоянно растёт из-за трения. Когда температура достигает определённого значения, функция временно теряет эффективность и автомобиль может начать ускоряться. В этом случае водитель должен съехать на безопасную обочину. Система помощи при спуске повторно активируется после снижения температуры тормозной системы.
HHC Помощь при старте на подъёме
Когда автомобиль находится на уклоне (передача D при движении носом вверх; передача R при движении носом вниз) и функция автоматического удержания не активирована, после нажатия педали тормоза для остановки и её отпускания тормозная система автоматически поддерживает тормозное усилие в течение 1,5 секунды; при нажатии педали акселератора тормозное усилие соответственно снижается для обеспечения достаточного времени для плавного старта.
Предупреждение
Система помощи при старте на подъёме может предотвратить откат автомобиля только на короткое время; водитель должен ехать осторожно, чтобы избежать продолжительных ситуаций, вызывающих откат.
CRBS Координируемая рекуперативная тормозная система
При торможении автомобиля координируемая рекуперативная тормозная система (CRBS) автоматически управляет передним и задним электродвигателями для рекуперации энергии. CRBS обеспечивает как рекуперацию энергии, так и определённое электрическое тормозное усилие.
Когда автомобиль находится в режиме адаптивного круиз-контроля: когда система стабилизации автомобиля определяет необходимость торможения, сначала активируется CRBS для обеспечения электрического торможения; если электрического торможения недостаточно, добавляется гидравлическое торможение.
Рекуперация энергии
В настройках центрального экрана нажмите «Автомобиль», выберите «Вождение», нажмите параметры в разделе «Рекуперация энергии» для установки уровня рекуперации.
Автомобиль предоставляет три уровня рекуперации энергии — «Комфортный, Стандартный, Сильный» — которые можно переключать в соответствии с привычками вождения.
Сценарий использования""")

# ── CHUNK 23 ── li_auto_l7_zh_3ef780bf  FCW + speed limit limitations
add("li_auto_l7_zh_3ef780bf",
"Forward Collision Warning",
"""Forward Collision Warning

II. Functional Limitations
The following situations may prevent the speed limit reminder function from fully functioning or may provide inaccurate information, including but not limited to:
● Incorrect speed limit information or road data stored in the onboard map.
● Lane speed limit information that changes based on time and date.
● Areas not covered by the onboard map.
Note
● Speed limit and speed camera information is for reference only; please follow actual road information and drive safely.
● In non-navigation mode, speed limit information accuracy is lower than in navigation mode.
Forward Collision Warning
When the vehicle speed is between 30 km/h and 75 km/h and the vehicle detects a stationary car or truck ahead with a collision risk, or when the vehicle speed is between 30 km/h and 120 km/h and the vehicle detects a moving car or truck ahead with a collision risk, or when the vehicle speed is between 30 km/h and 80 km/h and the vehicle detects a pedestrian, motorcycle, or bicycle ahead with a collision risk, the system will issue visual and audible warnings to alert the driver. The warning will automatically cancel once the forward collision risk decreases.
I. Settings
In the center console screen settings, tap "Smart Driving", select "Active Safety", tap the options under "Forward Collision Warning" to configure the function.
● Select "Off" to disable Forward Collision Warning. When disabled, no warning will be issued when there is a forward collision risk.
● Select "Near, Medium, Far" to choose the sensitivity of Forward Collision Warning and simultaneously enable the function.
Driving Scenario


Note
● The Forward Collision Warning function is enabled by default when the vehicle is powered on, with the sensitivity set to the most recently configured level.
● Before changing function settings, ensure the vehicle is in a safe area with the gear in Park (P).
● For best effectiveness, the "Far" option is recommended.
II. Alert Information
When there is a forward collision risk, the center console screen displays "Forward Collision Danger" along with an alarm sound.
Driving Scenario


III. Functional Limitations
In the following situations, Forward Collision Warning may be limited or unable to operate normally, including but not limited to:
● The function will not trigger when vehicle speed is below 30 km/h.
● The system cannot issue warnings for stationary obstacles on the road (e.g., traffic cones, guardrails, guide signs).
● Due to radar recognition angle and functional limitations, low-profile objects or obstacles at close range ahead of the vehicle may not be recognized.
● The system cannot warn about oncoming or crossing vehicles, or vehicles in adjacent lanes crossing the lane line.
● When the relative speed difference with the vehicle ahead is large, or when the vehicle ahead suddenly brakes, the system may not issue a timely warning.
● For vehicles cutting in at close range or merging rapidly into this lane, the function trigger may be delayed.
● For targets only detectable after this vehicle changes lanes, the system may not issue a timely warning.
● For targets in curves, system detection performance is limited and the function may not trigger.
● For targets with small radar reflection such as pedestrians, bicycles, and motorcycles, the function may not trigger.
● Camera imaging capability is affected, including but not limited to:
◆ Poor visibility due to nighttime conditions.
◆ Poor visibility due to adverse weather (e.g., heavy rain, heavy snow, heavy fog, sandstorms).
◆ Strong light, backlighting, water reflections, extreme light contrast.
Driving Scenario


◆ Camera obstructed by mud, ice, snow, etc.
◆ Degraded camera performance due to extreme heat or cold.
● Millimeter-wave radar detection capability is affected, including but not limited to:
◆ Radar affected by surrounding environment (e.g., electromagnetic interference, underground parking, tunnels, railway tracks, construction zones, width/height restriction frames).
◆ Radar obstructed by mud, ice, snow, etc.
◆ Degraded radar performance due to extreme heat or cold.
● LiDAR detection capability is affected, including but not limited to:
◆ Adverse weather such as rain, snow, haze, sandstorms.
◆ Direct strong light, backlighting, or water reflections.
◆ Exhaust, splashing water, snowflakes, or dust kicked up by vehicles ahead.
◆ Extreme heat or cold weather conditions.
◆ LiDAR transceiver window obstructed by rain, mud, ice, frost, snow, or window film.
◆ LiDAR transceiver window damaged by external force, showing scratches or cracks.
Warning
● Forward Collision Warning is a driving assistance function and must never replace the driver's observation and judgment of traffic conditions, nor the driver's responsibility for safe vehicle operation.
● The driver holds the highest priority for vehicle control. Forward Collision Warning may stop issuing alerts when the driver quickly turns the steering wheel or presses the brake pedal to avoid interfering with driver operations.
● Drivers must not become overly reliant on Forward Collision Warning, must not intentionally test or wait for function triggering. Due to inherent system limitations, false triggers and missed triggers cannot be completely avoided.
● Before driving, always confirm that there are no low-profile obstacles affecting safety around the vehicle to avoid related accidents caused by obstructed sightlines.
● When Forward Collision Warning is triggered, the driver must immediately assess the road situation and determine whether braking measures are necessary.
● Due to complex real-time traffic, road, and weather conditions, radar and cameras cannot ensure correct detection under all conditions. If radar or cameras fail to detect a forward obstacle, Forward Collision Warning will not be triggered.
Driving Scenario""",
"Предупреждение о лобовом столкновении",
"""Предупреждение о лобовом столкновении

II. Ограничения функции
Следующие ситуации могут помешать полной работе функции напоминания об ограничении скорости или привести к предоставлению неточной информации, включая, но не ограничиваясь:
● Неверная информация об ограничении скорости или данные о дорогах, хранящиеся в навигационной карте.
● Информация об ограничении скорости на полосе, изменяющаяся в зависимости от времени и даты.
● Районы, не охваченные навигационной картой.
Примечание
● Информация об ограничении скорости и камерах является справочной; руководствуйтесь фактической дорожной информацией и соблюдайте безопасность вождения.
● В режиме без навигации точность информации об ограничении скорости ниже, чем в режиме навигации.
Предупреждение о лобовом столкновении
Когда скорость автомобиля составляет от 30 км/ч до 75 км/ч и автомобиль обнаруживает стоящий легковой автомобиль или грузовик впереди с риском столкновения, или когда скорость от 30 км/ч до 120 км/ч и обнаружен движущийся легковой автомобиль или грузовик с риском столкновения, или когда скорость от 30 км/ч до 80 км/ч и обнаружен пешеход, мотоцикл или велосипед с риском столкновения, система выдаёт визуальное и звуковое предупреждение. Предупреждение автоматически отменяется после снижения риска лобового столкновения.
I. Настройки
В настройках центрального экрана нажмите «Интеллектуальное вождение», выберите «Активная безопасность», нажмите параметры в разделе «Предупреждение о лобовом столкновении» для настройки функции.
● Выберите «Выкл.» для отключения функции. При отключении предупреждения при риске лобового столкновения не выдаются.
● Выберите «Близко, Средне, Далеко» для выбора чувствительности и одновременного включения функции.
Сценарий использования


Примечание
● Функция предупреждения о лобовом столкновении включена по умолчанию при включении питания автомобиля с чувствительностью, установленной при последней конфигурации.
● Перед изменением настроек функции убедитесь, что автомобиль находится в безопасной зоне с переключателем в положении P (парковка).
● Для наибольшей эффективности рекомендуется выбрать «Далеко».
II. Информация об оповещении
При риске лобового столкновения центральный экран отображает «Опасность лобового столкновения» вместе со звуковым сигналом.
Сценарий использования


III. Ограничения функции
В следующих ситуациях функция предупреждения о лобовом столкновении может быть ограничена или не работать нормально, включая, но не ограничиваясь:
● Функция не срабатывает при скорости ниже 30 км/ч.
● Система не может выдавать предупреждения о стационарных препятствиях на дороге (например, конусы, ограждения, знаки).
● Из-за угла обнаружения радара и функциональных ограничений малогабаритные объекты или препятствия вблизи передней части автомобиля могут не распознаваться.
● Система не может предупреждать о встречных или пересекающих дорогу транспортных средствах или транспортных средствах в соседних полосах, выезжающих на линию разметки.
● Когда разница относительных скоростей с впереди идущим автомобилем велика или когда впереди идущий автомобиль резко тормозит, система может не выдать своевременное предупреждение.
● Для транспортных средств, резко вклинивающихся или быстро перестраивающихся в эту полосу, срабатывание может быть задержано.
● Для объектов, обнаруживаемых только после смены полосы данным автомобилем, система может не выдать своевременное предупреждение.
● Для объектов на изогнутых дорогах производительность обнаружения ограничена, и функция может не срабатывать.
● Для объектов с малым радиолокационным отражением, таких как пешеходы, велосипеды и мотоциклы, функция может не срабатывать.
● Нарушение работы камеры, включая, но не ограничиваясь:
◆ Плохая видимость из-за ночного времени.
◆ Плохая видимость из-за неблагоприятных погодных условий (сильный дождь, снег, туман, песчаные бури).
◆ Яркий свет, контровой свет, отражения от воды, экстремальный световой контраст.
Сценарий использования


◆ Камера заблокирована грязью, льдом, снегом и т.д.
◆ Снижение производительности камеры из-за экстремального тепла или холода.
● Нарушение работы миллиметрового радара, включая, но не ограничиваясь:
◆ Радар подвержен влиянию окружающей среды (электромагнитные помехи, подземные парковки, тоннели, железнодорожные пути, строительные зоны, ограничения ширины/высоты).
◆ Радар заблокирован грязью, льдом, снегом и т.д.
◆ Снижение производительности радара из-за экстремального тепла или холода.
● Нарушение работы лидара, включая, но не ограничиваясь:
◆ Неблагоприятные погодные условия: дождь, снег, смог, песчаные бури.
◆ Прямой яркий свет, контровой свет или отражения от воды.
◆ Выхлоп, брызги воды, снежинки или пыль от впередиидущих транспортных средств.
◆ Экстремальные погодные условия: жара или холод.
◆ Приёмо-передающее окно лидара заблокировано дождём, грязью, льдом, инеем, снегом или плёнкой на стекле.
◆ Приёмо-передающее окно лидара повреждено внешней силой, имеются царапины или трещины.
Предупреждение
● Предупреждение о лобовом столкновении является функцией помощи при вождении и никогда не должно заменять наблюдение и суждение водителя о дорожной обстановке.
● Водитель имеет наивысший приоритет управления автомобилем. Предупреждение о лобовом столкновении может прекратить выдачу сигналов при быстром повороте руля или нажатии педали тормоза водителем, чтобы не мешать его действиям.
● Водители не должны чрезмерно полагаться на эту функцию, намеренно проверять или ожидать её срабатывания. Из-за неотъемлемых ограничений системы ложные и пропущенные срабатывания не могут быть полностью исключены.
● Перед началом движения всегда проверяйте, нет ли малогабаритных препятствий вокруг автомобиля, влияющих на безопасность.
● При срабатывании предупреждения водитель должен немедленно оценить дорожную ситуацию и определить, необходимо ли торможение.
● Из-за сложных условий реального дорожного движения, дороги и погоды радар и камеры не могут гарантировать правильное обнаружение во всех условиях. Если радар или камеры не обнаруживают препятствие впереди, предупреждение не будет выдано.
Сценарий использования""")

# Save
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"Saved {len(results)} entries (chunks 0-23 translated)")
