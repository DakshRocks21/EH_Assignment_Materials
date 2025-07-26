## Setup

### Setting up the webhook

1. Populate `config.json` file in `C:\Users\<username>\config.json`
2. Create/Activate a virtual environment
3. Install the required packages.
4. Create a configuration file for supervisor at `C:\supervisor\supervisor.conf`.
5. Create a directory for the projects at `C:\Users\<username>\projects`
6. Start the service `python -m supervisor.supervisord -c C:\supervisor\supervisor.conf`
7. Start the webhook service using `python webhook.py`, which should be at `C:\Users\<username>\webhook.py`

8. Install Cloudflared
9. Tunnel it, and connect it to a github webhook
