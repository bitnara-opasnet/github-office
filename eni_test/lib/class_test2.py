# -*- coding: utf-8 -*-

class Car:
    def __init__(self):
        self.carname = 'bmw X5'
        self._type = 'suv'
        self.__manufacture = 'bmw'

car = Car()
# print(car.__manufacture) # 접근 불가

try:
    print(car.carname)
    print(car._type)
    print(car.__manufacture)
except AttributeError as err:
    print(err)

# 정보은닉
class Car2:
    def __init__(self):
        self.carname = 'bmw X5'
        self._type = 'suv'
        self.__manufacture = 'bmw'
    
    # getter
    def get_carmanufacture(self):
        return self.__manufacture

    # setter
    def set_carmanufacture(self, mvalue):
        self.__manufacture = mvalue

# 불러오기
car2 = Car2()
carmanufacture = car2.get_carmanufacture()
print(carmanufacture)

# 수정
car2.set_carmanufacture('ssangyong')
carmanufacture = car2.get_carmanufacture()
print(carmanufacture)


class Car3:
    def __init__(self):
        self.__manufacture = 'bmw'
    
    # getter
    @property
    def manufacture(self):
        return self.__manufacture
    
    # setter
    @manufacture.setter
    def manufacture(self, mvalue):
        if isinstance(mvalue, int):
            raise 'error'
        else:
            self.__manufacture = mvalue

# 불러오기
car3 = Car3()
carmanufacture3 = car3.manufacture
print(carmanufacture3)

# 수정
car3.manufacture = 'ssangyong'
print(car3.manufacture)

try:
    car3.manufacture = 1234
    print(car3.manufacture)
except TypeError as err:
    print(err)