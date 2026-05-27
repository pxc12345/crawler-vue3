import csv
import os
import uuid
import re
from datetime import datetime
from io import BytesIO
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from openpyxl import Workbook
from src.student_db import student_service
from src.notifications.config import notification_config
from src.notification_db import notification_db
from src.notifications.email_sender import EmailSender
from src.notifications.sms_sender import SmsSender
from src.notifications.verification_service import verification_service
from src.auth_service import auth_service

email_sender = None
sms_sender = None

if notification_config.EMAIL_ENABLED:
    email_sender = EmailSender(
        notification_config.ALIYUN_ACCESS_KEY_ID,
        notification_config.ALIYUN_ACCESS_KEY_SECRET,
        notification_config.ALIYUN_REGION
    )
    verification_service.set_email_sender(email_sender)

if notification_config.SMS_ENABLED:
    sms_sender = SmsSender(
        notification_config.ALIYUN_ACCESS_KEY_ID,
        notification_config.ALIYUN_ACCESS_KEY_SECRET,
        notification_config.ALIYUN_REGION
    )
    verification_service.set_sms_sender(sms_sender)

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}


def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def is_valid_phone(phone):
    pattern = r'^1[3-9]\d{9}$'
    return re.match(pattern, phone) is not None


def get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr


@app.after_request
def cors(response):
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, PATCH, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


