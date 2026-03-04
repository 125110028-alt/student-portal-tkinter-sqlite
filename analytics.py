def get_topper(data):
    if not data:
        return "NO DATA FOUND"
    highest_score = 0
    topper_name = ""
    for roll_no, details in data.items():
        if details["Total"] > highest_score:
            highest_score = details["Total"]
            topper_name = details["Name"]
    return topper_name, highest_score

def get_top3_students(data):
    if not data:
        return "NO DATA Found"
    arranged_list=[]
    for roll_no, details in data.items():
        arranged_list.append({("Name"):details["Name"],("Marks"):details["Total"]})
    sorted_list=sorted(arranged_list,key=lambda x: x["Marks"] ,reverse=True)
    return sorted_list[:3]

def calculate_class_average(data):
    if not data:
        return "NO DATA FOUND"
    count=0
    totale=0
    for roll_no,details in data.items():
        totale+=details["Total"]
        count+=1
    return totale/count

def calculate_pass_percentage(data):
    if not data:
        return "NO DATA FOUND"
    passe=0
    fail=0
    failed_students=[]
    for roll_no,details in data.items():
        sub=0
        for i in details.values():
            if type(i) == int and i<40:
                sub+=1
        if sub==0:
            passe+=1
        else: 
            fail+=1
            failed_students.append(details["Name"])
    return passe, fail, failed_students

student_records = {
    "Roll1":{
        "Name":"Aman",
        "ECO":40,
        "DSD":35,
        "Maths":51,
        "DS":18,
        "Python":12,
        "Total":105
    },
    "Roll2":{
        "Name":"Monu",
        "ECO":60,
        "DSD":55,
        "Maths":72,
        "DS":68,
        "Python":74,
        "Total":329
    },
    "Roll3":{
        "Name":"Neha",
        "ECO":70,
        "DSD":75,
        "Maths":85,
        "DS":80,
        "Python":77,
        "Total":387
    },
    "Roll4":{
        "Name":"Priya",
        "ECO":92,
        "DSD":91,
        "Maths":97,
        "DS":95,
        "Python":94,
        "Total":469
    },
    "Roll5":{
        "Name":"Sameer",
        "ECO":85,
        "DSD":70,
        "Maths":90,
        "DS":75,
        "Python":88,
        "Total":408
    }
}
Topper,Topper_score=get_topper(student_records)
print("Topper:", Topper,"-> With highest score:",Topper_score)

top_3_studants=get_top3_students(student_records)
print("Top 3 Students:", top_3_studants)

class_average=calculate_class_average(student_records)
print("Class Average:", class_average)

passe,fail,failed_students= calculate_pass_percentage(student_records)
print("Pass Percentage:",(passe*100)/(passe+fail), "%")
print("Failed students are:",failed_students)

import matplotlib.pyplot as plt
from datetime import datetime
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


x=[]
y=[]
for roll_no,details in student_records.items():
    x.append(details["Name"])
    y.append(details["Total"])
plt.subplot(2,2,1)
plt.bar_label(plt.bar(x,y,width=0.5,color="darkgreen"))
plt.xlabel("Students -->")
plt.ylabel("Total Marks -->")
plt.title("Comparision of Students")

a=[]
a.append(fail)
a.append(passe)
b=["Fail","Pass"]
plt.subplot(2,2,2)
plt.pie(a, labels=b, autopct='%1.1f%%',explode = [0.2, 0])
plt.title("Pass Vs Fail")

for roll_no, details in student_records.items():
    if details["Name"]==Topper:
        c=list(details.keys())
        d=list(details.values())
        c.remove("Name")
        c.remove("Total")
        d.remove(Topper)
        d.remove(Topper_score)
print(c)
plt.subplot(2,2,3)
plt.bar_label(plt.bar(c,d))
plt.xlabel("Subjects")
plt.ylabel("Topper Marks")
plt.title("Topper Details")

plt.subplot(2,2,4)
plt.axis("off")
plt.text(0.05, 0.05, f"Timestamp: {current_time}", 
         fontsize=10, 
         bbox=dict(facecolor='white', edgecolor='gray', alpha=0.8))

plt.tight_layout()
plt.savefig("Studant_graph.png")
plt.show()

# git add .
# git commit -m "Finished the initial layout for result.py"
# git push
# git push origin --delete nupur-task