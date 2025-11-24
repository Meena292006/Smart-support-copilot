# backend/smart_copilot.py
import joblib, numpy as np, torch, random
from sentence_transformers import SentenceTransformer, util
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# --- Load models ---
model_path = "model_CUSTOMER.pkl"
vectorizer_path = "vectorizer_CUSTOMER.pkl"

category_model = joblib.load(model_path)
vectorizer = joblib.load(vectorizer_path)

embedder = SentenceTransformer('all-MiniLM-L6-v2')

# --- Expanded & Better FAQ (Critical!) ---
faq_docs = [
    {"category": "Billing", "question": "charged twice", "answer": "Duplicate charges usually clear in 3–7 days. No action needed."},
    {"category": "Billing", "question": "double charge", "answer": "This is a pending authorization. It will drop off automatically."},
    {"category": "Billing", "question": "refund", "answer": "Refunds take 5–10 business days to appear on your statement."},
    {"category": "Account", "question": "delete account", "answer": "Go to Settings → Privacy → Delete Account."},
    {"category": "Account", "question": "can't login", "answer": "Try resetting password or check if your account is locked after too many attempts."},
    {"category": "Technical", "question": "app crash", "answer": "Please force close the app, restart your phone, and reinstall if needed."},
    {"category": "Technical", "question": "not loading", "answer": "Check your internet. Try switching to Wi-Fi or mobile data."},
    {"category": "Technical", "question": "payment failed", "answer": "Try a different card or payment method. Contact your bank if it persists."},
     {"category": "Account", "question": "delete account", "answer": "Go to Settings → Privacy → Delete Account. Confirmation email sent. Let us know if the button is greyed out!"},
    {"category": "Billing", "question": "charged twice duplicate", "answer": "Duplicate charges are bank holds — disappear in 3–7 days. Still there? Reply with order number → instant refund."},
    {"category": "Technical", "question": "app crash login", "answer": "Uninstall → restart phone → reinstall fixes 95% of crashes. Still issue? Tell us phone model + app version."},
    {"category": "Technical", "question": "damaged broken cracked leaking wrong item", "answer": "So sorry! Keep the item — new replacement ships today free + $15 credit. Just confirm your address."},
    {"category": "Technical", "question": "delivered but missing stolen", "answer": "Check neighbors/porch first. Still missing after 48h? Reply “STOLEN” → we reship immediately."},
    {"category": "Billing", "question": "cancelled subscription still charged", "answer": "We’ll refund the last 1–3 payments today. Money back in 3–5 days. Sorry for the trouble!"},
    {"category": "Account", "question": "delete account still billed", "answer": "Even after deletion request, pending charges can go through. Reply with your email — we’ll close everything and refund today."},
    # ← add your other 100+ FAQs here if you want
    {"category": "Account", "question": "How do I delete my account?",
     "answer": "To permanently delete your account, go to Settings → Privacy & Security → Delete Account. You will receive a confirmation email. This action is irreversible after 30 days."},

    {"category": "Account", "question": "I forgot my password",
     "answer": "Click 'Forgot password?' on the login page, enter your email, and we’ll send you a reset link within 2 minutes."},

    {"category": "Billing", "question": "I was charged twice",
     "answer": "Duplicate charges usually happen because of multiple clicks or bank pre-authorization. We automatically refund duplicates within 3–5 business days. Check your transaction history — if still there after 7 days, reply with your order ID."},

    {"category": "Billing", "question": "How to get a refund",
     "answer": "Refunds are processed automatically for returns. Once we receive the item, money is back in your account in 5–10 days depending on your bank."},

    {"category": "Shipping", "question": "Where is my order",
     "answer": "You can track your order here: https://track.mycompany.com with your order number. Most orders arrive in 3–7 business days."},

    {"category": "Product", "question": "Item arrived damaged",
     "answer": "We’re sorry! Please send photos of the damage to damaged@mycompany.com within 48 hours and we’ll ship a free replacement the same day."},

    # Add 50–200 more like this in real life
    {"category": "Account", "question": "How do I change my password?", "answer": "Go to Settings → Account → Change Password. You’ll need to enter your old password and confirm the new one."},
    {"category": "Account", "question": "I forgot my password", "answer": "Click 'Forgot password?' on the login page, enter your email, and we’ll send a reset link instantly."},
    {"category": "Account", "question": "How do I delete my account permanently?", "answer": "Settings → Privacy → Delete Account at the bottom. We’ll send a confirmation email — action is final after 30 days."},
    {"category": "Account", "question": "Can I change my username?", "answer": "Yes, once every 30 days. Go to Settings → Profile → Edit username."},
    {"category": "Account", "question": "How do I update my email address?", "answer": "Settings → Account → Email address → enter new email → verify with the link we send."},
    {"category": "Account", "question": "My account is locked", "answer": "After 5 failed login attempts it locks for 15 minutes. Wait or click 'Unlock account' on login page."},
    {"category": "Account", "question": "How to enable two-factor authentication (2FA)", "answer": "Settings → Security → Two-factor authentication → choose SMS or Authenticator app."},
    {"category": "Account", "question": "I lost access to my 2FA phone", "answer": "Use one of your backup codes or contact support with your registered email and order ID."},
    {"category": "Account", "question": "Can I merge two accounts?", "answer": "Yes, reply to this message with both emails and we’ll merge everything (orders, credits, history) in 24h."},
    {"category": "Account", "question": "How do I change my phone number?", "answer": "Settings → Account → Phone number → enter new number → verify with SMS code."},
    {"category": "Account", "question": "Why can’t I log in even with correct password?", "answer": "Try clearing browser cache/cookies or use incognito mode. Also check if Caps Lock is on."},
    {"category": "Account", "question": "How do I download all my data?", "answer": "Settings → Privacy → Download your data. We’ll email you a zip file within 24 hours."},
    {"category": "Account", "question": "Someone else is using my account", "answer": "Immediately change password and enable 2FA. Then contact us so we can log out all devices."},
    {"category": "Account", "question": "How do I close my account temporarily?", "answer": "We don’t offer temporary deactivation — you can just log out or delete permanently."},
    {"category": "Account", "question": "I never received the verification email", "answer": "Check spam/junk folder. Still missing? Click 'Resend verification' on the signup confirmation page."},

    # ==================== BILLING (34-66) ====================
    {"category": "Billing", "question": "I was charged twice for the same order", "answer": "This is usually a bank pre-authorization. The duplicate will drop off in 3–7 days. No action needed."},
    {"category": "Billing", "question": "Why do I see a $1 charge?", "answer": "It’s a temporary card verification hold — never actually charged and disappears in a few days."},
    {"category": "Billing", "question": "How do I get a refund?", "answer": "Refunds are automatic once we receive returned items. Money back to original payment method in 3–10 days."},
    {"category": "Billing", "question": "When will my refund appear?", "answer": "Usually 3–5 business days after we process the return. Credit cards are fast, bank transfers can take up to 10 days."},
    {"category": "Billing", "question": "How to update my credit card?", "answer": "Go to Wallet → Payment methods → Add or edit card."},
    {"category": "Billing", "question": "My payment was declined", "answer": "Check card details, expiry date, and available balance. Some banks block online purchases — call your bank."},
    {"category": "Billing", "question": "Can I get an invoice?", "answer": "Yes! Every order automatically emails a PDF invoice. You can also download from Orders → View invoice."},
    {"category": "Billing", "question": "How do I use a promo code?", "answer": "Enter the code at checkout in the 'Discount code' box and click Apply."},
    {"category": "Billing", "question": "My promo code is not working", "answer": "Check: minimum spend, expiry date, first-time user only, and whether it applies to sale items."},
    {"category": "Billing", "question": "What payment methods do you accept?", "answer": "Visa, Mastercard, PayPal, Apple Pay, Google Pay, and Klarna (pay later)."},
    {"category": "Billing", "question": "Can I pay with multiple cards?", "answer": "No, only one payment method per order."},
    {"category": "Billing", "question": "I see a charge from a different company name", "answer": "Our payment processor sometimes shows as 'PAYPRO' or 'STRIPE' — totally normal."},
    {"category": "Billing", "question": "How do I cancel a subscription?", "answer": "My Account → Subscriptions → Cancel. No charges after next billing date."},
    {"category": "Billing", "question": "Will I get charged sales tax/VAT?", "answer": "Yes, automatically calculated and added at checkout based on your shipping address."},
    {"category": "Billing", "question": "I was charged after cancelling", "answer": "Cancellation only stops future charges. If you were charged today, the cancellation came after the billing run — we’ll refund immediately."},

    # ==================== TECHNICAL (67-100) ====================
    {"category": "Technical", "question": "The website is not loading", "answer": "Try a different browser or incognito mode. Also check downdetector.com — if others have issues, we’re already fixing it."},
    {"category": "Technical", "question": "Images are not showing", "answer": "Clear browser cache (Ctrl+Shift+R) or disable ad-blocker temporarily."},
    {"category": "Technical", "question": "App keeps crashing", "answer": "Please update to the latest version in App Store / Google Play. If already updated, uninstall & reinstall."},
    {"category": "Technical", "question": "I can’t log in on the mobile app", "answer": "Force close the app, clear app cache (Settings → Apps → Our App → Storage → Clear cache), then try again."},
    {"category": "Technical", "question": "Buttons are not working", "answer": "Try on another device or browser. Common on old versions of Internet Explorer or Safari."},
    {"category": "Technical", "question": "Page says 404 error", "answer": "The link might be broken. Try going to homepage and navigating again."},
    {"category": "Technical", "question": "My order history is empty", "answer": "Log out and log back in. Sometimes the cache needs refreshing."},
    {"category": "Technical", "question": "I’m stuck on a white screen", "answer": "Hard refresh (Ctrl+F5 or Cmd+Shift+R) or try incognito/private mode."},
    {"category": "Technical", "question": "Checkout button is greyed out", "answer": "You probably have an invalid character in address or phone field. Remove emojis/symbols."},
    {"category": "Technical", "question": "Videos won’t play", "answer": "Update your browser and disable ad-blocker. We use HTML5 video."},
    {"category": "Technical", "question": "I get 'Session expired' every 5 minutes", "answer": "This happens on some corporate/school networks. Try mobile data or VPN."},
    {"category": "Technical", "question": "The search bar does nothing", "answer": "Clear your cookies or try typing slower — some keyboards send too many requests."},
    {"category": "Technical", "question": "My cart is empty after adding items", "answer": "Disable ad-blocker and tracker blockers — they sometimes delete cart cookies."},
    {"category": "Technical", "question": "I can’t upload photos", "answer": "File size limit is 10MB. Supported formats: JPG, PNG, GIF."},
    {"category": "Technical", "question": "Why is the site so slow?", "answer": "High traffic times (sales, launches). Try again in 10–15 minutes or use the mobile app."},
    {"category": "Technical", "question": "I’m getting too many emails", "answer": "Settings almo→ Email preferences → uncheck the types you don’t want."},
    {"category": "Technical", "question": "Push notifications won’t stop", "answer": "Phone Settings → Notifications → Our App → turn off or manage in-app settings."},
    {"category": "Technical", "question": "My item arrived damaged or broken",
     "answer": "We’re really sorry! Please reply with 2–3 photos of the damage and your order number — we’ll ship a free replacement the same day (no return needed)."},

    {"category": "Technical", "question": "Product came broken what do I do",
     "answer": "Keep the item or recycle it — we’ll send a brand new replacement immediately at no cost. Just send photos to damaged@yourcompany.com or reply here."},

    {"category": "Technical", "question": "Package arrived damaged",
     "answer": "Take a photo of the box + the item. We’ll file a claim with the carrier and ship your replacement today."},

    {"category": "Technical", "question": "I received a cracked item",
     "answer": "No need to return it. Send us photos and we’ll dispatch a new one within 24 hours + add $10 apology credit."},

    {"category": "Technical", "question": "Wrong item received",
     "answer": "Our mistake! Keep or donate the wrong item — we’ll send the correct one free of charge right away."},

    {"category": "Technical", "question": "Item is defective",
     "answer": "Reply with a short video/photo of the defect and we’ll replace it instantly, no questions asked."},

    {"category": "Technical", "question": "Missing parts from my order",
     "answer": "We’ll ship the missing pieces today with express shipping. Just let us know which parts are missing."},

    {"category": "Technical", "question": "Product doesn’t work out of the box",
     "answer": "100% our fault. We’ll send a tested replacement immediately. Reply with your order number."},
    {"category": "Account", "question": "delete account", "answer": "Go to Settings → Privacy → Delete Account. We’ll email confirmation. Sad to see you go!"},
    {"category": "Billing outrage", "question": "charged twice", "answer": "Duplicate charges are bank holds — disappear in 3–7 days. Still there after a week? Reply with order number → instant refund."},
    {"category": "Technical", "question": "app crashing", "answer": "Uninstall → restart phone → reinstall fixes 95% of crashes. Still bad? Tell us phone + app version."},
    {"category": "Technical", "question": "damaged broken cracked wrong item", "answer": "So sorry! Keep/discard it — new replacement ships today free + $15 apology credit. Confirm address?"},
    {"category": "Technical", "question": "package delivered but missing", "answer": "Check neighbors/porch first. Still gone after 48h? Reply “STOLEN” → we reship immediately."},
    {"category": "Billing", "question": "cancelled but still charged", "answer": "We’ll refund the last 1–3 payments today automatically. Money back in 3–5 days."},
    {"category": "Billing", "question": "payment went through but premium not unlocked",
     "answer": "It can take up to 10 minutes for premium to activate after payment. Try force-closing the app and logging in again. Still locked? Reply ‘PREMIUM’ and we’ll activate it manually in 2 minutes."},

    {"category": "Account", "question": "password reset link expired",
     "answer": "Just click ‘Forgot password?’ again — we send a new link instantly. Or reply here and we’ll reset it for you right now."},

    {"category": "Technical", "question": "app crashes when uploading photo",
     "answer": "Try this: update the app → restart phone → use a smaller photo (<10MB). Fixes 98% of upload crashes. Still crashing? Tell us your phone model."},

    {"category": "Billing", "question": "charged after cancelling plan",
     "answer": "Cancellation stops future charges only. We’ll refund the last payment automatically today — you’ll see it in 3–5 days. Sorry!"},

    {"category": "Account", "question": "can’t log in after update",
     "answer": "Force close the app → clear cache (Settings → Apps → Our App → Storage → Clear cache) → reopen. Works every time after updates."},

    {"category": "Technical", "question": "website won’t load but internet fine",
     "answer": "Try incognito mode or a different browser. If still down, we might be doing quick maintenance — back in 5 minutes. Or use the mobile app!"},

    {"category": "Account", "question": "account will be deactivated message",
     "answer": "That’s just a reminder about an unpaid invoice. Pay it or ignore if already paid — your account stays active. Need help? Reply ‘INVOICE’."}
]

