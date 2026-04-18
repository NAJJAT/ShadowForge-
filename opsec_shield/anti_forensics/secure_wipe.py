"""
Secure Wipe - مسح آمن للملفات والمجلدات
"""

import os
import random
import shutil
import logging
from pathlib import Path
from typing import Union

logger = logging.getLogger(__name__)


class SecureWipe:
    """
    مسح آمن للملفات بعدة تمريرات (مثل Gutmann method)
    """
    
    def __init__(self, passes: int = 7, simulation_mode: bool = True):
        self.passes = passes
        self.simulation_mode = simulation_mode
        logger.info(f"SecureWipe initialized (passes={passes})")
    
    def wipe_file(self, filepath: Union[str, Path]) -> bool:
        """
        مسح ملف بتمريرات متعددة
        """
        path = Path(filepath)
        if not path.exists():
            logger.warning(f"File not found: {path}")
            return False
        
        if self.simulation_mode:
            logger.info(f"[SIM] Would wipe {path} with {self.passes} passes")
            return True
        
        try:
            size = path.stat().st_size
            with open(path, "wb") as f:
                for _ in range(self.passes):
                    # تمرير بالأصفار
                    f.seek(0)
                    f.write(b'\x00' * size)
                    f.flush()
                    # تمرير بأحرف عشوائية
                    f.seek(0)
                    f.write(os.urandom(size))
                    f.flush()
                    # تمرير بقيم محددة (مثل 0xFF)
                    f.seek(0)
                    f.write(b'\xFF' * size)
                    f.flush()
            path.unlink()
            logger.info(f"Securely wiped {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to wipe {path}: {e}")
            return False
    
    def wipe_directory(self, dirpath: Union[str, Path], recursive: bool = True) -> bool:
        """
        مسح مجلد بالكامل
        """
        path = Path(dirpath)
        if not path.exists():
            logger.warning(f"Directory not found: {path}")
            return False
        
        if self.simulation_mode:
            logger.info(f"[SIM] Would wipe directory {path}")
            return True
        
        try:
            if recursive:
                for item in path.rglob("*"):
                    if item.is_file():
                        self.wipe_file(item)
            shutil.rmtree(path)
            logger.info(f"Securely wiped directory {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to wipe directory: {e}")
            return False
    
    def wipe_pattern(self, pattern: str, directory: Union[str, Path] = "."):
        """
        مسح الملفات المتطابقة مع نمط
        """
        path = Path(directory)
        for filepath in path.glob(pattern):
            self.wipe_file(filepath)


if __name__ == "__main__":
    wiper = SecureWipe(passes=3, simulation_mode=True)
    # wiper.wipe_file("test.txt")
    print("Secure wipe ready")