# ==================== 用户认证相关API ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json() or {}
        username = data.get('username', '').strip()
        email = data.get('email', '').strip() or None
        phone = data.get('phone', '').strip() or None
        password = data.get('password', '')

        if not username or len(username) < 3:
            return jsonify({'success': False, 'message': '用户名至少3个字符', 'code': 'INVALID_USERNAME'}), 400

        if not password or len(password) < 6:
            return jsonify({'success': False, 'message': '密码至少6个字符', 'code': 'INVALID_PASSWORD'}), 400

        if notification_db.get_user_by_username(username):
            return jsonify({'success': False, 'message': '用户名已存在', 'code': 'USERNAME_EXISTS'}), 400

        if email and notification_db.get_user_by_email(email):
            return jsonify({'success': False, 'message': '邮箱已被注册', 'code': 'EMAIL_EXISTS'}), 400

        if phone and notification_db.get_user_by_phone(phone):
            return jsonify({'success': False, 'message': '手机号已被注册', 'code': 'PHONE_EXISTS'}), 400

        password_hash = auth_service.hash_password(password)
        user_id = notification_db.create_user_with_username(
            username=username,
            email=email,
            phone=phone,
            password_hash=password_hash
        )

        notification_db.add_audit_log(
            user_id=user_id,
            action='REGISTER',
            ip_address=get_client_ip(),
            user_agent=request.headers.get('User-Agent'),
            details=f'用户 {username} 注册成功'
        )

        return jsonify({'success': True, 'message': '注册成功', 'data': {'user_id': user_id}}), 201

    except Exception as e:
        return jsonify({'success': False, 'message': '注册失败', 'code': 'REGISTER_FAILED', 'error': str(e)}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json() or {}
        identifier = data.get('identifier', '').strip()
        password = data.get('password', '')

        if not identifier or not password:
            return jsonify({'success': False, 'message': '请输入账号和密码', 'code': 'MISSING_CREDENTIALS'}), 400

        result = auth_service.authenticate_user(identifier, password)

        if result['success']:
            notification_db.add_audit_log(
                user_id=result['data']['user']['id'],
                action='LOGIN',
                ip_address=get_client_ip(),
                user_agent=request.headers.get('User-Agent'),
                details=f'用户 {identifier} 登录成功'
            )

        status_code = 200 if result['success'] else 401
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({'success': False, 'message': '登录失败', 'code': 'LOGIN_FAILED', 'error': str(e)}), 500


@app.route('/api/auth/refresh', methods=['POST'])
def refresh_token():
    try:
        data = request.get_json() or {}
        refresh_token = data.get('refresh_token', '')

        if not refresh_token:
            return jsonify({'success': False, 'message': '缺少Refresh Token', 'code': 'MISSING_TOKEN'}), 400

        result = auth_service.refresh_access_token(refresh_token)
        status_code = 200 if result['success'] else 401
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({'success': False, 'message': '刷新Token失败', 'code': 'REFRESH_FAILED', 'error': str(e)}), 500


@app.route('/api/auth/logout', methods=['POST'])
@auth_service.login_required
def logout():
    try:
        auth_header = request.headers.get('Authorization', '')
        _, access_token = auth_header.split()

        data = request.get_json() or {}
        refresh_token = data.get('refresh_token', '')

        auth_service.blacklist_token(access_token)
        if refresh_token:
            auth_service.blacklist_token(refresh_token)

        notification_db.add_audit_log(
            user_id=request.user_id,
            action='LOGOUT',
            ip_address=get_client_ip(),
            user_agent=request.headers.get('User-Agent'),
            details=f'用户 {request.username} 登出成功'
        )

        return jsonify({'success': True, 'message': '登出成功'}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': '登出失败', 'code': 'LOGOUT_FAILED', 'error': str(e)}), 500


@app.route('/api/auth/forgot-password/send-code', methods=['POST'])
def send_forgot_password_code():
    try:
        data = request.get_json() or {}
        target = data.get('target', '').strip()

        if not target:
            return jsonify({'success': False, 'message': '请输入邮箱或手机号', 'code': 'MISSING_TARGET'}), 400

        if is_valid_email(target):
            result = verification_service.send_email_code(target)
        elif is_valid_phone(target):
            result = verification_service.send_sms_code(target)
        else:
            return jsonify({'success': False, 'message': '请输入有效的邮箱或手机号', 'code': 'INVALID_TARGET'}), 400

        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({'success': False, 'message': '发送验证码失败', 'code': 'SEND_CODE_FAILED', 'error': str(e)}), 500


@app.route('/api/auth/forgot-password/verify-code', methods=['POST'])
def verify_forgot_password_code():
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id')
        code = data.get('code', '').strip()
        target = data.get('target', '').strip()

        if not all([user_id, code, target]):
            return jsonify({'success': False, 'message': '缺少必要参数', 'code': 'MISSING_PARAMS'}), 400

        code_type = 'email' if is_valid_email(target) else 'sms'
        result = verification_service.verify_code(user_id, code, code_type, target)

        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({'success': False, 'message': '验证失败', 'code': 'VERIFY_FAILED', 'error': str(e)}), 500


@app.route('/api/auth/forgot-password/reset', methods=['POST'])
def reset_password():
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id')
        new_password = data.get('new_password', '')

        if not user_id or not new_password:
            return jsonify({'success': False, 'message': '缺少必要参数', 'code': 'MISSING_PARAMS'}), 400

        if len(new_password) < 6:
            return jsonify({'success': False, 'message': '密码至少6个字符', 'code': 'INVALID_PASSWORD'}), 400

        result = auth_service.reset_password(user_id, new_password, check_history=True)

        if result['success']:
            notification_db.add_audit_log(
                user_id=user_id,
                action='RESET_PASSWORD',
                ip_address=get_client_ip(),
                user_agent=request.headers.get('User-Agent'),
                details='用户通过忘记密码流程重置密码'
            )

        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({'success': False, 'message': '重置密码失败', 'code': 'RESET_FAILED', 'error': str(e)}), 500


@app.route('/api/auth/change-password', methods=['POST'])
@auth_service.login_required
def change_password():
    try:
        data = request.get_json() or {}
        old_password = data.get('old_password', '')
        new_password = data.get('new_password', '')

        if not old_password or not new_password:
            return jsonify({'success': False, 'message': '缺少必要参数', 'code': 'MISSING_PARAMS'}), 400

        if len(new_password) < 6:
            return jsonify({'success': False, 'message': '新密码至少6个字符', 'code': 'INVALID_PASSWORD'}), 400

        user = notification_db.get_user_by_id(request.user_id)
        if not auth_service.verify_password(old_password, user['password_hash']):
            return jsonify({'success': False, 'message': '原密码错误', 'code': 'INVALID_OLD_PASSWORD'}), 400

        result = auth_service.reset_password(request.user_id, new_password, check_history=True)

        if result['success']:
            notification_db.add_audit_log(
                user_id=request.user_id,
                action='CHANGE_PASSWORD',
                ip_address=get_client_ip(),
                user_agent=request.headers.get('User-Agent'),
                details='用户修改密码'
            )

        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({'success': False, 'message': '修改密码失败', 'code': 'CHANGE_FAILED', 'error': str(e)}), 500


@app.route('/api/user/profile', methods=['GET'])
@auth_service.login_required
def get_profile():
    try:
        user = notification_db.get_user_by_id(request.user_id)
        if not user:
            return jsonify({'success': False, 'message': '用户不存在', 'code': 'USER_NOT_FOUND'}), 404

        return jsonify({
            'success': True,
            'data': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'phone': user['phone'],
                'last_login_at': user['last_login_at'],
                'created_at': user['created_at']
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': '获取用户信息失败', 'code': 'GET_PROFILE_FAILED', 'error': str(e)}), 500


# ==================== 学生管理相关API ====================

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
        avatar_url = data.get("avatar_url")
        return jsonify({
            "code": 201,
            "message": "学生创建成功",
            "data": student_service.create_student(name, age, grade, avatar_url).to_dict()
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
        avatar_url = data.get("avatar_url")
        return jsonify({
            "code": 200,
            "message": "学生更新成功",
            "data": student_service.update_student(student_id, name, age, grade, avatar_url).to_dict()
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


@app.route("/upload", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return jsonify({
            "code": 400,
            "message": "没有文件",
            "data": None
        }), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({
            "code": 400,
            "message": "没有选择文件",
            "data": None
        }), 400

    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        file_url = f"/uploads/{filename}"

        return jsonify({
            "code": 200,
            "message": "文件上传成功",
            "data": {"url": file_url, "filename": filename}
        })

    return jsonify({
        "code": 400,
        "message": "不支持的文件类型",
        "data": None
    }), 400


@app.route("/uploads/<filename>", methods=["GET"])
def serve_uploaded_file(filename):
    return send_file(os.path.join(UPLOAD_FOLDER, filename))


@app.route("/students/export", methods=["GET"])
def export_students():
    students = student_service.get_all_students()

    wb = Workbook()
    ws = wb.active
    ws.title = "学生数据"
    ws.append(['ID', '姓名', '年龄', '成绩', '创建时间', '测试列'])

    for student in students:
        ws.append([
            student.student_id,
            student.name,
            student.age,
            student.grade,
            str(student.create_time) if hasattr(student, 'create_time') and student.create_time else '',
            student.test_column if hasattr(student, 'test_column') else f"test-{student.student_id}-666"
        ])

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    return send_file(
        buffer,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f"students_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    )


@app.route("/students/import", methods=["POST"])
def import_students():
    if 'file' not in request.files:
        return jsonify({
            "code": 400,
            "message": "没有文件",
            "data": None
        }), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({
            "code": 400,
            "message": "没有选择文件",
            "data": None
        }), 400

    if not file.filename.endswith('.csv'):
        return jsonify({
            "code": 400,
            "message": "只支持 CSV 文件",
            "data": None
        }), 400

    import_folder = 'imports'
    if not os.path.exists(import_folder):
        os.makedirs(import_folder)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"import_{timestamp}.csv"
    filepath = os.path.join(import_folder, filename)
    file.save(filepath)

    imported_count = 0
    error_rows = []

    try:
        with open(filepath, 'r', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            for row_num, row in enumerate(reader, start=2):
                try:
                    name = row.get('姓名', '').strip()
                    age = int(row.get('年龄', 0))
                    grade = float(row.get('成绩', 0))

                    if name and 1 <= age <= 150 and 0 <= grade <= 100:
                        student_service.create_student(name, age, grade)
                        imported_count += 1
                    else:
                        error_rows.append(f"第{row_num}行: 数据格式错误")
                except (ValueError, KeyError) as e:
                    error_rows.append(f"第{row_num}行: {str(e)}")

        return jsonify({
            "code": 200,
            "message": f"导入完成，成功导入 {imported_count} 条记录",
            "data": {
                "imported": imported_count,
                "errors": error_rows
            }
        })

    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"导入失败: {str(e)}",
            "data": None
        }), 500


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "code": 200,
        "message": "healthy",
        "data": {"status": "ok", "database": "MySQL"}
    })


@app.route("/api/health", methods=['GET'])
def api_health_check():
    return jsonify({
        'success': True,
        'message': 'Server is running',
        'data': {
            'status': 'healthy'
        }
    }), 200


@app.route("/verification/send-email", methods=["POST"])
def send_email_verification():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({
            "code": 400,
            "message": "邮箱不能为空",
            "data": None
        }), 400

    result = verification_service.send_email_code(email)

    if result["success"]:
        return jsonify({
            "code": 200,
            "message": result["message"],
            "data": result["data"]
        })
    else:
        return jsonify({
            "code": 400,
            "message": result["message"],
            "data": None
        }), 400


@app.route("/verification/send-sms", methods=["POST"])
def send_sms_verification():
    data = request.get_json()
    phone = data.get("phone")

    if not phone:
        return jsonify({
            "code": 400,
            "message": "手机号不能为空",
            "data": None
        }), 400

    result = verification_service.send_sms_code(phone)

    if result["success"]:
        return jsonify({
            "code": 200,
            "message": result["message"],
            "data": result["data"]
        })
    else:
        return jsonify({
            "code": 400,
            "message": result["message"],
            "data": None
        }), 400


@app.route("/verification/verify", methods=["POST"])
def verify_code():
    data = request.get_json()
    user_id = data.get("user_id")
    code = data.get("code")
    code_type = data.get("type")
    target = data.get("target")

    if not all([user_id, code, code_type, target]):
        return jsonify({
            "code": 400,
            "message": "参数不完整",
            "data": None
        }), 400

    result = verification_service.verify_code(user_id, code, code_type, target)

    if result["success"]:
        return jsonify({
            "code": 200,
            "message": result["message"],
            "data": result["data"]
        })
    else:
        return jsonify({
            "code": 400,
            "message": result["message"],
            "data": None
        }), 400


if __name__ == "__main__":
    print("=" * 50)
    print("  学生管理系统 + 用户认证系统 API")
    print("=" * 50)
    print("API地址: http://127.0.0.1:5000")
    print("数据库: sys (TiDB Cloud @ gateway01.ap-southeast-1.prod.aws.tidbcloud.com)")
    print("前端地址: http://localhost:5173")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=True)