faq_texts = [d["answer"] for d in faq_docs]
faq_embeddings = embedder.encode(faq_texts, convert_to_tensor=True)

sent_analyzer = SentimentIntensityAnalyzer()

def predict_categories(text, threshold=0.25):  # Lowered from 0.3
    X = vectorizer.transform([text])
    probs = category_model.predict_proba(X)[0]
    selected = [cls for cls, p in zip(category_model.classes_, probs) if p >= threshold]
    if not selected:
        selected = [category_model.classes_[np.argmax(probs)]]
    return selected

def detect_sentiment(text):
    score = sent_analyzer.polarity_scores(text)["compound"]
    if score < -0.05:
        return "negative"
    elif score > 0.3:
        return "positive"
    return "neutral"

def detect_priority(text):
    urgent_words = ["urgent", "refund", "immediately", "broken", "charged twice", "double charge", "now"]
    return "urgent" if any(w in text.lower() for w in urgent_words) else "normal"

def retrieve_best_answer(msg):
    q = embedder.encode(msg, convert_to_tensor=True)
    scores = util.cos_sim(q, faq_embeddings)[0]
    best_idx = int(scores.argmax())
    return {
        "score": float(scores[best_idx]),
        "answer": faq_docs[best_idx]["answer"]
    }

def smart_support_copilot(message):
    cats = predict_categories(message)
    sentiment = detect_sentiment(message)
    priority = detect_priority(message)
    rag = retrieve_best_answer(message)
    score = rag["score"]

    # MAIN FIX: Lower thresholds so FAQs actually trigger!
    if score > 0.58:  # Was 0.75 → too high!
        reply = rag["answer"]
        auto = True
    elif sentiment == "negative" and score > 0.45:  # Was 0.55
        reply = "We’re sorry for the trouble. " + rag["answer"]
        auto = True
    else:
        reply = "Forwarding this to a human agent."
        auto = False

    return {
        "predicted_categories": cats,
        "sentiment": sentiment,
        "priority": priority,
        "rag_score": round(score, 3),
        "auto_reply": reply,
        "can_auto_reply": auto
    }