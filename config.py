import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()  # Cargar variables desde .env

@dataclass
class Settings:
    RACKSPACE_URL: str
    RACKSPACE_USERNAME: str
    RACKSPACE_PASSWORD: str
    CHROME_HEADLESS: bool
    WAIT_SHORT: int
    WAIT_LONG: int
    OUTPUT_XLSX: str

    @classmethod
    def load(cls) -> "Settings":
        url = os.getenv("RACKSPACE_URL", "").strip()
        user = os.getenv("RACKSPACE_USERNAME", "").strip()
        pwd = os.getenv("RACKSPACE_PASSWORD", "").strip()
        if not url:
            raise ValueError("RACKSPACE_URL no está configurado.")
        if not user:
            raise ValueError("RACKSPACE_USERNAME no está configurado.")
        if not pwd:
            raise ValueError("RACKSPACE_PASSWORD no está configurado.")
        headless = os.getenv("CHROME_HEADLESS", "false").lower() in ("1", "true", "yes")
        wait_short = int(os.getenv("WAIT_SHORT", "10"))
        wait_long = int(os.getenv("WAIT_LONG", "40"))
        out_xlsx = os.getenv("OUTPUT_XLSX", "emails.xlsx")
        return cls(
            RACKSPACE_URL=url,
            RACKSPACE_USERNAME=user,
            RACKSPACE_PASSWORD=pwd,
            CHROME_HEADLESS=headless,
            WAIT_SHORT=wait_short,
            WAIT_LONG=wait_long,
            OUTPUT_XLSX=out_xlsx,
        )

    def safe_print(self) -> None:
        def mask(val, start=2, end=2):
            if not val:
                return ""
            if len(val) <= start + end:
                return "*" * len(val)
            return val[:start] + "*" * (len(val) - start - end) + val[-end:]
        print("⚙️  Config:")
        print(f"   • RACKSPACE_URL: {self.RACKSPACE_URL}")
        print(f"   • RACKSPACE_USERNAME: {mask(self.RACKSPACE_USERNAME, 3, 3)}")
        # No mostramos password
        print(f"   • CHROME_HEADLESS: {self.CHROME_HEADLESS}")
        print(f"   • WAIT_SHORT: {self.WAIT_SHORT}s  • WAIT_LONG: {self.WAIT_LONG}s")
        print(f"   • OUTPUT_XLSX: {self.OUTPUT_XLSX}")
