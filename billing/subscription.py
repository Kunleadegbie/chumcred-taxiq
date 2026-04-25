from core.database import get_supabase

supabase = get_supabase()

def has_active_subscription(user_id):
    res = supabase.table("subscriptions")\
        .select("*")\
        .eq("user_id", user_id)\
        .eq("status", "active")\
        .execute()

    return len(res.data) > 0

def is_premium(user_id):

    res = supabase.table("subscriptions")\
        .select("plan, status, created_at")\
        .eq("user_id", user_id)\
        .eq("status", "active")\
        .order("created_at", desc=True)\
        .limit(1)\
        .execute()

    if res.data:
        sub = res.data[0]
        return sub.get("plan") == "premium"

    return False