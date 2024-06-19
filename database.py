from pymongo import MongoClient
from bson.binary import Binary

# Kết nối đến MongoDB
client = MongoClient("mongodb://localhost:27017/")

# Tạo hoặc chọn database Test
db = client["Test"]

# Tạo hoặc chọn collection certificate
certificate_collection = db["certificate"]
certificate_collection.create_index("school_name", unique=True)
certificate_collection.create_index("auth_name", unique=False)
certificate_collection.create_index("auth_email", unique=False)
certificate_collection.create_index("status", unique=False)
certificate_collection.create_index("csr", unique=False)
certificate_collection.create_index("certificate", unique=False)


users_collection = db["users"]
users_collection.create_index("username", unique=True)
users_collection.create_index("password", unique=False)
users_collection.create_index("school_name", unique=False)
users_collection.create_index("role", unique=False)

# Tạo hoặc chọn collection students
students_collection = db["students"]
students_collection.create_index("student_id", unique=True)
students_collection.create_index("student_name", unique=False)
students_collection.create_index("student_school", unique=False)



# Tạo hoặc chọn collection school
school_collection = db["school"]
school_collection.create_index("school_name", unique=True)
school_collection.create_index("auth_name", unique=False)
school_collection.create_index("auth_email", unique=False)
school_collection.create_index("public_key", unique=False)
school_collection.create_index("certificate", unique=False)



# Tạo hoặc chọn collection qualificate
qualificate_collection = db["qualificate"]
qualificate_collection.create_index("student_id", unique=False)
qualificate_collection.create_index("qualificate_id", unique=True)
qualificate_collection.create_index("qualificate", unique=False)
qualificate_collection.create_index("signature", unique=False)




print("Collections and sample data created successfully.")
