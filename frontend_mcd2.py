from flask import Flask, render_template_string

app = Flask(__name__)

# HTML + CSS + JS dimasukkan ke variabel string
html_page = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>McD Sentiment Fun - Mobile</title>

    <link href="https://fonts.googleapis.com/css2?family=Fredoka+One&display=swap" rel="stylesheet">

    <style>
    body {
        font-family: 'Fredoka One', sans-serif;
        padding: 15px;
        background: linear-gradient(to bottom, #fff3cd, #ffe0b2);
        text-align: center;
    }
    h1 { color: #d32f2f; font-size: 2em; }
    p { font-size: 0.95em; }

    .input-area {
        width: 90%;
        display: flex;
        flex-direction: column;
        gap: 12px;
        margin-top: 10px;
    }
    input[type=text] {
        width: 100%;
        padding: 12px;
        border-radius: 15px;
        border: 2px solid #fbc02d;
        font-size: 1em;
        outline: none;
    }
    input[type=text]:focus { border-color: #d32f2f; }
    button {
        padding: 12px;
        width: 100%;
        background-color: #fbc02d;
        color: #d32f2f;
        border: none;
        border-radius: 15px;
        font-size: 1.1em;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    button:hover {
        background-color: #d32f2f;
        color: white;
        transform: scale(1.05);
    }
    #results { margin-top: 25px; }
    .model-result {
        margin-top: 15px;
        padding: 15px;
        border-radius: 15px;
        background: #ffffffc0;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        text-align: left;
    }
    .model-result h3 { margin: 0 0 5px; color: #d32f2f; }
    .emoji { font-size: 1.8em; }
    .wordcloud-img {
        width: 100%;
        max-width: 350px;
        border-radius: 15px;
        margin-top: 10px;
    }
    @media (min-width: 600px) {
        h1 { font-size: 2.5em; }
        button { width: auto; padding: 12px 25px; }
        .input-area { flex-direction: row; justify-content: center; }
        input[type=text] { width: 70%; }
    }
    </style>
</head>
<body>

    <h1>🍔 McD Sentiment Fun 📱</h1>
    <p>Enter your McD review below:</p>

    <div class="input-area">
        <input type="text" id="reviewText" placeholder="Example: The chicken is delicious!">
        <button onclick="submitReview()">Analyze!</button>
    </div>

    <div id="results"></div>

    <script>
        // Make it dynamic: follow the host where frontend is accessed (laptop / phone)
        const API_PORT = 5000;  // backend port churn_api.py
        const API_BASE = `${window.location.protocol}//${window.location.hostname}:${API_PORT}`;

        async function submitReview() {
            const text = document.getElementById("reviewText").value.trim();
            if (!text) {
                alert("Please enter review text first bestie 😭");
                return;
            }

            const resultsDiv = document.getElementById("results");
            resultsDiv.innerHTML = "<p>Loading, please wait...</p>";

            try {
                const response = await fetch(`${API_BASE}/predict`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ text })
                });

                const data = await response.json();

                let html = "";

                data.results.forEach(res => {
                    res.per_model.forEach(m => {
                        let emoji = m.pred_label === "pos" ? "😊🍔"
                                  : (m.pred_label === "neg" ? "😢🍟" : "😐");

                        html += `
                        <div class="model-result">
                            <h3>${m.model} <span class="emoji">${emoji}</span></h3>
                            <p><strong>Prediction:</strong> ${m.pred_label}</p>
                            ${m.probs ? `<p>Probability: neg=${m.probs.neg.toFixed(2)}, pos=${m.probs.pos.toFixed(2)}</p>` : ""}
                        </div>`;
                    });

                    if (res.wordcloud) {
                        html += `
                        <div class="model-result" style="text-align:center;">
                            <h3>Word Cloud</h3>
                            <img src="data:image/png;base64,${res.wordcloud}" class="wordcloud-img">
                        </div>`;
                    }
                });

                resultsDiv.innerHTML = html;

            } catch (err) {
                resultsDiv.innerHTML = `<p style="color:red;">Failed to connect to API: ${err}</p>`;
            }
        }
    </script>

</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(html_page)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
