#!/bin/bash

echo "=== 1️⃣ Checking Python packages ==="
PACKAGES=("fastapi" "sqlmodel" "uvicorn" "python-jose" "asyncpg")
for pkg in "${PACKAGES[@]}"; do
    pip show $pkg &> /dev/null
    if [ $? -eq 0 ]; then
        echo "✅ $pkg is installed"
    else
        echo "❌ $pkg is NOT installed"
    fi
done

echo -e "\n=== 2️⃣ Checking backend folder structure ==="

REQUIRED_FOLDERS=("src/api" "src/models" "src/schemas" "src/services" "src/database")
for folder in "${REQUIRED_FOLDERS[@]}"; do
    if [ -d "$folder" ]; then
        echo "✅ $folder exists"
    else
        echo "❌ $folder is MISSING"
    fi
done

REQUIRED_API_FILES=("src/api/auth.py" "src/api/tasks.py" "src/api/health.py" "src/api/monitoring.py")
for file in "${REQUIRED_API_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file is MISSING"
    fi
done

REQUIRED_MODEL_FILES=("src/models/user.py" "src/models/task.py")
for file in "${REQUIRED_MODEL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file is MISSING"
    fi
done

echo -e "\n=== 3️⃣ Checking .env variables ==="
ENV_FILE="../.env"
if [ -f "$ENV_FILE" ]; then
    REQUIRED_VARS=("NEON_DB_URL" "BETTER_AUTH_SECRET" "ALLOWED_ORIGINS")
    for var in "${REQUIRED_VARS[@]}"; do
        grep -q "^$var=" "$ENV_FILE"
        if [ $? -eq 0 ]; then
            echo "✅ $var found in .env"
        else
            echo "❌ $var is MISSING in .env"
        fi
    done
else
    echo "❌ .env file not found at $ENV_FILE"
fi

echo -e "\n✅ Verification complete!"

