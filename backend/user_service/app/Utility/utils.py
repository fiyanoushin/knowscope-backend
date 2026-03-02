def serialize_student(student) -> dict:
    return {
        "id": str(student["_id"]),
        "name": student.get("name"),
        "class_number": student.get("class_number"),
        "medium": student.get("medium"),
        "learningstyle": student.get("learningstyle"),
        "image": student.get("image"), 
    }
