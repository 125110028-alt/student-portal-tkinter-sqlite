import csv
from datetime import datetime
import matplotlib.pyplot as plt
from export import export_real_data
export_real_data()  # refresh the CSV from live DB first
student_records = load_student_records("student_results.csv")  # use export's filename


def get_topper(data):
    if not data:
        return None, 0

    topper_roll = max(data, key=lambda roll_no: data[roll_no]["Total"])
    return data[topper_roll]["Name"], data[topper_roll]["Total"]


def get_top3_students(data):
    if not data:
        return []

    arranged_list = []
    for roll_no, details in data.items():
        arranged_list.append({
            "Roll No": roll_no,
            "Name": details["Name"],
            "Marks": details["Total"]
        })

    sorted_list = sorted(arranged_list, key=lambda x: x["Marks"], reverse=True)
    return sorted_list[:3]


def calculate_class_average(data):
    if not data:
        return 0

    total_marks = sum(details["Total"] for details in data.values())
    return round(total_marks / len(data), 2)


def calculate_pass_percentage(data):
    if not data:
        return 0, 0, []

    passed = 0
    failed = 0
    failed_students = []

    for _, details in data.items():
        failed_subjects = 0

        for subject, marks in details.items():
            if subject not in ("Name", "Total") and isinstance(marks, int) and marks < 40:
                failed_subjects += 1

        if failed_subjects == 0:
            passed += 1
        else:
            failed += 1
            failed_students.append(details["Name"])

    return passed, failed, failed_students


def load_student_records(filename="database.csv"):
    student_records = {}

    with open(filename, mode="r", newline="", encoding="utf-8") as file:
        csv_reader = csv.DictReader(file)

        for row in csv_reader:
            roll_no = row.pop("Roll_no").strip()
            name = row["Name"].strip()

            student_data = {"Name": name}
            running_total = 0

            for key, value in row.items():
                if key == "Name":
                    continue

                marks = int(value)
                student_data[key] = marks
                running_total += marks

            student_data["Total"] = running_total
            student_records[roll_no] = student_data

    return student_records


def create_graphs(student_records, topper_name, topper_score, passed, failed, current_time):
    names = []
    totals = []

    for _, details in student_records.items():
        names.append(details["Name"])
        totals.append(details["Total"])

    plt.figure(figsize=(12, 8))

    plt.subplot(2, 2, 1)
    bars = plt.bar(names, totals, width=0.5, color="darkgreen")
    plt.bar_label(bars)
    plt.xlabel("Students")
    plt.ylabel("Total Marks")
    plt.title("Comparison of Students")
    plt.xticks(rotation=15)

    plt.subplot(2, 2, 2)
    plt.pie(
        [failed, passed],
        labels=["Fail", "Pass"],
        autopct="%1.1f%%",
        explode=[0.2, 0]
    )
    plt.title("Pass vs Fail")

    topper_subjects = []
    topper_marks = []

    for _, details in student_records.items():
        if details["Name"] == topper_name:
            for subject, marks in details.items():
                if subject not in ("Name", "Total"):
                    topper_subjects.append(subject)
                    topper_marks.append(marks)
            break

    plt.subplot(2, 2, 3)
    bars = plt.bar(topper_subjects, topper_marks, color="royalblue")
    plt.bar_label(bars)
    plt.xlabel("Subjects")
    plt.ylabel("Topper Marks")
    plt.title(f"Topper Details: {topper_name} ({topper_score})")

    plt.subplot(2, 2, 4)
    plt.axis("off")
    plt.text(
        0.05,
        0.75,
        f"Timestamp: {current_time}",
        fontsize=10,
        bbox=dict(facecolor="white", edgecolor="gray", alpha=0.8)
    )
    plt.text(0.05, 0.55, f"Class Average: {calculate_class_average(student_records)}", fontsize=10)
    plt.text(0.05, 0.35, f"Total Students: {len(student_records)}", fontsize=10)
    plt.text(0.05, 0.15, f"Topper: {topper_name}", fontsize=10)

    plt.tight_layout()
    plt.savefig("Student_graph.png")
    plt.show()


def main():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        student_records = load_student_records("database.csv")
    except FileNotFoundError:
        print("Error: database.csv file not found.")
        return
    except Exception as e:
        print(f"Error while reading data: {e}")
        return

    topper_name, topper_score = get_topper(student_records)
    top_3_students = get_top3_students(student_records)
    class_average = calculate_class_average(student_records)
    passed, failed, failed_students = calculate_pass_percentage(student_records)

    print("Topper:", topper_name, "-> With highest score:", topper_score)
    print("Top 3 Students:", top_3_students)
    print("Class Average:", class_average)

    total_students = passed + failed
    pass_percentage = (passed * 100 / total_students) if total_students > 0 else 0

    print("Pass Percentage:", round(pass_percentage, 2), "%")
    print("Failed students are:", failed_students)

    if student_records:
        create_graphs(
            student_records,
            topper_name,
            topper_score,
            passed,
            failed,
            current_time
        )


if __name__ == "__main__":
    main()
