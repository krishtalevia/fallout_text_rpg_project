import os
import gui
import json
import random


def check_char_directory() -> None:
    if not os.path.isdir('characters'):
        os.makedirs('characters')
        print('\033[5;36m[temp]\033[0m Папки содержащей профили не существовало, папка создана.')


def character_deifne(load_status, char_name) -> bool:
    if load_status == 'new' and os.path.exists(rf'characters/{char_name}.json') == True:
        answer = gui.char_exists()

        if answer == 'rewrite':
            file = open(fr'characters/{char_name}.json', 'w', encoding='utf-8')
            file.close()
            return True
        else:
            return False

    elif load_status == 'new' and os.path.exists(rf'characters/{char_name}.json') == False:
        file = open(fr'characters/{char_name}.json', 'w', encoding='utf-8')
        file.close()
        return True

    elif load_status == 'load' and os.path.exists(rf'characters/{char_name}.json') == False:
        gui.back_button('Персонажа с таким именем не существует')
        return False

    elif load_status == 'load':
        print('Ваш прогресс загружен. %название пути и локации%')
        return True

def perk_define(genesis: str, role: str) -> str:
    if genesis == 'Человек':  # +5 к харизме
        if role == 'Караванщик':
            perk = 'Переговорщик'  # +10 к харизме
        elif role == 'Рейдер':
            perk = 'Адреналин'  # +15 к бонусному урону, если здоровье падает ниже 25

    elif genesis == 'Гуль':  # -15 к харизме, сопротивление к радиации
        if role == 'Караванщик':
            perk = 'Торговец'  # +20 к харизме
        elif role == 'Старатель':
            perk = 'Изыскатель'  # 30% вероятность найти дополнительный предмет

    elif genesis == 'Супермутант':  # отсутствие харизмы, сопротивление к радиации +20 к исходному здоровью
        if role == 'Тень':
            perk = 'Элита'  # +15 к броне
        elif role == 'Странник':
            perk = 'Адаптивность'  # 30% резист к отнимающим здоровье предметам

    return perk


def save_start_profile(char_name, genesis, role, perk) -> None:
    rad_level = 0

    charisma = 25
    if role == 'Переговорщик':
        charisma = 35
    elif genesis == 'Супермутант':
        charisma = 0
    elif role == 'Торговец':
        charisma = 20
    elif role == 'Изыскатель':
        charisma = 5

    armor = 0
    if role == 'Элита':
        armor = 15

    parameters = {'genesis': genesis,
                  'role': role,
                  'perk': perk,
                  'hp': 100 if role == 'Супермутант' else 70,
                  'armor': armor,
                  'damage': 10,
                  'bdamage': 0,
                  'rad_level': rad_level,
                  'charisma': charisma,
                  'inventory': [],
                  'death_count': 0,
                  'kill_count': 0,
                  'room_count': 0,
                  'current_location': 'Начало пути.txt',
                  'road': None}

    with open(rf'characters/{char_name}.json', 'w', encoding='utf-8') as profile:
        json.dump(parameters, profile, ensure_ascii=False)


def print_import_stats(char_name):

    path = rf'characters/{char_name}.json'
    stats = import_data(path)
    gui.print_stats(stats, char_name)

def import_data(path):
    with open(path, 'r', encoding='utf-8') as profile:
        data = json.load(profile)

    return data

def export_player_data(char_name, player_data):
    with open(f'characters/{char_name}.json', 'w', encoding='utf-8') as profile:
        json.dump(player_data, profile, ensure_ascii=False)

def import_dir_list(path: str) -> list:
    return os.listdir(path)

def convert_room_to_events_matrix(road: str, room_name='Начало пути.txt') -> list:
    with open(fr'paths/{road}/{room_name}', 'r', encoding='utf-8') as file:
        room_file = file.read()

    room_lines = room_file.split('|||')

    room = []

    for i in room_lines:
        events = i.split('||')
        choices = events[-1].split('|')
        del events[-1]

        events.append(choices)
        room.append(events)

    return room

def state_of_combat(char_name, player_data, enemy_data):
    move = 'player'

    while True:
        gui.print_state_of_combat(char_name, player_data, enemy_data)

        if move == 'player':
            gui.input_player_attack()

            enemy_data['hp'] -= (player_data['damage'] + player_data['bdamage'])

            if enemy_data['hp'] <= 0:
                player_data['kill_count'] += 1

                player_data = player_get_loot_for_win(enemy_data, player_data)

                return player_data

            move = 'enemy'
            continue
        else:
            gui.print_enemy_attack()

            if player_data['armor'] > 0:
                player_data['armor'] -= enemy_data['damage']
            else:
                player_data['hp'] -= enemy_data['damage']

            if int(player_data['hp']) <= 0:

                return player_data

            else:
                move = 'player'
                continue

