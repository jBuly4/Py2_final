from abc import ABC, abstractmethod
import pygame
import random


def create_sprite(img, sprite_size):
    icon = pygame.image.load(img).convert_alpha()
    icon = pygame.transform.scale(icon, (sprite_size, sprite_size))
    sprite = pygame.Surface((sprite_size, sprite_size), pygame.HWSURFACE)
    sprite.blit(icon, (0, 0))
    return sprite


class Interactive(ABC):

    @abstractmethod
    def interact(self, engine, hero):
        for notification in hero.level_up():
            engine.notify(notification)


class Ally(AbstractObject, Interactive):

    def __init__(self, icon, action, position):
        self.sprite = icon
        self.action = action
        self.position = position

    def interact(self, engine, hero):
        self.action(engine, hero)


class Creature(AbstractObject):

    def __init__(self, icon, stats, position):
        self.sprite = icon
        self.stats = stats
        self.position = position
        self.calc_max_HP()
        self.hp = self.max_hp

    def calc_max_HP(self):
        self.max_hp = 5 + self.stats["endurance"] * 2


class Hero(Creature):

    def __init__(self, stats, icon):
        pos = [1, 1]
        self.level = 1
        self.exp = 0
        self.gold = 0
        super().__init__(icon, stats, pos)

    def level_up(self):
        while self.exp >= 100 * (2 ** (self.level - 1)):
            yield "level up!"
            self.level += 1
            self.stats["strength"] += 2
            self.stats["endurance"] += 2
            self.calc_max_HP()
            self.hp = self.max_hp


class Effect(Hero):

    def __init__(self, base):
        self.base = base
        self.stats = self.base.stats.copy()
        self.apply_effect()

    @property
    def position(self):
        return self.base.position

    @position.setter
    def position(self, value):
        self.base.position = value

    @property
    def level(self):
        return self.base.level

    @level.setter
    def level(self, value):
        self.base.level = value

    @property
    def gold(self):
        return self.base.gold

    @gold.setter
    def gold(self, value):
        self.base.gold = value

    @property
    def hp(self):
        return self.base.hp

    @hp.setter
    def hp(self, value):
        self.base.hp = value

    @property
    def max_hp(self):
        return self.base.max_hp

    @max_hp.setter
    def max_hp(self, value):
        self.base.max_hp = value

    @property
    def exp(self):
        return self.base.exp

    @exp.setter
    def exp(self, value):
        self.base.exp = value

    @property
    def sprite(self):
        return self.base.sprite

    @abstractmethod
    def apply_effect(self):
        pass


# FIXME
# add classes

class Berserk(Effect):
    """ Berserk effects:
        increase strength +5
        increase endurance +5
        decrease intelligence -5 """

    def apply_effect(self):
        self.stats["strength"] += 5
        self.stats["endurance"] += 5
        self.stats["intelligence"] -= 5
        return self.stats.copy()


class Blessing(Effect):
    """ Blessing effects: increase all characteristics by 2 """

    def apply_effect(self):
        for key in self.stats:
            self.stats[key] += 2
        return self.stats.copy()


class Weakness(Effect):
    """ Weakness effects: decrease all characteristics by 2 """

    def apply_effect(self):
        for key in self.stats:
            self.stats[key] -= 2
        return self.stats.copy()


class LowXP(Effect):
    """ LowXP effects: when meet enemy with higher XP then luck is decreased by 2 """

    def apply_effect(self):
        self.stats["luck"] -= 2
        return self.stats.copy()


class Enemy(Creature, Interactive):
    """ Enemy is like Ally but hurts """
    def __init__(self, icon, stats, xp, position):
        super().__init__(icon, stats, position)
        self.experience = xp

    def interact(self, engine, hero):
        if self.experience >= hero.stats['experience']:
            hero.stats['luck'] -= 2
        elif self.stats["strength"] >= hero.stats['strength']:
            hero.hp -= (self.stats['strength'] - hero.stats['strength'])
        else:
            hero.hp -= (hero.stats['strength'] - self.stats['strength']) // 2
        if hero.hp <= 0:
            engine.delete_object(hero)

        hero.xp += self.experience // 2
        super().interact(engine, hero)
