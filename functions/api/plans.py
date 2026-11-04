from fastapi import HTTPException


PLANS = {
    "free": {
        "label": "Free",
        "qr_limit": 5,
        "templates": {"basic", "basic-soft", "basic-contrast"},
        "allow_custom_colors": False,
        "allow_logo": False,
    },
    "prime": {
        "label": "Prime",
        "qr_limit": 50,
        "templates": {"basic", "basic-soft", "basic-contrast", "prime-rounded", "prime-dots", "prime-frame"},
        "allow_custom_colors": True,
        "allow_logo": False,
    },
    "business": {
        "label": "Business",
        "qr_limit": 250,
        "templates": {
            "basic", "basic-soft", "basic-contrast",
            "prime-rounded", "prime-dots", "prime-frame",
            "business-gradient", "business-frame",
        },
        "allow_custom_colors": True,
        "allow_logo": True,
    },
    "enterprise": {
        "label": "Custom Enterprise",
        "qr_limit": 10000,
        "templates": {"basic", "basic-soft", "basic-contrast", "prime-rounded", "prime-dots", "prime-frame", "business-gradient", "business-frame"},
        "allow_custom_colors": True,
        "allow_logo": True,
    },
}


def plan_for(business: dict) -> tuple[str, dict]:
    name = str(business.get("PLAN") or "free").strip().lower()
    return (name if name in PLANS else "free"), PLANS.get(name, PLANS["free"])


def require_template(business: dict, template: str) -> tuple[str, dict]:
    plan_name, plan = plan_for(business)
    if template not in plan["templates"]:
        raise HTTPException(403, f"This QR design is available on the {plan['label']} plan or higher")
    return plan_name, plan
