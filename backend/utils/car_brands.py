"""
═══════════════════════════════════════════════════════════════════════════════
                    БАЗА ДАННЫХ МАРОК АВТОМОБИЛЕЙ
═══════════════════════════════════════════════════════════════════════════════

Содержит ключевые слова для определения марки авто по названию файла.
Добавляйте новые марки по образцу.
"""

CAR_BRANDS = {
    # ═══════════════════════════════════════════════════════════════════════
    # НЕМЕЦКИЕ
    # ═══════════════════════════════════════════════════════════════════════
    'BMW': {
        'keywords': ['bmw', 'бмв'],
        'models': ['e30', 'e34', 'e36', 'e38', 'e39', 'e46', 'e53', 'e60', 'e65', 'e70', 'e87', 'e90', 'f10', 'f15', 'f20', 'f30', 'g20', 'g30', 'x1', 'x3', 'x5', 'x6', 'x7'],
    },
    'Mercedes-Benz': {
        'keywords': ['mercedes', 'мерседес', 'benz', 'mb '],
        'models': ['w124', 'w140', 'w163', 'w202', 'w203', 'w204', 'w205', 'w210', 'w211', 'w212', 'w220', 'w221', 'w222', 'a-class', 'b-class', 'c-class', 'e-class', 's-class', 'g-class', 'ml', 'gl', 'gle', 'gls', 'glc', 'cls', 'amg'],
    },
    'Audi': {
        'keywords': ['audi', 'ауди'],
        'models': ['a1', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'q2', 'q3', 'q5', 'q7', 'q8', 'tt', 'r8', 'rs', 'e-tron'],
    },
    'Volkswagen': {
        'keywords': ['volkswagen', 'vw', 'фольксваген'],
        'models': ['polo', 'поло', 'golf', 'гольф', 'jetta', 'джетта', 'passat', 'пассат', 'tiguan', 'тигуан', 'touareg', 'туарег', 'touran', 'caddy', 'transporter', 't4', 't5', 't6', 'amarok', 'arteon', 'id.3', 'id.4'],
    },
    'Porsche': {
        'keywords': ['porsche', 'порше'],
        'models': ['911', 'cayenne', 'каен', 'panamera', 'панамера', 'macan', 'макан', 'boxster', 'cayman', 'taycan'],
    },
    'Opel': {
        'keywords': ['opel', 'опель'],
        'models': ['astra', 'астра', 'vectra', 'вектра', 'insignia', 'инсигния', 'zafira', 'зафира', 'corsa', 'корса', 'mokka', 'мокка', 'antara', 'omega'],
    },

    # ═══════════════════════════════════════════════════════════════════════
    # ЯПОНСКИЕ
    # ═══════════════════════════════════════════════════════════════════════
    'Toyota': {
        'keywords': ['toyota', 'тойота'],
        'models': ['camry', 'камри', 'corolla', 'королла', 'rav4', 'рав4', 'land cruiser', 'ленд крузер', 'prado', 'прадо', 'highlander', 'хайлендер', 'yaris', 'auris', 'avensis', 'hilux', 'fortuner', 'sequoia', 'tundra', 'tacoma', '4runner', 'sienna', 'venza', 'c-hr', 'supra', 'mark', 'crown', 'camry', 'alphard', 'harrier'],
    },
    'Lexus': {
        'keywords': ['lexus', 'лексус'],
        'models': ['es', 'gs', 'is', 'ls', 'rx', 'nx', 'lx', 'gx', 'ux', 'ct', 'rc', 'lc'],
    },
    'Honda': {
        'keywords': ['honda', 'хонда'],
        'models': ['civic', 'сивик', 'accord', 'аккорд', 'cr-v', 'crv', 'hr-v', 'pilot', 'пилот', 'fit', 'jazz', 'city', 'odyssey', 'element', 'legend', 'prelude', 'integra', 's2000'],
    },
    'Nissan': {
        'keywords': ['nissan', 'ниссан'],
        'models': ['qashqai', 'кашкай', 'x-trail', 'xtrail', 'pathfinder', 'патфайндер', 'murano', 'мурано', 'teana', 'теана', 'almera', 'альмера', 'note', 'juke', 'жук', 'tiida', 'sentra', 'maxima', 'altima', 'patrol', 'навара', 'titan', 'armada', 'rogue', 'kicks', 'leaf', '350z', '370z', 'gt-r', 'skyline', 'primera', 'sunny', 'micra'],
    },
    'Mazda': {
        'keywords': ['mazda', 'мазда'],
        'models': ['mazda2', 'mazda3', 'mazda5', 'mazda6', 'cx-3', 'cx-30', 'cx-5', 'cx-7', 'cx-9', 'mx-5', 'miata', 'rx-7', 'rx-8', 'bt-50', '323', '626', 'demio', 'atenza', 'axela'],
    },
    'Mitsubishi': {
        'keywords': ['mitsubishi', 'митсубиси', 'мицубиси'],
        'models': ['outlander', 'аутлендер', 'pajero', 'паджеро', 'lancer', 'лансер', 'asx', 'eclipse', 'эклипс', 'l200', 'galant', 'carisma', 'colt', 'grandis', 'evo', 'evolution', '3000gt', 'delica'],
    },
    'Subaru': {
        'keywords': ['subaru', 'субару'],
        'models': ['forester', 'форестер', 'outback', 'аутбек', 'impreza', 'импреза', 'legacy', 'легаси', 'xv', 'crosstrek', 'wrx', 'sti', 'brz', 'tribeca', 'ascent', 'levorg'],
    },
    'Suzuki': {
        'keywords': ['suzuki', 'сузуки'],
        'models': ['vitara', 'витара', 'grand vitara', 'sx4', 'jimny', 'джимни', 'swift', 'свифт', 'ignis', 'baleno', 'liana', 'escudo', 'samurai', 'xl7', 's-cross'],
    },

    # ═══════════════════════════════════════════════════════════════════════
    # КОРЕЙСКИЕ
    # ═══════════════════════════════════════════════════════════════════════
    'Hyundai': {
        'keywords': ['hyundai', 'хендай', 'хундай', 'хёндай'],
        'models': ['solaris', 'солярис', 'creta', 'крета', 'tucson', 'туссан', 'santa fe', 'санта фе', 'elantra', 'элантра', 'sonata', 'соната', 'accent', 'акцент', 'i10', 'i20', 'i30', 'i40', 'ix35', 'kona', 'venue', 'palisade', 'ioniq', 'veloster', 'genesis', 'grandeur', 'getz', 'matrix', 'starex', 'porter'],
    },
    'Kia': {
        'keywords': ['kia', 'киа'],
        'models': ['rio', 'рио', 'ceed', 'сид', 'sportage', 'спортейдж', 'sorento', 'соренто', 'optima', 'оптима', 'cerato', 'церато', 'seltos', 'селтос', 'soul', 'соул', 'stinger', 'стингер', 'telluride', 'mohave', 'carnival', 'niro', 'picanto', 'пиканто', 'k5', 'k7', 'forte', 'spectra', 'magentis'],
    },
    'Genesis': {
        'keywords': ['genesis', 'генезис'],
        'models': ['g70', 'g80', 'g90', 'gv60', 'gv70', 'gv80'],
    },

    # ═══════════════════════════════════════════════════════════════════════
    # АМЕРИКАНСКИЕ
    # ═══════════════════════════════════════════════════════════════════════
    'Ford': {
        'keywords': ['ford', 'форд'],
        'models': ['focus', 'фокус', 'mondeo', 'мондео', 'fusion', 'фьюжн', 'kuga', 'куга', 'escape', 'эскейп', 'explorer', 'эксплорер', 'fiesta', 'фиеста', 'mustang', 'мустанг', 'f-150', 'f150', 'ranger', 'рейнджер', 'bronco', 'expedition', 'edge', 'taurus', 'transit', 'транзит', 'galaxy', 's-max', 'c-max', 'ecosport', 'puma', 'maverick'],
    },
    'Chevrolet': {
        'keywords': ['chevrolet', 'шевроле', 'chevy'],
        'models': ['cruze', 'круз', 'lacetti', 'лачетти', 'aveo', 'авео', 'captiva', 'каптива', 'niva', 'нива', 'tahoe', 'тахо', 'suburban', 'traverse', 'equinox', 'trailblazer', 'blazer', 'colorado', 'silverado', 'camaro', 'камаро', 'corvette', 'корвет', 'malibu', 'impala', 'spark', 'cobalt', 'orlando', 'trax', 'bolt', 'volt', 'lanos', 'nexia'],
    },
    'Jeep': {
        'keywords': ['jeep', 'джип'],
        'models': ['grand cherokee', 'гранд чероки', 'cherokee', 'чероки', 'wrangler', 'рэнглер', 'compass', 'компас', 'renegade', 'ренегат', 'gladiator', 'patriot', 'liberty', 'commander'],
    },
    'Dodge': {
        'keywords': ['dodge', 'додж'],
        'models': ['ram', 'рам', 'charger', 'чарджер', 'challenger', 'челленджер', 'durango', 'journey', 'caravan', 'nitro', 'caliber', 'avenger', 'dart', 'viper', 'neon'],
    },
    'Cadillac': {
        'keywords': ['cadillac', 'кадиллак'],
        'models': ['escalade', 'эскалейд', 'cts', 'ats', 'xts', 'ct4', 'ct5', 'ct6', 'xt4', 'xt5', 'xt6', 'srx'],
    },
    'Tesla': {
        'keywords': ['tesla', 'тесла'],
        'models': ['model s', 'model 3', 'model x', 'model y', 'roadster', 'cybertruck'],
    },

    # ═══════════════════════════════════════════════════════════════════════
    # ФРАНЦУЗСКИЕ
    # ═══════════════════════════════════════════════════════════════════════
    'Renault': {
        'keywords': ['renault', 'рено'],
        'models': ['duster', 'дастер', 'logan', 'логан', 'sandero', 'сандеро', 'kaptur', 'каптюр', 'arkana', 'аркана', 'megane', 'меган', 'fluence', 'флюенс', 'clio', 'клио', 'scenic', 'сценик', 'koleos', 'koleos', 'kadjar', 'каджар', 'talisman', 'laguna', 'лагуна', 'symbol', 'kangoo', 'кангу', 'master', 'мастер', 'trafic', 'трафик'],
    },
    'Peugeot': {
        'keywords': ['peugeot', 'пежо'],
        'models': ['206', '207', '208', '2008', '301', '307', '308', '3008', '408', '508', '5008', 'partner', 'партнер', 'expert', 'эксперт', 'boxer', 'боксер', 'rifter'],
    },
    'Citroen': {
        'keywords': ['citroen', 'ситроен', 'ситроэн'],
        'models': ['c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c8', 'berlingo', 'берлинго', 'jumpy', 'джампи', 'jumper', 'ds3', 'ds4', 'ds5', 'ds7', 'c3 aircross', 'c5 aircross', 'cactus'],
    },

    # ═══════════════════════════════════════════════════════════════════════
    # БРИТАНСКИЕ
    # ═══════════════════════════════════════════════════════════════════════
    'Land Rover': {
        'keywords': ['land rover', 'ленд ровер', 'landrover'],
        'models': ['range rover', 'рендж ровер', 'range rover sport', 'velar', 'велар', 'evoque', 'эвок', 'discovery', 'дискавери', 'freelander', 'фрилендер', 'defender', 'дефендер'],
    },
    'Jaguar': {
        'keywords': ['jaguar', 'ягуар'],
        'models': ['xe', 'xf', 'xj', 'f-pace', 'f-type', 'e-pace', 'i-pace', 'xk', 's-type', 'x-type'],
    },
    'Mini': {
        'keywords': ['mini', 'мини'],
        'models': ['cooper', 'купер', 'one', 'clubman', 'клабмен', 'countryman', 'кантримен', 'paceman', 'cabrio'],
    },

    # ═══════════════════════════════════════════════════════════════════════
    # ДРУГИЕ ЕВРОПЕЙСКИЕ
    # ═══════════════════════════════════════════════════════════════════════
    'Volvo': {
        'keywords': ['volvo', 'вольво'],
        'models': ['xc40', 'xc60', 'xc70', 'xc90', 's40', 's60', 's70', 's80', 's90', 'v40', 'v50', 'v60', 'v70', 'v90', 'c30', 'c70'],
    },
    'Skoda': {
        'keywords': ['skoda', 'шкода'],
        'models': ['octavia', 'октавия', 'rapid', 'рапид', 'superb', 'суперб', 'kodiaq', 'кодиак', 'karoq', 'карок', 'fabia', 'фабия', 'scala', 'скала', 'kamiq', 'yeti', 'йети', 'roomster', 'felicia', 'enyaq'],
    },
    'Fiat': {
        'keywords': ['fiat', 'фиат'],
        'models': ['500', 'panda', 'панда', 'punto', 'пунто', 'tipo', 'типо', 'bravo', 'браво', 'doblo', 'добло', 'ducato', 'дукато', 'linea', 'линеа', 'albea', 'альбеа', 'stilo'],
    },
    'Alfa Romeo': {
        'keywords': ['alfa romeo', 'альфа ромео', 'alfa'],
        'models': ['giulia', 'джулия', 'stelvio', 'стельвио', 'giulietta', 'джульетта', '159', '156', '147', 'mito', 'мито', '4c', 'brera', 'spider', 'tonale'],
    },
    'Seat': {
        'keywords': ['seat', 'сеат'],
        'models': ['leon', 'леон', 'ibiza', 'ибица', 'ateca', 'атека', 'arona', 'арона', 'tarraco', 'toledo', 'altea', 'alhambra'],
    },

    # ═══════════════════════════════════════════════════════════════════════
    # КИТАЙСКИЕ
    # ═══════════════════════════════════════════════════════════════════════
    'Chery': {
        'keywords': ['chery', 'чери'],
        'models': ['tiggo', 'тигго', 'tiggo 2', 'tiggo 3', 'tiggo 4', 'tiggo 5', 'tiggo 7', 'tiggo 8', 'arrizo', 'арризо', 'bonus', 'fora', 'amulet', 'qq'],
    },
    'Geely': {
        'keywords': ['geely', 'джили'],
        'models': ['emgrand', 'эмгранд', 'atlas', 'атлас', 'coolray', 'кулрей', 'tugella', 'тугелла', 'okavango', 'monjaro', 'монжаро', 'mk'],
    },
    'Haval': {
        'keywords': ['haval', 'хавал', 'хавейл'],
        'models': ['f7', 'f7x', 'h2', 'h5', 'h6', 'h9', 'jolion', 'джолион', 'dargo', 'дарго', 'm6'],
    },
    'Great Wall': {
        'keywords': ['great wall', 'грейт волл'],
        'models': ['hover', 'ховер', 'h3', 'h5', 'h6', 'wingle', 'вингл', 'poer', 'safe', 'deer'],
    },
    'Changan': {
        'keywords': ['changan', 'чанган'],
        'models': ['cs35', 'cs55', 'cs75', 'cs85', 'cs95', 'uni-t', 'uni-k', 'uni-v', 'eado', 'alsvin'],
    },
    'JAC': {
        'keywords': ['jac', 'джак'],
        'models': ['s2', 's3', 's4', 's5', 's7', 'j2', 'j3', 'j4', 'j5', 't6', 't8'],
    },
    'Lifan': {
        'keywords': ['lifan', 'лифан'],
        'models': ['solano', 'солано', 'x50', 'x60', 'x70', 'myway', 'smily', 'breez', '320', '520', '620'],
    },
    'BYD': {
        'keywords': ['byd', 'бид'],
        'models': ['tang', 'тан', 'han', 'хан', 'song', 'сонг', 'yuan', 'qin', 'seal', 'dolphin', 'atto 3', 'f0', 'f3', 'f6', 's6', 's7'],
    },
    'Exeed': {
        'keywords': ['exeed', 'эксид'],
        'models': ['txl', 'vx', 'lx', 'rx'],
    },
    'Omoda': {
        'keywords': ['omoda', 'омода'],
        'models': ['c5', 's5'],
    },
    'Tank': {
        'keywords': ['tank', 'танк'],
        'models': ['300', '500', '700'],
    },

    # ═══════════════════════════════════════════════════════════════════════
    # РОССИЙСКИЕ
    # ═══════════════════════════════════════════════════════════════════════
    'LADA': {
        'keywords': ['lada', 'лада', 'ваз', 'vaz', 'автоваз'],
        'models': ['vesta', 'веста', 'granta', 'гранта', 'xray', 'х-рей', 'largus', 'ларгус', 'niva', 'нива', 'kalina', 'калина', 'priora', 'приора', '2101', '2102', '2103', '2104', '2105', '2106', '2107', '2108', '2109', '21099', '2110', '2111', '2112', '2113', '2114', '2115', '2170', '2190', '4x4'],
    },
    'UAZ': {
        'keywords': ['uaz', 'уаз'],
        'models': ['patriot', 'патриот', 'hunter', 'хантер', 'pickup', 'пикап', 'profi', 'профи', 'буханка', '469', '452', '3151', '3163'],
    },
    'GAZ': {
        'keywords': ['газ', 'gaz'],
        'models': ['газель', 'gazel', 'gazelle', 'next', 'некст', 'соболь', 'sobol', 'валдай', 'valdai', 'волга', 'volga', '3102', '3110', '31105', '24', '3307', '53', '66'],
    },

    # ═══════════════════════════════════════════════════════════════════════
    # ДРУГИЕ
    # ═══════════════════════════════════════════════════════════════════════
    'Daewoo': {
        'keywords': ['daewoo', 'дэу'],
        'models': ['matiz', 'матиз', 'nexia', 'нексия', 'lanos', 'ланос', 'nubira', 'leganza', 'espero', 'lacetti', 'gentra', 'evanda', 'magnus', 'tacuma', 'rezzo'],
    },
    'Ravon': {
        'keywords': ['ravon', 'равон'],
        'models': ['r2', 'r3', 'r4', 'gentra', 'nexia', 'cobalt', 'matiz'],
    },
    'SsangYong': {
        'keywords': ['ssangyong', 'санг йонг', 'ссангйонг'],
        'models': ['actyon', 'актион', 'kyron', 'кайрон', 'rexton', 'рекстон', 'korando', 'корандо', 'musso', 'tivoli', 'тиволи', 'rodius', 'torres'],
    },
    'Dacia': {
        'keywords': ['dacia', 'дачия'],
        'models': ['logan', 'логан', 'sandero', 'сандеро', 'duster', 'дастер', 'lodgy', 'dokker', 'spring', 'jogger'],
    },
    'Infiniti': {
        'keywords': ['infiniti', 'инфинити'],
        'models': ['q30', 'q50', 'q60', 'q70', 'qx30', 'qx50', 'qx55', 'qx60', 'qx70', 'qx80', 'fx', 'ex', 'jx', 'g25', 'g35', 'g37', 'm35', 'm37'],
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# ТИПЫ ДОКУМЕНТОВ
# ═══════════════════════════════════════════════════════════════════════════════

DOCUMENT_TYPES = {
    'Руководство по ремонту': {
        'keywords': ['ремонт', 'repair', 'workshop', 'service manual', 'сервисное руководство', 'руководство по ремонту', 'shop manual', 'factory service'],
        'priority': 1,
    },
    'Руководство по эксплуатации': {
        'keywords': ['эксплуатация', 'owner', 'владельца', 'пользователя', 'user manual', 'owners manual', 'handbook'],
        'priority': 2,
    },
    'Электросхемы': {
        'keywords': ['электросхем', 'wiring', 'electrical', 'электрик', 'схема', 'ewd', 'circuit'],
        'priority': 3,
    },
    'Каталог запчастей': {
        'keywords': ['каталог', 'catalog', 'parts', 'запчаст', 'epc', 'spare parts', 'microcat'],
        'priority': 4,
    },
    'Кузовной ремонт': {
        'keywords': ['кузов', 'body', 'collision', 'кузовной'],
        'priority': 5,
    },
    'Диагностика': {
        'keywords': ['диагност', 'diagnostic', 'trouble', 'fault', 'ошибк', 'dtc', 'obd'],
        'priority': 6,
    },
    'ТО и обслуживание': {
        'keywords': ['то ', ' то', 'обслуживан', 'maintenance', 'сервис', 'техническое обслуживание', 'регламент'],
        'priority': 7,
    },
    'Общее': {
        'keywords': [],
        'priority': 99,
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# ФУНКЦИИ ОПРЕДЕЛЕНИЯ
# ═══════════════════════════════════════════════════════════════════════════════

def detect_brand(text: str) -> str:
    """Определяет марку автомобиля по тексту"""
    text_lower = text.lower()
    
    best_match = None
    best_score = 0
    
    for brand, data in CAR_BRANDS.items():
        score = 0
        
        # Ключевые слова бренда
        for keyword in data['keywords']:
            if keyword.lower() in text_lower:
                score += 10
        
        # Модели
        for model in data.get('models', []):
            if model.lower() in text_lower:
                score += 5
        
        if score > best_score:
            best_score = score
            best_match = brand
    
    return best_match if best_match else 'Другие марки'


def detect_document_type(text: str) -> str:
    """Определяет тип документа по тексту"""
    text_lower = text.lower()
    
    best_match = 'Общее'
    best_priority = 99
    
    for doc_type, data in DOCUMENT_TYPES.items():
        for keyword in data['keywords']:
            if keyword.lower() in text_lower:
                if data['priority'] < best_priority:
                    best_priority = data['priority']
                    best_match = doc_type
                    break
    
    return best_match


def get_all_brands() -> list:
    """Возвращает список всех марок"""
    return list(CAR_BRANDS.keys())