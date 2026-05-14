from flask import Flask, jsonify, request
from src.student_db import student_service

app = Flask(__name__)

@app.after_request
def cors(response):
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, PATCH, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


@app.route("/students", methods=["GET"])
def get_all_students():
    students = student_service.get_all_students()
    return jsonify({
        "code": 200,
        "message": "success",
        "data": [s.to_dict() for s in students]
    })


@app.route("/students/<int:student_id>", methods=["GET"])
def get_student(student_id):
    try:
        student = student_service.get_student_by_id(student_id)
        return jsonify({
            "code": 200,
            "message": "success",
            "data": student.to_dict()
        })
    except ValueError as e:
        return jsonify({
            "code": 404,
            "message": str(e),
            "data": None
        }), 404


@app.route("/students/search", methods=["GET"])
def search_student():
    name = request.args.get("name", "")
    students = student_service.search_by_name(name)
    return jsonify({
        "code": 200,
        "message": "success",
        "data": [s.to_dict() for s in students]
    })


@app.route("/students", methods=["POST"])
def create_student():
    data = request.get_json()
    try:
        name = data.get("name")
        age = data.get("age")
        grade = data.get("grade")
        return jsonify({
            "code": 201,
            "message": "学生创建成功",
            "data": student_service.create_student(name, age, grade).to_dict()
        })
    except ValueError as e:
        return jsonify({
            "code": 400,
            "message": str(e),
            "data": None
        }), 400


@app.route("/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    data = request.get_json()
    try:
        name = data.get("name")
        age = data.get("age")
        grade = data.get("grade")
        return jsonify({
            "code": 200,
            "message": "学生更新成功",
            "data": student_service.update_student(student_id, name, age, grade).to_dict()
        })
    except ValueError as e:
        return jsonify({
            "code": 404,
            "message": str(e),
            "data": None
        }), 404


@app.route("/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    try:
        student_service.delete_student(student_id)
        return jsonify({
            "code": 200,
            "message": "学生删除成功",
            "data": None
        })
    except ValueError as e:
        return jsonify({
            "code": 404,
            "message": str(e),
            "data": None
        }), 404


@app.route("/students/batch", methods=["DELETE"])
def batch_delete_students():
    data = request.get_json()
    ids = data.get("ids", [])
    try:
        deleted = student_service.batch_delete_students(ids)
        return jsonify({
            "code": 200,
            "message": f"成功删除 {len(deleted)} 个学生",
            "data": {"deleted_ids": deleted}
        })
    except ValueError as e:
        return jsonify({
            "code": 400,
            "message": str(e),
            "data": None
        }), 400


@app.route("/students/statistics", methods=["GET"])
def get_statistics():
    stats = student_service.get_statistics()
    return jsonify({
        "code": 200,
        "message": "success",
        "data": stats
    })


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "code": 200,
        "message": "healthy",
        "data": {"status": "ok", "database": "MySQL"}
    })


if __name__ == "__main__":
    print("=" * 50)
    print("  学生管理系统 API (MySQL数据库)")
    print("=" * 50)
    print("API地址: http://127.0.0.1:5000")
    print("数据库: school_db (MySQL)")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=True)
