from core.database import get_supabase

supabase = get_supabase()

def has_active_subscription(user_id):
    res = supabase.table("subscriptions")\
        .select("*")\
        .eq("user_id", user_id)\
        .eq("status", "active")\
        .execute()

    return len(res.data) > 0