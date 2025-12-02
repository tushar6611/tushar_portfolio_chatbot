import os

def generate_resume_download_link():
    """
    Generates a OneDrive direct download link.
    Store RESID + AUTHKEY in environment variables.
    """
    resid = os.getenv("ONEDRIVE_RESID")
    authkey = os.getenv("ONEDRIVE_AUTHKEY")

    if not resid:
        return "OneDrive resid not configured!"
    if not authkey:
        return "OneDrive authkey not configured!"

    return f"https://1drv.ms/b/c/5bc38c510559f1a0/IQCg8VkFUYzDIIBbTwgAAAAAAUr9zp9_AmA6ExTZPf6Fq0I?e=pnhFwI"
