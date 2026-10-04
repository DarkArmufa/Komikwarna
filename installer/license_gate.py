"""Local license check shared by web and terminal installers."""
import hashlib
import hmac
import getpass

LICENSE_DIGEST = "d7d36fca8bc74d67cd86e9104f3805fdf563a4e219236014865fa0f94d74832f"
LICENSE_MODES = {'both', 'panel', 'wings', 'update', 'repair'}

def require_license(value):
    if not isinstance(value, str) or not hmac.compare_digest(hashlib.sha256(value.strip().encode()).hexdigest(), LICENSE_DIGEST):
        raise ValueError('License key kosong atau salah. Proses dibatalkan.')
    return value.strip()

def prompt_license():
    try:
        return require_license(getpass.getpass('Masukkan license key: '))
    except (EOFError, KeyboardInterrupt):
        raise ValueError('License key wajib dimasukkan. Proses dibatalkan.') from None
