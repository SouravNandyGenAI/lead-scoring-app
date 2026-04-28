from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)


class LeadScorer:
    def score_lead(self, lead):
        score = 0

        company_size = int(lead.get("company_size", 0))
        if company_size >= 500:
            score += 25
        elif company_size >= 100:
            score += 15
        elif company_size >= 20:
            score += 8

        title = str(lead.get("job_title", "")).lower()
        if any(role in title for role in ["ceo", "founder", "cto", "vp", "director"]):
            score += 20
        elif any(role in title for role in ["manager", "lead", "head"]):
            score += 10

        industry = str(lead.get("industry", "")).lower()
        if industry in ["saas", "technology", "finance", "healthcare"]:
            score += 15

        website_visits = int(lead.get("website_visits", 0))
        email_opens = int(lead.get("email_opens", 0))

        score += min(website_visits * 2, 20)
        score += min(email_opens * 3, 15)

        if bool(lead.get("demo_requested", False)):
            score += 30

        budget = int(lead.get("budget", 0))
        if budget >= 50000:
            score += 20
        elif budget >= 10000:
            score += 10
        elif budget >= 5000:
            score += 5

        return score

    def classify_lead(self, score):
        if score >= 80:
            return "Hot"
        elif score >= 50:
            return "Warm"
        return "Cold"


def is_authorized(req):
    expected_api_key = os.environ.get("API_KEY")

    # If no API_KEY is set, skip auth
    if not expected_api_key:
        return True

    auth_header = req.headers.get("Authorization", "")
    expected_header = f"Bearer {expected_api_key}"
    return auth_header == expected_header


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        lead = {
            "name": request.form["name"],
            "email": request.form["email"],
            "company_size": int(request.form["company_size"]),
            "job_title": request.form["job_title"],
            "industry": request.form["industry"],
            "website_visits": int(request.form["website_visits"]),
            "email_opens": int(request.form["email_opens"]),
            "demo_requested": request.form.get("demo_requested") == "yes",
            "budget": int(request.form["budget"]),
        }

        scorer = LeadScorer()
        score = scorer.score_lead(lead)
        category = scorer.classify_lead(score)

        return render_template("result.html", lead=lead, score=score, category=category)

    return render_template("index.html")


@app.post("/api/score-lead")
def score_lead_api():
    if not is_authorized(request):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    required_fields = [
        "email",
        "job_title",
        "industry",
        "company_size",
        "website_visits",
        "email_opens",
        "demo_requested",
        "budget",
    ]

    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({
            "error": "Missing required fields",
            "missing_fields": missing_fields
        }), 400

    try:
        lead = {
            "first_name": data.get("first_name", ""),
            "last_name": data.get("last_name", ""),
            "company": data.get("company", ""),
            "email": data["email"],
            "job_title": data["job_title"],
            "industry": data["industry"],
            "company_size": int(data["company_size"]),
            "website_visits": int(data["website_visits"]),
            "email_opens": int(data["email_opens"]),
            "demo_requested": bool(data["demo_requested"]),
            "budget": int(data["budget"]),
        }

        scorer = LeadScorer()
        score = scorer.score_lead(lead)
        category = scorer.classify_lead(score)

        return jsonify({
            "success": True,
            "score": score,
            "category": category,
            "lead": {
                "first_name": lead["first_name"],
                "last_name": lead["last_name"],
                "company": lead["company"],
                "email": lead["email"],
            }
        }), 200

    except ValueError:
        return jsonify({
            "error": "Invalid numeric field value"
        }), 400
    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500


@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)