# -*- coding: utf-8 -*-

# Подземелье было выкопано ящеро-подобными монстрами рядом с аномальной рекой, постоянно выходящей из берегов.
# Из-за этого подземелье регулярно затапливается, монстры выживают, но не герои, рискнувшие спуститься к ним в поисках
# приключений.
# Почуяв безнаказанность, ящеры начали совершать набеги на ближайшие деревни. На защиту всех деревень не хватило
# солдат и вас, как известного в этих краях героя, наняли для их спасения.
#
# Карта подземелья представляет собой json-файл под названием rpg.json. Каждая локация в лабиринте описывается объектом,
# в котором находится единственный ключ с названием, соответствующем формату "Location_<N>_tm<T>",
# где N - это номер локации (целое число), а T (вещественное число) - это время,
# которое необходимо для перехода в эту локацию. Например, если игрок заходит в локацию "Location_8_tm30000",
# то он тратит на это 30000 секунд.
# По данному ключу находится список, который содержит в себе строки с описанием монстров а также другие локации.
# Описание монстра представляет собой строку в формате "Mob_exp<K>_tm<M>", где K (целое число) - это количество опыта,
# которое получает игрок, уничтожив данного монстра, а M (вещественное число) - это время,
# которое потратит игрок для уничтожения данного монстра.
# Например, уничтожив монстра "Boss_exp10_tm20", игрок потратит 20 секунд и получит 10 единиц опыта.
# Гарантируется, что в начале пути будет две локации и один монстр
# (то есть в коренном json-объекте содержится список, содержащий два json-объекта, одного монстра и ничего больше).
#
# На прохождение игры игроку дается 123456.0987654321 секунд.
# Цель игры: за отведенное время найти выход ("Hatch")
#
# По мере прохождения вглубь подземелья, оно начинает затапливаться, поэтому
# в каждую локацию можно попасть только один раз,
# и выйти из нее нельзя (то есть двигаться можно только вперед).
#
# Чтобы открыть люк ("Hatch") и выбраться через него на поверхность, нужно иметь не менее 280 очков опыта.
# Если до открытия люка время заканчивается - герой задыхается и умирает, воскрешаясь перед входом в подземелье,
# готовый к следующей попытке (игра начинается заново).
#
# Гарантируется, что искомый путь только один, и будьте аккуратны в рассчетах!
# При неправильном использовании библиотеки decimal человек, играющий с вашим скриптом рискует никогда не найти путь.


import datetime
import json
import re
from decimal import *

from termcolor import cprint

getcontext().prec = 17

remaining_time = '123456.0987654321'
# если изначально не писать число в виде строки - теряется точность!
with open("snippets/rpg.json", "r") as read_file:
    game_file = json.load(read_file)


