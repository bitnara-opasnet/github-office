# -*- coding: utf-8 -*-

class Car:
    def __init__(self, carname):
        self.carname = carname
    
    def run(self):
        return '{} is running'.format(self.carname)
    
    def stop(self):
        return '{} is stopped'.format(self.carname)

car = Car('BMW')
run_car = car.run()
print(run_car)

class CarRepair(Car):
    def __init__(self, carname, item):
        super().__init__(carname) 
        self.item = item

    def run(self):
        return '{} is running fastly'.format(self.carname)

    def punk(self):
        a = super().stop() # super : 부모 class에 접근과 수정 가능
        return '{} by punk'.format(a)
    
    def repair(self):
        return "{}'s {} was repaired".format(self.carname, self.item)

car_repair = CarRepair('BMW', 'Engine')
run_car1 = car_repair.run()
repair_car = car_repair.repair()
stop_car = car_repair.punk()

print(run_car1)
print(repair_car)
print(stop_car)
