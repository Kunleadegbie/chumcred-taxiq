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
        .select("*")\
        .eq("user_id", user_id)\
        .eq("status", "approved")\
        .execute()

    if res.data:
        return res.data[0]["plan"] == "premium"
    return False