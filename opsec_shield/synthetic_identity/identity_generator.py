"""
Synthetic Identity Generator - توليد هويات رقمية كاملة
"""

import random
import time
import hashlib
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from faker import Faker  # pip install Faker

# تهيئة Faker لكل اللغات
fake_en = Faker('en_US')
fake_ar = Faker('ar_SA')
fake_fr = Faker('fr_FR')


@dataclass
class DigitalIdentity:
    """هوية رقمية كاملة"""
    name: str
    email: str
    phone: str
    crypto_wallets: Dict[str, str]
    social_accounts: Dict[str, str]
    location: Dict[str, str]
    behavioral_profile: Dict[str, any]
    created_at: float = field(default_factory=time.time)
    identity_id: str = ""
    
    def __post_init__(self):
        if not self.identity_id:
            self.identity_id = hashlib.md5(
                f"{self.name}{self.email}{self.created_at}".encode()
            ).hexdigest()[:12]
    
    def to_dict(self) -> dict:
        return {
            "identity_id": self.identity_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "crypto_wallets": self.crypto_wallets,
            "social_accounts": self.social_accounts,
            "location": self.location,
            "behavioral_profile": self.behavioral_profile,
            "created_at": self.created_at,
        }


class SyntheticIdentity:
    """
    مولد هويات رقمية اصطناعية
    
    يولد هوية كاملة لكل عملية:
    - اسم وهمي
    - بريد إلكتروني مجهول
    - رقم هاتف مؤقت
    - محافظ عملات رقمية
    - حسابات على وسائل التواصل
    - بصمة سلوكية فريدة
    """
    
    def __init__(self, simulation_mode: bool = True):
        self.simulation_mode = simulation_mode
        self.identities: List[DigitalIdentity] = []
        self.current_identity: Optional[DigitalIdentity] = None
        
        # قوائم للأسماء والألقاب العربية والإنجليزية
        self.first_names_ar = ["أحمد", "محمد", "علي", "حسن", "حسين", "عمر", "عثمان", "خالد", "ياسر"]
        self.last_names_ar = ["الهاشمي", "التميمي", "القحطاني", "المالكي", "العبيدي", "الراشدي"]
        
        self.first_names_en = ["John", "David", "Michael", "James", "Robert", "William", "Thomas"]
        self.last_names_en = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller"]
        
        logger.info(f"SyntheticIdentity initialized")
    
    def generate(self, nationality: str = "random", personality: str = "random") -> DigitalIdentity:
        """
        توليد هوية جديدة
        
        Args:
            nationality: الجنسية (us, uk, sa, ae, random)
            personality: نوع الشخصية (tech, business, student, random)
        
        Returns:
            DigitalIdentity: الهوية المولدة
        """
        if nationality == "random":
            nationality = random.choice(["us", "uk", "sa", "ae", "fr", "de"])
        
        # 1. الاسم
        if nationality in ["sa", "ae", "eg"]:
            first = random.choice(self.first_names_ar)
            last = random.choice(self.last_names_ar)
            name = f"{first} {last}"
        else:
            first = random.choice(self.first_names_en)
            last = random.choice(self.last_names_en)
            name = f"{first} {last}"
        
        # 2. البريد الإلكتروني
        email = self._generate_email(name, nationality)
        
        # 3. رقم الهاتف
        phone = self._generate_phone(nationality)
        
        # 4. المحافظ الرقمية
        crypto_wallets = self._generate_crypto_wallets()
        
        # 5. حسابات التواصل
        social_accounts = self._generate_social_accounts(name)
        
        # 6. الموقع
        location = self._generate_location(nationality)
        
        # 7. البصمة السلوكية
        behavioral_profile = self._generate_behavioral_profile(personality)
        
        # إنشاء الهوية
        identity = DigitalIdentity(
            name=name,
            email=email,
            phone=phone,
            crypto_wallets=crypto_wallets,
            social_accounts=social_accounts,
            location=location,
            behavioral_profile=behavioral_profile,
        )
        
        self.identities.append(identity)
        logger.info(f"Generated identity: {identity.name} ({identity.email})")
        
        return identity
    
    def _generate_email(self, name: str, nationality: str) -> str:
        """توليد بريد إلكتروني"""
        providers = [
            "protonmail.com", "proton.me", "tutanota.com", 
            "mailfence.com", "ctemplar.com", "cock.li"
        ]
        
        # اختيار مزود آمن
        provider = random.choice(providers)
        
        # تنظيف الاسم
        clean_name = name.lower().replace(" ", ".")
        clean_name = ''.join(c for c in clean_name if c.isalnum() or c == '.')
        
        # إضافة أرقام عشوائية
        suffix = random.randint(10, 999)
        
        return f"{clean_name}.{suffix}@{provider}"
    
    def _generate_phone(self, nationality: str) -> str:
        """توليد رقم هاتف"""
        # أرقام وهمية لأغراض تعليمية
        prefixes = {
            "us": "+1", "uk": "+44", "sa": "+966", "ae": "+971", 
            "fr": "+33", "de": "+49"
        }
        
        prefix = prefixes.get(nationality, "+1")
        number = ''.join([str(random.randint(0, 9)) for _ in range(9)])
        
        return f"{prefix}{number}"
    
    def _generate_crypto_wallets(self) -> Dict[str, str]:
        """توليد محافظ عملات رقمية"""
        wallets = {}
        
        # Bitcoin (P2PKH format)
        btc_chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        btc_address = '1' + ''.join(random.choices(btc_chars, k=33))
        wallets["bitcoin"] = btc_address
        
        # Monero (محفظة غير قابلة للتتبع)
        xmr_chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        xmr_address = '4' + ''.join(random.choices(xmr_chars, k=94))
        wallets["monero"] = xmr_address
        
        # Ethereum
        eth_address = '0x' + ''.join(random.choices('0123456789abcdef', k=40))
        wallets["ethereum"] = eth_address
        
        return wallets
    
    def _generate_social_accounts(self, name: str) -> Dict[str, str]:
        """توليد حسابات على وسائل التواصل"""
        clean_name = name.lower().replace(" ", "_")
        
        return {
            "github": f"github.com/{clean_name}_{random.randint(1,999)}",
            "twitter": f"twitter.com/@{clean_name}_{random.randint(1,999)}",
            "linkedin": f"linkedin.com/in/{clean_name}_{random.randint(1,999)}",
            "reddit": f"reddit.com/user/{clean_name}_{random.randint(1,999)}",
        }
    
    def _generate_location(self, nationality: str) -> Dict[str, str]:
        """توليد موقع جغرافي"""
        locations = {
            "us": {"city": "New York", "state": "NY", "country": "USA", "timezone": "America/New_York"},
            "uk": {"city": "London", "state": "England", "country": "UK", "timezone": "Europe/London"},
            "sa": {"city": "Riyadh", "state": "Riyadh", "country": "Saudi Arabia", "timezone": "Asia/Riyadh"},
            "ae": {"city": "Dubai", "state": "Dubai", "country": "UAE", "timezone": "Asia/Dubai"},
            "fr": {"city": "Paris", "state": "Île-de-France", "country": "France", "timezone": "Europe/Paris"},
            "de": {"city": "Berlin", "state": "Berlin", "country": "Germany", "timezone": "Europe/Berlin"},
        }
        
        base = locations.get(nationality, locations["us"])
        
        # إضافة إحداثيات وهمية
        base["lat"] = round(random.uniform(-90, 90), 4)
        base["lon"] = round(random.uniform(-180, 180), 4)
        
        return base
    
    def _generate_behavioral_profile(self, personality: str) -> Dict[str, any]:
        """توليد بصمة سلوكية"""
        
        if personality == "random":
            personality = random.choice(["tech", "business", "student", "creative"])
        
        profiles = {
            "tech": {
                "typing_speed_wpm": random.randint(60, 100),
                "mouse_pattern": "fast_direct",
                "working_hours": "9-5",
                "browser": "Chrome",
                "os": "Linux",
                "programming_languages": ["Python", "JavaScript"],
                "github_activity": "daily",
            },
            "business": {
                "typing_speed_wpm": random.randint(40, 70),
                "mouse_pattern": "slow_deliberate",
                "working_hours": "8-6",
                "browser": "Edge",
                "os": "Windows",
                "programming_languages": ["Excel", "PowerPoint"],
                "github_activity": "rarely",
            },
            "student": {
                "typing_speed_wpm": random.randint(50, 90),
                "mouse_pattern": "erratic",
                "working_hours": "10-2, 7-11",
                "browser": "Firefox",
                "os": "MacOS",
                "programming_languages": ["Python", "Java"],
                "github_activity": "weekly",
            },
            "creative": {
                "typing_speed_wpm": random.randint(30, 60),
                "mouse_pattern": "flowing",
                "working_hours": "11-7",
                "browser": "Safari",
                "os": "MacOS",
                "programming_languages": [],
                "github_activity": "rarely",
            },
        }
        
        return profiles.get(personality, profiles["tech"])
    
    def use_identity(self, identity_id: str) -> Optional[DigitalIdentity]:
        """استخدام هوية موجودة"""
        for identity in self.identities:
            if identity.identity_id == identity_id:
                self.current_identity = identity
                logger.info(f"Now using identity: {identity.name}")
                return identity
        return None
    
    def rotate_identity(self) -> DigitalIdentity:
        """تبديل الهوية"""
        new_identity = self.generate()
        self.current_identity = new_identity
        logger.info(f"Rotated to new identity: {new_identity.name}")
        return new_identity
    
    def get_current(self) -> Optional[DigitalIdentity]:
        """الحصول على الهوية الحالية"""
        return self.current_identity
    
    def export_identity(self, identity: DigitalIdentity = None, format: str = "json") -> str:
        """تصدير الهوية"""
        if identity is None:
            identity = self.current_identity
        
        if identity is None:
            return "{}"
        
        if format == "json":
            return json.dumps(identity.to_dict(), indent=2)
        elif format == "csv":
            # تبسيط للعرض
            return f"{identity.identity_id},{identity.name},{identity.email},{identity.phone}"
        
        return str(identity.to_dict())
    
    def get_stats(self) -> dict:
        """إحصائيات الهويات"""
        return {
            "total_identities": len(self.identities),
            "current_identity": self.current_identity.identity_id if self.current_identity else None,
            "identities": [i.identity_id for i in self.identities[-5:]],  # آخر 5
        }


# مثال الاستخدام
if __name__ == "__main__":
    generator = SyntheticIdentity(simulation_mode=True)
    
    # توليد هوية جديدة
    identity = generator.generate(nationality="sa", personality="tech")
    
    print("\n" + "="*60)
    print("Generated Identity:")
    print("="*60)
    print(generator.export_identity(identity, "json"))
    
    # تبديل الهوية
    print("\n" + "="*60)
    print("Rotating identity...")
    print("="*60)
    new_identity = generator.rotate_identity()
    print(f"New identity: {new_identity.name}")
    
    # إحصائيات
    print(f"\nStats: {generator.get_stats()}")