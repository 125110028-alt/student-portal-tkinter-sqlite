def get_topper(data):
    if not data:
        return None
    sorted_data = sorted(data, key=lambda x: x['total_marks'], reverse=True)
    return sorted_data[0]

def get_top3_students(data):
    if not data:
        return []
    sorted_data = sorted(data, key=lambda x: x['total_marks'], reverse=True)
    return sorted_data[:3]

def calculate_class_average(data):
    if not data:
        return 0
    total_score = sum(student['total_marks'] for student in data)
    return total_score / len(data)

def calculate_pass_percentage(data, passing_score=40):
    if not data:
        return 0
    passed_count = sum(1 for student in data if student['total_marks'] >= passing_score)
    return (passed_count / len(data)) * 100

student_records = [
    {"name": "Nupur", "total_marks": 65},
    {"name": "Raunak", "total_marks": 75},
    {"name": "Kshitiz", "total_marks": 85},
    {"name": "Divyanshu", "total_marks": 70},
    {"name": "Goku Bhai", "total_marks": 75}
]
print("Topper:", get_topper(student_records))
print("Top 3 Students:", get_top3_students(student_records))
print("Class Average:", calculate_class_average(student_records))
print("Pass Percentage:", calculate_pass_percentage(student_records), "%")