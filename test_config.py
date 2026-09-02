from config.settings import settings

print("Testing Configuration Setup")
print(f"Root {settings.BASE_DIR}")
print(f"Uploads directory {settings.UPLOADS_DIR}")
print(f"Target LLM Model: {settings.LLM_MODEL}")


try:
    settings.validate()
    print("correct")

except ValueError as e:
    print(e)
