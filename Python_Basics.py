## Eingabe
# float = Kommazahl (z.b. 2.3)
# int = Ganzzahl (z.b. 2 oder 3)
# bool = Boolscher Operator (True od. False)
# str  = String ("Schrift oder auch Zahlen in Anführungszeichen oder durch Eingabe)

## Funktionen
# input() = returns a string
# print() = Ausgabe von str, int, float, etc.
# float() = Umwandlung in float
# int() = Umwandlung in integer
# bool() = Umwandlung in boolschen operator
# str() = Umwandlung in string

## Funktionen Beispiele
# first = input("First: ")
# second = input("Second: ")
# sum = float(first) + float(second)
#
# print("Sum = " + str(sum)) #can not process string + float -> convert float to string

##Methodes (functions is part of an object (string))
# modifies string without changing initial value
# everytime you modify a string, a new string will be saved
# course = "Tutorial for Python"
#         # 01234567 9
# print(course.upper())
# print(course.lower())
# print(course.find("l"))
# print(course.find("for"))
# print(course.replace("for", "4"))

##Arithmetic operators
# print(4+3) #7
# print(4-3) #1
# print(4*3) #12
# print(4/3) #1.33
# print(4**3) #64

##augmented assignment operator
# x = 10
# x = x+3
# print(x)
# x += 3
# print(x)

## comparison operator (outcome is boolean)
# x = 3 > 2
# y = 3 >= 2
# z = 3 == 2
# s = 3 != 2
# print(x, y, z, s)


## logic operators
# price = 25
# print(price > 10 and price > 30)
# print(price > 10 or price > 30)
# print(not price == 25)

## if clause
# temperature = 30
# if temperature > 30:
#     print("It's a hot day") #shift + tab -> removes indentation
# elif temperature < 10:
#     print("It's a cold day")
# else:
#     print("It's a day")


## Exercise
# weight = input("weight: ")
# unit = input("(k)g or (l)bs: ")
# if unit.upper() == "K":
#     conversion = float(weight) * 2.20462
#     print("Your weight in pounds is " + str(conversion))
# elif unit.upper () == "L":
#     conversion = float(weight) * 0.453592
#     print("Your weight in kilogram is " + str(conversion))
# else:
#     print("No valid input")

## while clause
# x = 0
# while x <= 1_000:
#     print(x)
#     x=x+1

# x = 1
# while x <= 5:
#     print(x * "DAVE ")
#     x=x+1

## lists

# list = ["Dave", "Leo", "Hanna", "Markus"]
# name = list[0]
# print(name.upper())
# print(list[-1])
# list[0]= "Lorena"
# name = list[0]
# print(name.upper())
# print(list[0:3]) #returnes a new list and does not modify list

## methods for lists

# numbers = [1, 2, 3, 4, 5]
# numbers.append(6)
# numbers.insert(0, 0)
# print(numbers)
# numbers.remove(3)
# print(numbers)
# numbers.reverse()
# print(numbers)
# print(1 in numbers) #boolean operator
# print(len(numbers)) #len gives the number of items in a list

## For loop
# list = [1, 2, 3, 4, 5]
# for item in list
#     print(item)

numbers = range(5)
number = range(5,10,2)
print(numbers)
print(number)


for number in number:
    print(number)

## tupels


