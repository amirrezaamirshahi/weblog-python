from decouple import config

JWT_SECRET = config("SECRET")
JWT_ALGORITGM = config("ALGORITGM")

print(JWT_SECRET)
print(JWT_ALGORITGM)