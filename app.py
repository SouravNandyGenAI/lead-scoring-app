from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)


class LeadScorer:
    def score_lead(self, lead):
        score = 0

        company_size = lead["company_size"]
        if company_size >= 500:
            score += 25
        elif company_size >= 100:
            score += 15
        elif company_size >= 20:
            score += 8

        title = lead["job_title"].lower()
        if any(role in title for role in ["ceo", "founder", "cto", "vp", "director"]):
            score += 20
        elif any(role in title for role in ["manager", "lead", "head"]):
            score += 10

        if lead["industry"].lower() in ["saas", "technology", "finance", "healthcare"]:
            score += 15

        score += min(lead["website_visits"] * 2, 20)
        score += min(lead["email_opens"] * 3, 15)

        if lead["demo_requested"]:
            score += 30

        budget = lead["budget"]
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


@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
