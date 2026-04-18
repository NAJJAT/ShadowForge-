"""
MacOS Persistence - استمرارية على MacOS
"""

import logging

logger = logging.getLogger(__name__)

class MacOSPersistence:
    """يدير طرق الاستمرارية على MacOS"""
    
    def __init__(self, simulation_mode: bool = True):
        self.simulation_mode = simulation_mode
    
    def add_launch_agent(self, label: str, program: str) -> bool:
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{label}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{program}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
"""
        path = f"~/Library/LaunchAgents/{label}.plist"
        if self.simulation_mode:
            logger.info(f"[SIM] Created launch agent at {path}")
        else:
            with open(os.path.expanduser(path), "w") as f:
                f.write(plist_content)
        return True