class Game:

    def __init__(self, in_file):
        self.remaining_time = Decimal('123456.0987654321')
        self.time_after_start = datetime.timedelta(seconds=0)
        self.experience = 0
        self.locations_and_monsters = []
        self.path_game = in_file
        self.path_after_end = in_file
        self.path_to_see = 'Около пещеры'
        self.pattern_time = r'tm\d*.\d*'
        self.pattern_exp = r'_exp\d*'

    def begin_again(self):
        if self.path_game == 'You are winner':
            print('*' * 150)
            print('{:^150}'.format('Вы нашли выход, но вам не хватило очков опыта (не менее 280)'))
            print('{:^150}'.format('Вы не смогли открыть люк. Попробуйте снова!'))
            print('*' * 150)
        elif self.remaining_time <= 0:
            print('*' * 150)
            print('{:^150}'.format('Время закончилось!!!'))
            print('{:^150}'.format('Вы не успели открыть люк!!! НАВОДНЕНИЕ!!!'))
            print('*' * 150)
        elif self.remaining_time > 0:
            print('*' * 150)
            print('{:^150}'.format('Вы пошли не той дорогой! Увы'))
            print('{:^150}'.format('Попробуйтте ещё разок! Выход точно есть!'))
            print('*' * 150)
        self.remaining_time = Decimal(123456.0987654321)
        self.time_after_start = datetime.timedelta(seconds=0)
        self.experience = 0
        self.locations_and_monsters = []
        self.path_game = self.path_after_end
        self.path_to_see = 'Около пещеры'
        self.you_see()

    def read_location(self):
        print('Внутри Вы видите:')
        if isinstance(self.path_game, dict):
            for value in self.path_game.keys():
                if value.startswith('L'):
                    self.locations_and_monsters.append(value)
                    print('Вход в ', value)
                elif value.startwith('M'):
                    self.locations_and_monsters.append(value)
                    print('Монстра', value)
        if isinstance(self.path_game, list):
            for value in self.path_game:
                if isinstance(value, dict):
                    self.locations_and_monsters.append(list(value.keys())[0])
                    print('Вход в ', list(value.keys())[0])
                elif isinstance(value, str):
                    self.locations_and_monsters.append(value)
                    print('Монстра', value)

    def you_see(self, after_monster=0):
        cprint((f'Показатели: Опыт {self.experience}, Время {self.time_after_start}, '
                f'До наводнения {self.remaining_time} секунд'), color='green')
        print(f'Вы находитесь в {self.path_to_see}')
        if after_monster == 0:
            self.read_location()
            self.game_step(step=self.you_do())
        else:
            if len(self.locations_and_monsters) == 0:
                self.begin_again()
            else:
                print('Внутри Вы видите:')
                for choise in self.locations_and_monsters:
                    if str(choise).startswith('L'):
                        print('location - ', choise)
                    elif str(choise).startswith('M'):
                        print('monster - ', choise)
                    elif str(choise).startswith('H'):
                        print('Выход - ', choise)
                self.game_step(step=self.you_do())

    def you_do(self):
        count_do = 0
        cprint('Выберите действие:', color='blue')
        for val in self.locations_and_monsters:
            if str(val).startswith('M'):
                count_do += 1
                cprint(f'{count_do} = > Атаковать монстра {val}', color='blue')
            elif str(val).startswith('L'):
                count_do += 1
                cprint(f'{count_do} = > Перейти в локацию {val}', color='blue')
            elif str(val).startswith('H'):
                count_do += 1
                cprint(f'{count_do} = > Выйти наружу {val}', color='blue')
            elif str(val).startswith('B'):
                count_do += 1
                cprint(f'{count_do} = > Атаковать БОССА {val}', color='blue')
        go_away = count_do + 1
        cprint(f'{go_away} = > Сдаться и выйти из игры', color='blue')
        while True:
            step_choise = input('')
            if not str(step_choise).isdigit() or int(step_choise) not in range(1, count_do + 2):
                print(f'Введено неверное число. Выберите от 1 до {count_do + 1}')
            elif int(step_choise) == go_away:
                print('Никогда не сдавайтесь. В пещере точно есть выход!')
                print('Попробуем снова?')
                step_choise = input('1 - Пробуем снова, 2 - Сдаться. Выбрать: ')
                if int(step_choise) == 1:
                    print('Выбор смельчаков =)')
                    self.remaining_time = Decimal(123456.0987654321)
                    self.time_after_start = datetime.timedelta(seconds=0)
                    self.experience = 0
                    self.locations_and_monsters = []
                    self.path_game = self.path_after_end
                    self.path_to_see = 'Около пещеры'
                    self.you_see()
                else:
                    return False
            else:
                break
        return int(step_choise) - 1

    def game_step(self, step):
        if step is False:
            print('Игра закончена. Пока.')
            return 'End'
        elif str(self.locations_and_monsters[step]).startswith('L'):
            get_time = str(re.search(self.pattern_time, self.locations_and_monsters[step]))[42:-2:]
            location_time = float(get_time)
            self.remaining_time -= Decimal(float(location_time))
            self.time_after_start += datetime.timedelta(seconds=int(location_time))
            if isinstance(self.path_game, dict):
                for choise in self.path_game.keys():
                    if choise == self.locations_and_monsters[step]:
                        self.path_game = self.path_game[choise]
                        self.path_to_see = choise
                        break
            elif isinstance(self.path_game, list):
                count = -1
                for choise in self.path_game:
                    count += 1
                    if isinstance(choise, dict) and list(choise.keys())[0] == self.locations_and_monsters[step]:
                        self.path_game = self.path_game[count][list(choise.keys())[0]]
                        self.path_to_see = self.locations_and_monsters[step]
            self.locations_and_monsters.clear()
            if self.remaining_time < 0:
                self.begin_again()
            else:
                self.you_see(after_monster=0)
        elif str(self.locations_and_monsters[step]).startswith('M') or str(
                self.locations_and_monsters[step]).startswith('B'):
            monster_time = str(re.search(self.pattern_time, self.path_game[step]))[42:-2:]
            self.remaining_time -= Decimal(float(monster_time))
            exp = str(re.findall(self.pattern_exp, self.path_game[step]))[6:-2:]
            self.experience += int(exp)
            self.time_after_start += datetime.timedelta(seconds=int(monster_time))
            self.locations_and_monsters.pop(step)
            if self.remaining_time < 0:
                self.begin_again()
            else:
                self.you_see(after_monster=1)
        elif str(self.locations_and_monsters[step]).startswith('H'):
            get_time = str(re.search(self.pattern_time, self.locations_and_monsters[step]))[41:-2:]
            location_time = float(get_time)
            self.remaining_time -= Decimal(float(location_time))
            self.path_game = 'You are winner'
            if self.experience >= 280 and self.remaining_time > 0:
                print('*' * 150)
                print('{:^150}'.format('ВЫХОД НА СВЕТ!'))
                print('{:^150}'.format('ВЫ ЭТО СДЕЛАЛИ!'))
                print('{:^150}'.format('ВЫ ПОБЕДИТЕЛЬ!'))
                print('*' * 150)
            else:
                self.begin_again()


game = Game(in_file=game_file)
game.you_see()