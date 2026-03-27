set -e

# Navigate to your project directory
cd /home/lean/phytolean

# Create or clear the log file
logfile="/home/lean/deploy.log"
: > "$logfile"

# Log the user executing the script
echo "Logging who is executing the script..." | tee -a "$logfile"
whoami | tee -a "$logfile"

# Pull the latest code
echo "Pulling latest code..." | tee -a "$logfile"
git fetch origin
git reset --hard origin/main >> "$logfile" 2>&1
echo "git reset exit code: $?" | tee -a "$logfile"

# Ensure uv is available
if ! command -v uv &> /dev/null; then
    echo "Installing uv..." | tee -a "$logfile"
    curl -LsSf https://astral.sh/uv/install.sh | sh >> "$logfile" 2>&1
fi
export PATH="$HOME/.local/bin:$PATH"

# Install dependencies with uv
echo "Installing dependencies..." | tee -a "$logfile"
uv sync >> "$logfile" 2>&1
echo "uv sync exit code: $?" | tee -a "$logfile"

# Apply migrations
echo "Applying migrations..." | tee -a "$logfile"
uv run python manage.py migrate --noinput >> "$logfile" 2>&1
echo "migrate exit code: $?" | tee -a "$logfile"

# Collect static files
echo "Collecting static files..." | tee -a "$logfile"
uv run python manage.py collectstatic --noinput >> "$logfile" 2>&1
echo "collectstatic exit code: $?" | tee -a "$logfile"

# Restart Gunicorn using the password from SERVER_PWD
echo "Restarting Gunicorn..." | tee -a "$logfile"
if sudo systemctl restart gunicorn >> "$logfile" 2>&1; then
    echo "Gunicorn restarted successfully." | tee -a "$logfile"
else
    echo "Failed to restart Gunicorn" | tee -a "$logfile"
fi
