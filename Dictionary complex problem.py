#distionary problem  , create a dictionary that maps students names with thir scores write a function that takes dictionary and returns the name of the stusent with the highest score
students={}
for i in range(5):
    name=input("enter name of student :")
    marks=int(input("enter his marks :"))
    students.update({name:marks})

print(students)

def Topper(students):
    topper_name=""
    top_score=-1
    for name,marks in students.items():
        if marks>top_score:
            top_score=marks
            topper_name=name
    return topper_name
print(f'the topper name is {Topper(students)} ')