def import_item_data(item_name, type_name):
    buff = import_data(f'{type_name}.json')

    if type_name != 'items':
        item_data = buff[item_name]

    else:
        if item_name in buff['Обычные']:
            item_data = buff['Обычные'][item_name]

        elif item_name in buff['Редкие']:
            item_data = buff['Редкие'][item_name]

        elif item_name in buff['Легендарные']:
            item_data = buff['Легендарные'][item_name]

        else:
            item_data = buff['Неизвестный'][item_name]

    return item_data

def use_item(player_data):
    item_name = gui.input_item_for_use(player_data)

    if item_name != 'back':
        item_data = import_item_data(item_name, 'items')
        parameter = item_data['eff_parameter']
        effect = item_data['eff']

        if item_name == 'Неизвестный':
            random_parameter_index = random.randint(0, len(parameter))
            parameter = parameter[random_parameter_index]

            random_effect_index = random.randint(0, len(effect))
            effect = effect[random_effect_index]

        player_data[parameter] += effect

        gui.print_item_use_effect(item_data['eff_description'], item_name, effect, item_data, random_parameter_index)

        for i in range(0, len(player_data['inventory']), 1):
            if player_data['inventory'][i] == f'{item_name}':
                del player_data['inventory'][i]
                return player_data
    else:
        return player_data

def stats_fix(player_data):
    if player_data['bdamage'] < 0:
        player_data['bdamage'] = 0
    elif player_data['armor'] < 0:
        player_data['armor'] = 0
    elif player_data['rad_level'] < 0:
        player_data['rad_level'] = 0

    if player_data['genesis'] == 'Супермутант' or player_data['genesis'] == 'Гуль':
        player_data['rad_level'] = 0

    return player_data

def take_item(item_name, player_data):
    player_data['inventory'].append(item_name)

    gui.print_item_taken(item_name)

    return player_data

def get_random_item_from_category(item_category):
    items = import_data('items.json')

    category_items = list(items[item_category].keys())

    random_item = random.choice(category_items)

    return random_item

def player_get_loot_for_win(enemy_data, player_data, win_by='combat'):

    dice = random.randint(0,100)
    categories = ['Обычные', 'Редкие', 'Легендарные']
    for i in range(0, len(categories), 1):
        if categories[i] == enemy_data['loot'][0]:
            del categories[i]

    if dice < 85:
        random_item_1 = get_random_item_from_category(enemy_data['loot'][0])
    else:
        dice = random.randint(0,1)
        random_item_1 = get_random_item_from_category(categories[dice])

    random_item_2 = get_random_item_from_category(enemy_data['loot'][1])

    if win_by == 'combat':
        item_name = gui.input_loot_choice_for_win(enemy_data, random_item_1, random_item_2)

        if item_name != None:
            player_data['inventory'].append(item_name)
            return player_data
        else:
            return player_data

    else:
        random_loot = random.randint(0,1)

        if random_loot == 1:
            item_name = random_item_1
        else:
            item_name = random_item_2

        answer = gui.input_loot_for_win_by_charisma(item_name)

        if answer == 'yes':
            player_data['inventory'].append(item_name)
            return player_data
        else:
            return player_data

def charisma_check(player_data, enemy_data):
    if player_data['charisma'] > enemy_data['hostility']:
        gui.print_dodged_by_charisma()
        return True
    else:
        gui.failed_charisma()
        return False

def menu(player_data, char_name):
    while True:
        menu_choice = gui.input_menu_choice(player_data, char_name)

        if menu_choice == 'go':
            return player_data, menu_choice

        elif menu_choice == 'use_item':
            if len(player_data['inventory']) == 0:
                gui.inventory_is_empty()
                gui.continue_button()

            else:
                player_data = use_item(player_data)

            continue

        elif menu_choice == 'exit':
            return player_data, menu_choice

def trap(choice, player_data, trap_data):
    eff_parameter = trap_data['eff_parameter']
    eff_parameter_name = trap_data['eff_parameter_name']
    win = trap_data['win']
    eff = trap_data['eff']
    dice = random.randint(1, 100)

    res = 'lose'

    if choice == '1':
        if dice < trap_data['1st chance']:
            player_data[eff_parameter] += eff
        else:
            res = 'win'

    elif choice == '2':
        if dice < trap_data['2nd chance']:
            player_data[eff_parameter] += eff
        else:
            res = 'win'

    elif choice == '3':
        if dice < trap_data['3rd chance']:
            player_data[eff_parameter] += eff
        else:
            res = 'win'

    if res == 'lose':
        gui.print_trap_fail(eff, eff_parameter_name)

    elif res == 'win':
        player_data[win['parameter']] + win['eff']
        gui.print_trap_success(trap_data['is_succ_eff'], win['eff'], win['name'])
        
    return player_data

def location_change(location_name_1, location_name_2, choice, player_data):
    if choice == '1':
        player_data['current_location'] = f'{location_name_1}.txt'
    else:
        player_data['current_location'] = f'{location_name_2}.txt'

    return player_data

def radiation_sickness(player_data):

    if player_data['genesis'] == 'Человек':
        if player_data['rad_level'] > 100:
            gui.print_radiation_sickness()
            player_data['hp'] -= 20

    return player_data

